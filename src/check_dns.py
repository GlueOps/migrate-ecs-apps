import requests


def check_dns(
    domain: str,
    query_type: str = 'NS'
) -> dict:
    return requests.get(
        'https://dns.google/resolve',
        params={
            "name": domain,
            "type": query_type
        }
    )
