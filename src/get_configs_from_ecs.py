import boto3


def get_configs_from_ecs(
    cluster_arn: str,
    service_arn: str
) -> dict:
    
    ecs_client = boto3.client('ecs')


    service_response = ecs_client.describe_services(
        cluster=cluster_arn,
        services=[service_arn]
    )

    # assumes all tasks have same configuration
    task_definition_arn = service_response['services'][0]['taskDefinition']

    task_definition_response = ecs_client.describe_task_definition(
        taskDefinition=task_definition_arn
    )
    # get ecr_repository and image_tag
    image = task_definition_response['taskDefinition']['containerDefinitions'][0]['image']
    ecr_repository = image.split('/')[1].split(':')[0]
    image_tag = image.split(':')[-1]

    # get volume config
    volume_config = task_definition_response['taskDefinition'].get('volumes', None)
    volume_mount_sub_path = volume_config[0]['host']['sourcePath'][5:] if volume_config else None
    volume_mount_point = task_definition_response['taskDefinition']['containerDefinitions'][0]['mountPoints'][0]['containerPath'] if volume_config else None
    
    # get task env/secrets
    task_env = task_definition_response['taskDefinition']['containerDefinitions'][0]['environment']
    vault_secrets = {
        i["name"] : i["value"]
        for i in task_env
    }

    return {
        "ecr_repository": ecr_repository,
        "image_tag": image_tag,
        "volume_mount_path": volume_mount_point,
        "volume_mount_sub_path": volume_mount_sub_path,
        "vault_secrets": vault_secrets
    }
