"""Automatisk e-postsvarare via Gmail API."""

import os
import pickle
import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .agents import ComplaintAgent

# Gmail API scope för att skicka mail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class AutoResponder:
    """Skickar automatiska svar via Gmail API."""

    def __init__(self):
        self.service = self._authenticate_gmail()
        self.sender_email = os.getenv("SENDER_EMAIL")
        self._complaint_agent = None

    @property
    def complaint_agent(self):
        if self._complaint_agent is None:
            self._complaint_agent = ComplaintAgent()
        return self._complaint_agent

    def _authenticate_gmail(self):
        """Autentiserar mot Gmail API."""
        creds = None

        # Kolla om vi har en sparad token
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # Om ingen giltig token, autentisera
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Spara token för nästa gång
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def _send_email(self, to: str, subject: str, body: str):
        """Skickar ett e-postmeddelande."""
        message = MIMEText(body)
        message['to'] = to
        message['from'] = self.sender_email
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self.service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        print(f"Mail skickat till {to}: {subject}")

    def create_and_send_auto_reply(self, email: dict):
        """Skapar och skickar ett generiskt autosvar."""
        subject = f"Autosvar: {email['subject']}"
        body = (
            f"Hej!\n\n"
            f"Tack för ditt mejl angående: {email['subject']}\n\n"
            f"Vi har mottagit ditt meddelande och återkommer så snart som möjligt.\n\n"
            f"Vänliga hälsningar,\n"
            f"Bengtssons Trävaror"
        )
        self._send_email(email['from'], subject, body)

    def create_auto_response_complaint(self, email: dict, to: str = None):
        """Skapar ett AI-genererat svar på ett klagomål."""
        to = to or email['from']
        subject = f"Svar på klagomål: {email['subject']}"
        body = self.complaint_agent.write_response_to_complaint(email)
        self._send_email(to, subject, body)
