import os

from glueops.setup_logging import configure as go_configure_logging
from glueops.vault_client import VaultClient
from pprint import pprint

from src.create_app_configs.create_app_configs import render_app_configs
from src.get_configs_from_ecs import get_configs_from_ecs
from src.stage_app_data import stage_app_data_from_csv

# configure logger
logger = go_configure_logging(
    name='GO_MIGRATE_APP',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)

# configure vault clients for each cluster
nonprod_vault_client = VaultClient(
    vault_url=os.environ['VAULT_URL'],
    kubernetes_role=os.environ['KUBERNETES_ROLE'],
    vault_token=os.environ['VAULT_TOKEN'],
    pomerium_cookie=os.environ['POMERIUM_COOKIE']
)
prod_vault_client = VaultClient(
    vault_url=os.environ['VAULT_URL'],
    kubernetes_role=os.environ['KUBERNETES_ROLE'],
    vault_token=os.environ['VAULT_TOKEN'],
    pomerium_cookie=os.environ['POMERIUM_COOKIE']
)


csv_app_data = stage_app_data_from_csv('/app/inputs/glueops_wip.csv')

for d in csv_app_data:
    ecs_stage_conf = get_configs_from_ecs(
        cluster_arn=os.environ['STAGE_CLUSTER_ARN'],
        service_arn=d['stage_ecs_service']
    )
    ecs_prod_conf = get_configs_from_ecs(
        cluster_arn=os.environ['PROD_CLUSTER_ARN'],
        service_arn=d['prod_ecs_service']
    )


    #==== remove secrets for testing
    import random
    import string


    def get_random_string():
        rnd_str = string.ascii_letters
        return ''.join(random.choice(rnd_str) for i in range(10))

    for k in ecs_stage_conf['vault_secrets']:
        ecs_stage_conf['vault_secrets'][k] = f'stage-{get_random_string()}'
    for k in ecs_prod_conf['vault_secrets']:
        ecs_prod_conf['vault_secrets'][k] = f'prod-{get_random_string()}'
    #===== end secrets removal


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
    print(f'the following configurations are staged for {d["app_repo"]}\n')
    pprint(app_config)

    confirm = input('\nrender templates and write secrets to vault (yolo/no): ').strip().lower()
    if confirm == 'yolo':
        print('\nrendering templates and writing secrets')
        render_app_configs(app_config)
        # write secrets
        for app_env in app_config['env_configs']:
            if app_env['vault_secrets'] == {}:
                print(f'no secrets to write for app: {app_config["app_repo"]} in env: {app_env["env"]}')
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
                print(f'WARNING: unrecognized environment: {app_env["env"]}')
            print(write_response)
    else:
        print(f'\nskipping configuration of {d["app_repo"]}\n\n')
