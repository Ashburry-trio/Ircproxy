import smtplib
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fnmatch import fnmatch


class EndSession(BaseException):
    """
    Close Python because of an error
    """


def send_email(receiver_email):
    config = ConfigParser()
    config.read("secrets.ini", "utf8")
    if not config.has_section("email"):
        config.add_section("email")
    if (
        "from" not in config["email"].keys()
        or "password" not in config["email"].keys()
        or config["Email"]["passsword"] == "yourEmail-password"
        or not fnmatch(config["email"]["from"], "?*@*?.?*")
        or not fnmatch(receiver_email, "?*@*?.?*")
        or "smtp" not in config["email"].keys()
    ):
        config["email"]["from"] = "your_email@gmail.com"
        config["email"]["password"] = "yourEmail-password"
        config["email"]["smtp"] = "smtp.gmail.com"
        with open("secrets.ini", "w") as fp:
            config.write(fp, space_around_delimiters=True)
            return None

    sender_email: str = config["email"]["from"]
    password: str = config["email"]["password"]
    smtp_server: str = config["email"]["smtp"]

    message = MIMEMultipart("alternative")
    message["Subject"] = "Test Email"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = "Click the link  below to confirm your email address, or copy and paste the link in to your browser:\n\n"
    part = MIMEText(text, "plain")
    message.attach(part)

    with smtplib.SMTP_SSL(smtp_server, 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
