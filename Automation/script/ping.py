import os

hostname =  "google.com"
response = os.system("ping -c 1 " + hostname)

print(response)

if response == 0:
    print(f"{hostname} is up!")
else:
        print(f"{hostname} is down!")
