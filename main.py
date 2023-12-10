import os

from glueops.setup_logging import configure as go_configure_logging

# from src.load_vault import load_secrets_to_vault
from src.get_configs_from_ecs import get_configs_from_ecs
from src.create_app_configs.create_app_configs import render_app_configs
from src.stage_app_data import stage_app_data_from_csv

# configure logger
logger = go_configure_logging(
    name='GO_MIGRATE_APP',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)


from pprint import pprint

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
                "vault_secrets": ecs_stage_conf['vault_secrets']
            },
            {
                "env": "prod",
                "image_tag": ecs_prod_conf['image_tag'],
                "hostnames": d['prod_hostnames'],
                "volume_mount_claim_name": d['prod_volume_mount_claim_name'],
                "volume_mount_path": ecs_prod_conf['volume_mount_path'],
                "volume_mount_sub_path": ecs_prod_conf['volume_mount_sub_path'],
                "web_acl_name": "primary",
                "vault_secrets": ecs_prod_conf['vault_secrets']
            }
        ]
    }
    print(f'the following configurations are staged for {d["app_repo"]}\n')
    pprint(app_config)

    confirm = input('\nrender templates and write secrets to vault (yolo/no): ').strip().lower()
    if confirm == 'yolo':
        print('\nrendering templates and writing secrets')
        render_app_configs(app_config)
    else:
        print(f'\nskipping configuration of {d["app_repo"]}\n\n')
