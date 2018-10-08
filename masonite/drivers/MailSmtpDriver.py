"""SMTP Driver Module."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from masonite.contracts.MailContract import MailContract
from masonite.drivers.BaseMailDriver import BaseMailDriver


class MailSmtpDriver(BaseMailDriver, MailContract):
    """Mail smtp driver."""

    def send(self, message_contents=None):
        """Send the message through SMTP.

        Keyword Arguments:
            message {string} -- The message to be sent to SMTP. (default: {None})

        Returns:
            None
        """
        config = self.config.DRIVERS['smtp']

        message = MIMEMultipart('alternative')

        if not message_contents:
            message_contents = self.message_body

        message_contents = MIMEText(message_contents, 'html')

        message['Subject'] = self.message_subject
        message['From'] = '{0} <{1}>'.format(
            self.config.FROM['name'], self.config.FROM['address'])
        message['To'] = self.to_address
        message.attach(message_contents)

        # Send the message via our own SMTP server.
        if 'ssl' in config and config['ssl'] is True:
            self.smtp = smtplib.SMTP_SSL('{0}:{1}'.format(config['host'], config['port']))
        else:
            self.smtp = smtplib.SMTP('{0}:{1}'.format(
                config['host'], config['port']))

        self.smtp.login(config['username'], config['password'])

        # self.smtp.send_message(message)
        self.smtp.sendmail(self.config.FROM['name'],
                   self.to_address, message.as_string())
        self.smtp.quit()
