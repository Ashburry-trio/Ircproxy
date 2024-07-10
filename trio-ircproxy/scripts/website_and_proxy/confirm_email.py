import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser
from fnmatch import fnmatch

class EndSession(BaseException):
    """
    Close Python3 because of an error
    """

config = ConfigParser()
config.read("secrets.ini", 'utf8')
if not config.has_section('email'):
    config.add_section('email')
if not 'from' in config['email'].keys() or not 'password' in config['email'].keys() or not \
                            fnmatch(config["email"]['from'],"?*@*?.?*") or not  'smtp' in config['email'].keys():
    config['email']['from'] = 'your_email@gmail.com'
    config['email']['password'] = 'yourEmail-password'
    config['email']['smtp'] = 'smtp.gmail.com'
    with open('secrets.ini', 'w') as fp:
        config.write(fp, space_around_delimiters=True)
    raise BaseException('Please set up email in ./trio_ircproxy/scripts/website_and_proxy/secrets.ini')


sender_email: str = config['email']['from']
receiver_email: str = ""
password: str = config['email']['password']
smtp_server: str = config['email']['smtp']

message = MIMEMultipart("alternative")
message["Subject"] = "Test Email"
message["From"] = sender_email
message["To"] = receiver_email

text = "Click the link  below to confirm your email address, or copy and paste teh link in to your browser:\n\n"
part = MIMEText(text, "plain")
message.attach(part)

with smtplib.SMTP_SSL(smtp_server, 465) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
print("Email Sent")