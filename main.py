import os
from typing import List

from glueops.setup_logging import configure as go_configure_logging
from glueops.vault_client import VaultClient

from src.check_dns import check_dns
from src.create_app_configs.create_app_configs import render_app_configs
from src.get_configs_from_ecs import get_configs_from_ecs
from src.get_listener_rules import get_target_group_mapping
from src.stage_app_data import stage_app_data_from_csv
from src.style import Colors, pprint_dict


# configure logger
logger = go_configure_logging(
    name='GO_MIGRATE_APP',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)

# configure vault clients for clusters
nonprod_vault_client = VaultClient(
    vault_url=os.environ['NONPROD_VAULT_URL'],
    kubernetes_role=os.environ['KUBERNETES_ROLE'],
    vault_token=os.environ['NONPROD_VAULT_TOKEN'],
    pomerium_cookie=os.environ['NONPROD_POMERIUM_COOKIE']
)
prod_vault_client = VaultClient(
    vault_url=os.environ['PROD_VAULT_URL'],
    kubernetes_role=os.environ['KUBERNETES_ROLE'],
    vault_token=os.environ['PROD_VAULT_TOKEN'],
    pomerium_cookie=os.environ['PROD_POMERIUM_COOKIE']
)

# get listener rules
# stage_listener_rules = os.environ['NONPROD_LISTENER_ARNS'].split(',')
# from pprint import pprint
# pprint(
#     get_target_group_mapping(stage_listener_rules)
# )

# load input csv
csv_app_data = stage_app_data_from_csv('/app/inputs/glueops_wip.csv')


def check_prod_dns(domains: List[str]):
    from requests.exceptions import JSONDecodeError
    for d in csv_app_data:
        for r in domains:
            try:
                resp_json = check_dns(r).json()
                try:
                    print({
                        r : resp_json['Authority'][0]['data']
                    })
                except KeyError:
                    print({
                        r : resp_json['Answer'][0]['data']
                    })
            except JSONDecodeError:
                print(f'invalid query: {r}')

def configure_apps_for_migration():
    # user configuration and prompts

    total_configurations = len(csv_app_data)
    print(f'\n\n{Colors.YELLOW}Staging{Colors.ENDC} {Colors.RED}{total_configurations}{Colors.ENDC} {Colors.YELLOW}application configurations:{Colors.ENDC}')
    pprint_dict({
        r['app_repo']: [r['prod_ecs_service'], r['stage_ecs_service']]
        for r in csv_app_data
    })

    while True:
        confirm_remove_secrets = input(
            f'\n{Colors.YELLOW}remove secrets for testing?{Colors.ENDC} ({Colors.GREEN}yes{Colors.ENDC}/{Colors.RED}no{Colors.ENDC}): '
        ).strip().lower()
        if confirm_remove_secrets == 'yes':
            print(f'\n{Colors.YELLOW} secrets will be removed for this run{Colors.ENDC}')
            break
        elif confirm_remove_secrets == 'no':
            print(f'\n{Colors.YELLOW} secrets will{Colors.ENDC} {Colors.RED}NOT{Colors.ENDC} {Colors.YELLOW}be removed for this run{Colors.ENDC}')
            break
        else:
            print(
                f'\n{Colors.YELLOW}please enter "{Colors.GREEN}yes{Colors.ENDC}{Colors.YELLOW}" or "{Colors.ENDC}{Colors.GREEN}no{Colors.ENDC} {Colors.YELLOW}to determine secrets handline{Colors.ENDC}"'
            )

    while True:
        confirm_each_config = input(
            f'\n{Colors.YELLOW}do you want to confirm each app config?{Colors.ENDC} ({Colors.GREEN}yes{Colors.ENDC}/{Colors.RED}no{Colors.ENDC}): '
        ).strip().lower()
        if confirm_each_config == 'yes':
            print(f'\n{Colors.YELLOW} each app config will request confirmation{Colors.ENDC}')
            break
        elif confirm_each_config == 'no':
            print(f'\n{Colors.YELLOW} you will{Colors.ENDC} {Colors.RED}NOT{Colors.ENDC} {Colors.YELLOW}be prompted to confirm each app config{Colors.ENDC}')
            confirm = 'yolo'
            break
        else:
            print(
                f'\n{Colors.YELLOW}please enter "{Colors.GREEN}yes{Colors.ENDC}{Colors.YELLOW}" or "{Colors.ENDC}{Colors.GREEN}no{Colors.ENDC} {Colors.YELLOW}to determine secrets handline{Colors.ENDC}"'
            )

    # config generation and secrets writing
    i = 0
    for d in csv_app_data:
        i += 1
        print(f'{Colors.YELLOW}Application Configuration:{Colors.ENDC}')
        ecs_stage_conf = get_configs_from_ecs(
            cluster_arn=os.environ['STAGE_CLUSTER_ARN'],
            service_arn=d['stage_ecs_service']
        )
        ecs_prod_conf = get_configs_from_ecs(
            cluster_arn=os.environ['PROD_CLUSTER_ARN'],
            service_arn=d['prod_ecs_service']
        )

        # remove secrets for testing
        if confirm_remove_secrets == 'yes':
            import random
            import string

            def get_random_string():
                rnd_str = string.ascii_letters
                return ''.join(random.choice(rnd_str) for i in range(10))

            for k in ecs_stage_conf['vault_secrets']:
                ecs_stage_conf['vault_secrets'][k] = f'stage-{get_random_string()}'
            for k in ecs_prod_conf['vault_secrets']:
                ecs_prod_conf['vault_secrets'][k] = f'prod-{get_random_string()}'
        elif confirm_remove_secrets == 'no':
            pass


        app_config = {
            "app_repo": d['app_repo'],
            "ecr_repository": ecs_prod_conf['ecr_repository'],
            "env_configs": [
                {
                    "env": "stage",
                    "image_tag": ecs_stage_conf['image_tag'],
                    "hostnames": d['stage_hostnames'],
                    "volume_mount_claim_name": d['stage_volume_mount_claim_name'],
                    "volume_mount_path": ecs_stage_conf['volume_mount_path'],
                    "volume_mount_sub_path": ecs_stage_conf['volume_mount_sub_path'],
                    "web_acl_name": None,
                    "vault_secrets": ecs_stage_conf['vault_secrets'],
                    "vault_secrets_path": f'secret/{d["app_repo"].split("/")[-1]}/stage'
                },
                {
                    "env": "prod",
                    "image_tag": ecs_prod_conf['image_tag'],
                    "hostnames": d['prod_hostnames'],
                    "volume_mount_claim_name": d['prod_volume_mount_claim_name'],
                    "volume_mount_path": ecs_prod_conf['volume_mount_path'],
                    "volume_mount_sub_path": ecs_prod_conf['volume_mount_sub_path'],
                    "web_acl_name": "primary",
                    "vault_secrets": ecs_prod_conf['vault_secrets'],
                    "vault_secrets_path": f'secret/{d["app_repo"].split("/")[-1]}/prod'
                }
            ]
        }

        pprint_dict(app_config)
        print(f'\n{Colors.YELLOW}Configurations staged for: {Colors.GREEN}{d["app_repo"]}{Colors.ENDC}{Colors.BLUE}{Colors.ENDC}\n')

        if confirm_each_config == 'no':
            confirm = 'yolo'
        elif confirm_each_config == 'yes':
            confirm = input(f'\n{Colors.YELLOW}render templates and write secrets to vault{Colors.ENDC} ({Colors.GREEN}yolo{Colors.ENDC}/{Colors.RED}no{Colors.ENDC}): ').strip().lower()
        if confirm == 'yolo':
            print(f'\n{Colors.YELLOW}rendering templates and writing secrets{Colors.ENDC}')
            render_app_configs(app_config)

            ##=== write secrets
            for app_env in app_config['env_configs']:
                if app_env['vault_secrets'] == {}:
                    print(f'{Colors.YELLOW}no secrets to write for app: {Colors.GREEN}{app_config["app_repo"]}{Colors.ENDC} {Colors.YELLOW}in env:{Colors.ENDC} {Colors.GREEN}{app_env["env"]}{Colors.ENDC}')
                    continue
                elif app_env['env'] == 'stage':
                    write_response = nonprod_vault_client.write_data_to_vault(
                        secret_path=app_env['vault_secrets_path'],
                        data=app_env['vault_secrets']
                    )
                elif app_env['env'] == 'prod':
                    write_response = prod_vault_client.write_data_to_vault(
                        secret_path=app_env['vault_secrets_path'],
                        data=app_env['vault_secrets']
                    )
                else:
                    print(f'{Colors.RED}WARNING:{Colors.ENDC} {Colors.YELLOW}unrecognized environment:{Colors.ENDC} {Colors.GREEN}{app_env["env"]}{Colors.ENDC}')
                pprint_dict(write_response)
        else:
            print(f'\n{Colors.YELLOW}skipping configuration of:{Colors.ENDC} {Colors.GREEN}{d["app_repo"]}{Colors.ENDC}\n\n\n')
        if i < total_configurations:
            print(f'\n{Colors.MAGENTA}next configuration:{Colors.ENDC}\n\n')

configure_apps_for_migration()

# for d in csv_app_data:
#     check_prod_dns(d['prod_hostnames'])
