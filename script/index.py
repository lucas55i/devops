import requests
import json
import xlsxwriter
 
# Mapeamento de números de severidade para nomes
severity_map = {
    '0': 'Not classified',
    '1': 'Information',
    '2': 'Warning',
    '3': 'Average',
    '4': 'High',
    '5': 'Disaster'
}
 
 
def get_zabbix_triggers():
    # Configurações de conexão com o Zabbix
    # Substitua 'seu_zabbix' pela URL do seu servidor Zabbix
    url = ''
    headers = {'Content-Type': 'application/json'}
 
    # Credenciais de acesso ao Zabbix
    # Substitua 'seu_usuario' pelo seu nome de usuário do Zabbix
    username = ''
    password = ''  # Substitua 'sua_senha' pela sua senha do Zabbix
 
    # Payload da solicitação de autenticação
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": username,
            "password": password
        },
        "id": 1
    }
    # Realiza a solicitação de autenticação
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    result = response.json()
 
    if 'result' in result:
        auth_token = result['result']
        # Payload da solicitação para obter as triggers
        trigger_payload = {
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                # Adicionando a prioridade (severidade) da trigger
                "output": ["description", "priority"]
            },
            "auth": auth_token,
            "id": 1
        }
 
        # Realiza a solicitação para obter as triggers
        response = requests.post(url, headers=headers,
                                 data=json.dumps(trigger_payload))
        trigger_result = response.json()
 
        if 'result' in trigger_result:
            triggers = trigger_result['result']
            return triggers
        else:
            print("Erro ao obter as triggers:",
                  trigger_result['error']['data'])
    else:
        print("Erro de autenticação:", result['error']['data'])
 
 
def write_triggers_to_excel(triggers, filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
 
    # Escrevendo cabeçalhos
    worksheet.write(0, 0, 'Severidade')
    worksheet.write(0, 1, 'Descrição')
 
    # Escrevendo dados das triggers
    row = 1
    for trigger in triggers:
        # Obtendo o número de severidade da trigger
        severity_num = str(trigger['priority'])
        # Mapeando o número para o nome da severidade
        severity_name = severity_map.get(severity_num, 'Unknown')
        description = trigger['description']
        worksheet.write(row, 0, severity_name)
        worksheet.write(row, 1, description)
        row += 1
 
    workbook.close()
 
 
if __name__ == "__main__":
    triggers = get_zabbix_triggers()
    if triggers:
        print("Triggers no Zabbix:")
        for trigger in triggers:
            severity_num = str(trigger['priority'])
            severity_name = severity_map.get(severity_num, 'Unknown')
            print("Severidade:", severity_name,
                  "| Descrição:", trigger['description'])
        write_triggers_to_excel(triggers, 'triggers.xlsx')
        print("As triggers foram escritas no arquivo triggers.xlsx")
    else:
        print("Não foi possível obter as triggers.")