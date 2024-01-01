from datetime import datetime, timedelta

zabbix_event = {"alert_target": {"type": "string"},
                "alert_id": {"type": "string"},
                "alert_message": {"type": "string"},
                "alert_age": {"type": "string"},
                "alert_type": {"type": "string"},
                "alert_threshold": {"type": "number"},
                "alert_status": "RESOLVED",
                "host_group": {"type": "string"},
                "host_os": {"type": "string"},
                "host_name": {"type": "string"},
                "host_ip": {"type": "string"},
                "notify_action": {"type": "string"},
                "notify_only": {"type": "string"},
                "notify_message": {"type": "string"},
                "message": {"type": "string"}, }

itsm_ticket_open = {
    "customer": "customer",
    "event_id": "event_id",
    "event_date": datetime.strptime("2022-11-23 14:10:00", '%Y-%m-%d %H:%M:%S'),
    "source": "itsm_handler",
    "action_name": "action",
    "ticket_id": 12,
    "execution_state": "execution_status",
    "execution_code": 'execution_code',
    "execution_data": "execution_data"
}
alert_status = zabbix_event.get("alert_status")
alert_date = itsm_ticket_open.get("event_date")

print('=====START======')
if alert_status == "PROBLEM":
    print('Abrir chamado')
elif alert_status == "RESOLVED":
    reference = datetime.now()
    diff = reference - alert_date
    diff_minutes = diff.seconds / 60
    if diff_minutes > 15:
        print('Mantendo o ticket aberto para trativa')
        print(itsm_ticket_open.get("event_date"))
    else:
        print('Encerramento do ticket')
else:
    print(f'{alert_status} não reconhecido')

print('======END=======')
