import os

from glueops.setup_logging import configure as go_configure_logging

from src.load_vault import load_secrets_to_vault
from src.get_configs_from_ecs import get_configs_from_ecs
# from src.create_app_configs.create_app_configs import render_app_configs

# configure logger
logger = go_configure_logging(
    name='GO_MIGRATE_APP',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)



from pprint import pprint

pprint(
get_configs_from_ecs(
        cluster_arn=os.environ['CLUSTER_ARN'],
        service_arn=os.environ['SERVICE_ARN']
    )
)

test_app_config = {
    "app_repo": "my-repository",
    "ecr_repository": "my.ecr.repo",
    "env_configs": [
        {
            "env": "stage",
            "image_tag": "v0.1.0",
            "hostnames": [
                "stage.example.com",
                "www.stage.example.com"
            ],
            # "volume_mount_claim_name": "my-claim",
            # "volume_mount_sub_path": "my-sub-path"
            # "web_acl_name": "my-web-acl"
        },
        {
            "env": "prod",
            "image_tag": "v0.1.0",
            "hostnames": [
                "example.com",
                "www.example.com"
            ],
            "volume_mount_claim_name": "my-claim",
            "volume_mount_sub_path": "my-sub-path",
            "web_acl_name": "my-web-acl"
        }
    ]
}

# render_app_configs(test_app_config)
