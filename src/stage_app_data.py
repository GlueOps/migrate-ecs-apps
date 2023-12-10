import csv


def stage_app_data_from_csv(
    csv_path: str
):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        result = []

        for r in reader:
            record = {
                key: value for key, value in r.items()
                if not key.startswith('stage_hostname') and not key.startswith('prod_hostname')
            }
            if record['stage_volume_mount_claim_name'].lower() == 'none':
                record['stage_volume_mount_claim_name'] = None
            prod_hostnames = [
                value for key, value in r.items()
                if key.startswith('prod_hostname') and value
            ]
            stage_hostnames = [
                value for key, value in r.items()
                if key.startswith('stage_hostname') and value
            ]
            record['prod_hostnames'] = prod_hostnames
            record['stage_hostnames'] = stage_hostnames

            result.append(record)

    return result
