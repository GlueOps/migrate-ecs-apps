import os
from typing import List, TypedDict

from jinja2 import Environment, FileSystemLoader


class AppEnvConfig(TypedDict):
    env: str
    image_tag: str
    hostnames: List[str]
    volume_mount_claim_name: str
    volume_mount_path: str
    volume_mount_sub_path: str
    web_acl_name: str
    vault_secrets: str
    vault_secrets_path: str

    
class AppConfig(TypedDict):
    app_repo: str
    ecr_repository: str
    env_configs: List[AppEnvConfig]


renderer_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(renderer_dir, 'templates')
tpl_env = Environment(
    loader=FileSystemLoader(template_dir),
    keep_trailing_newline=True
)

def render_app_configs(app_config: AppConfig):
    render_base_config(
        app_repo=app_config['app_repo'],
        ecr_repository=app_config['ecr_repository']
    )
    for e in app_config['env_configs']:
        # evaluate presence of vault_secrets
        if e['vault_secrets'] == {}:
            e['vault_secrets_path'] = None
        render_env_config(
            app_repo=app_config['app_repo'],
            app_env=e['env'],
            image_tag=e['image_tag'],
            hostnames=e['hostnames'],
            volume_mount_claim_name=e.get('volume_mount_claim_name', None),
            volume_mount_path=e.get('volume_mount_path', None),
            volume_mount_sub_path=e.get('volume_mount_sub_path', None),
            external_secret_vault_path=e['vault_secrets_path'],
            web_acl_name=e.get('web_acl_name', None)
        )


def render_base_config(
    app_repo: str,
    ecr_repository: str
):
    
    template_file = 'base/base-values.yaml'
    
    base_config_path = f'/app/rendered_templates/{app_repo}/{template_file}'
    os.makedirs(os.path.dirname(base_config_path), exist_ok=True)
    
    template=tpl_env.get_template(template_file)
    rendered_base_config = template.render(
        app_repo=app_repo,
        ecr_repository=ecr_repository
    )
    
    with open(base_config_path, 'w') as f:
        f.write(rendered_base_config)


def render_env_config(
    app_repo: str,
    app_env: str,
    image_tag: str,
    hostnames: List[str],
    volume_mount_claim_name: str = None,
    volume_mount_path: str = None,
    volume_mount_sub_path: str = None,
    external_secret_vault_path: str = None,
    web_acl_name: str = None
    
    
):
    template_file = 'envs/values.yaml'
    output_file = f'envs/{app_env}/values.yaml'
    
    env_config_path = f'/app/rendered_templates/{app_repo}/{output_file}'
    os.makedirs(os.path.dirname(env_config_path), exist_ok=True)
    
    template=tpl_env.get_template(template_file)
    rendered_env_config = template.render(
        image_tag=image_tag,
        hostnames=hostnames,
        volume_mount_claim_name=volume_mount_claim_name,
        volume_mount_path=volume_mount_path,
        volume_mount_sub_path=volume_mount_sub_path,
        external_secret_vault_path=external_secret_vault_path,
        web_acl_name=web_acl_name
    )
    
    with open(env_config_path, 'w') as f:
        f.write(rendered_env_config)
