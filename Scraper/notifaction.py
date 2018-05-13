from http.client import HTTPSConnection
from urllib import parse


class Notification(object):
    def __init__(self, message, title, token, user):
        self.message = message
        self.title = title
        self.token = token
        self.user = user

        self.send()

    def send(self):
        body = {
            'token': self.token,
            'user': self.user,
            'message': self.message,
            'title': self.title
        }

        conn = HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json", parse.urlencode(body), {"Content-type": "application/x-www-form-urlencoded"})
        conn.getresponse()