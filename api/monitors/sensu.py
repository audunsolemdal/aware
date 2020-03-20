from typing import Dict, List

import requests

from config import Config
from utils import dead_mans_switch, truncate_string


def convert_severity(status) -> str:
    if status == 1:
        return "warning"
    elif status == 2:
        return "critical"
    else:
        return "none"


def get_sensu_events() -> List[Dict]:
    headers = {"AUTHORIZATION": f"Key {Config.sensu_key}"}
    try:
        request = requests.get(url=Config.sensu_api, headers=headers)
        data = request.json()
    except Exception as e:
        print(f"Fatal: Could not GET Sensu API {Config.sensu_api}. Error: {e}")
        return dead_mans_switch("Sensu checks", Config.sensu_api, e)

    not_passing_status = [check for check in data if check["check"]["state"] != "passing"]

    events = [{
        'alertname': event["check"]['metadata']['name'],
        'namespace': event["entity"]["metadata"]["name"],
        'severity': convert_severity(event["check"]["status"]),
        'message': truncate_string(event["check"]["output"]),
        'triggered': int(event["check"]["last_ok"]),
        "source": "Sensu"
    } for event in not_passing_status]

    return events