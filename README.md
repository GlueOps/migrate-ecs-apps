# migrate-ecs-apps

## Environment Variable File Configuration

```sh
docker build . -t migrate-ecs && docker run --env-file .env -t migrate-ecs
```

```.env
#AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=

# nonproduction vault
NONPROD_VAULT_URL=
KUBERNETES_ROLE=
NONPROD_VAULT_TOKEN=
NONPROD_POMERIUM_COOKIE=

# production vault
PROD_VAULT_URL=
KUBERNETES_ROLE=
PROD_VAULT_TOKEN=
PROD_POMERIUM_COOKIE=
```
