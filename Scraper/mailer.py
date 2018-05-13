import smtplib
from datetime import datetime
from os import environ


class Mailer(object):
    def __init__(self, body):
        self.fromAddress = environ.get("MAIL_EMAIL")
        self.toAddress = environ.get("MAIL_TO")
        self.password = environ.get("MAIL_PASSWORD")
        self.send_mail(body)

    def send_mail(self, body):
        subject = 'Bowling Score update - ' + datetime.now().strftime('%d-%m-%Y')

        header = 'From: %s\n' % self.fromAddress
        header += 'To: %s\n' % ','.join(self.toAddress)
        header += 'Subject: %s\n\n' % subject
        message = header + body

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.fromAddress, self.password)
        server.sendmail(self.fromAddress, self.toAddress, message)
        server.quit()