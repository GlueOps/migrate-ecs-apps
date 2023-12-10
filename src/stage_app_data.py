import csv

def stage_app_data_from_csv(
    csv_path: str
):
    with open(csv_path, 'r') as f:
        f.read()
