import requests
from config import Config
from loggers.loki import get_container_logs, get_job_logs
from utils import (dead_mans_switch, get_path, local_to_epoch_time,
                   truncate_string)

ignore_alert_list = Config.ignore_alert_list


def get_prometheus_events():
    try:
        request = requests.get(url=Config.prometheus_api)
        request.raise_for_status()
        data = request.json()
        # data = json.loads(Config.prom_test_data)
    except Exception as e:
        print(f'Fatal: Could not GET prometheus API {Config.prometheus_api}. Error: {e}')
        return dead_mans_switch("Prometheus events", Config.prometheus_api, e)

    filtered = [alert for alert in data['data']['alerts']
                if alert['labels']['alertname'] not in ignore_alert_list]

    events = []
    for event in filtered:
        annotation = event.get("annotations")
        message = annotation.get("message") if "message" in annotation else annotation.get("description")
        pod = event["labels"].get("pod")

        container_logs = get_container_logs(pod)if pod and Config.loki_api else ["No logs"]
        if container_logs != "No logs":
            log_to_display = container_logs
        else:
            job = event["labels"].get("job")
            job_logs = get_job_logs(job)if job and Config.loki_api else ["No logs"]
            if job_logs != "No logs":
                log_to_display = job_logs
            else:
                job_logs = "No logs found, only pods and jobs are currently supported"

        events.append({
            'alertname': get_path(event, 'labels', 'alertname'),
            'namespace': get_path(event, 'labels', 'namespace'),
            'severity': get_path(event, 'labels', 'severity'),
            'message': truncate_string(message),
            'triggered': local_to_epoch_time(event['activeAt']),
            "source": "Prometheus",
            "logs": log_to_display
        })

    return events
