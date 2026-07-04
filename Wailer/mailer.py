#!/usr/bin/env python3
# encoding: utf-8

import ssl
import smtplib
from cortexutils.responder import Responder
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailer(Responder):
    def __init__(self):
        Responder.__init__(self)
        self.smtp_host = self.get_param("config.smtp_host", "localhost")
        self.smtp_port = self.get_param("config.smtp_port", "25")
        self.mail_from = self.get_param("config.from", None, "Missing sender email address")
        self.bcc = self.get_param("config.bcc", None, "Missing bcc email address")
        self.smtp_user = self.get_param("config.smtp_user", "user", None)
        self.smtp_pwd = self.get_param("config.smtp_pwd", "pwd", None)

    def run(self):
        Responder.run(self)
        mail_to = None

        if self.data_type.startswith("dfir-iris-case"):
            title = self.get_param("data.title", None, "title is missing")
            description = self.get_param("data.description", None, "description is missing")
            mail_to = self.get_param("data.recipient", None, "recipient address not found")

        msg = MIMEMultipart()
        msg["Subject"] = title
        msg["From"] = self.mail_from

        if "," in mail_to:
            recipients = [item.strip() for item in str(mail_to).split(",")]
        else:
            recipients = [mail_to]

        msg["To"] = mail_to
        msg.attach(MIMEText(description, "plain", "utf-8"))

        if self.bcc:
            msg["Bcc"] = self.bcc
            recipients.append(self.bcc)

        if self.smtp_user and self.smtp_pwd:
            try:
                context = ssl.create_default_context()
                context.minimum_version = ssl.TLSVersion.TLSv1_2

                # STANDARD CONNECTION, TRY ADDING TLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(self.smtp_user, self.smtp_pwd)
                    server.send_message(msg, self.mail_from, recipients)
            except smtplib.SMTPServerDisconnected:
                # SMTP_SSL CONNECTION
                with smtplib.SMTP_SSL(
                    self.smtp_host, self.smtp_port, context=context
                ) as server:
                    server.login(self.smtp_user, self.smtp_pwd)
                    server.send_message(msg, self.mail_from, recipients)
            except Exception:
                # STANDARD CONNECTION WITHOUT TLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.ehlo()
                    server.login(self.smtp_user, self.smtp_pwd)
                    server.send_message(msg, self.mail_from, recipients)
        else:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg, self.mail_from, recipients)

        self.report({"message": "message sent"})

    def operations(self, raw):
        return []

if __name__ == "__main__":
    Mailer().run()