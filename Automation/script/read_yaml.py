import yaml


with open("Automation/script/config.yaml", 'r') as file:
    data =  yaml.safe_dump(file)

print(data)
