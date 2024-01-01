import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

destinarios = ['lukinhas_correia12@hotmail.com', 'lucas.devj@outlook.com']
server = smtplib.SMTP('smtp-mail.outlook.com', 587)

server.starttls()

server.login('lpZeus2@outlook.com', 'lucas-H963')

msg = MIMEMultipart()
msg['From'] = 'Lucas Silva'
msg['To'] = 'lucas_55i@outlook.com'  # Destinatario
msg['Subject'] = 'E-mail de teste'  # assunto


with open('index.html', 'r') as f:
    message = f.read()

msg.attach(MIMEText(message, 'html'))

filename = 'index.html'
attachment = open(filename, 'rb')

p = MIMEBase('application', 'octet-stream')
p.set_payload(attachment.read())


encoders.encode_base64(p)

text = msg.as_string()
server.sendmail('lpZeus2@outlook.com', 'lucas_55i@outlook.com', text, rcpt_options=destinarios)
