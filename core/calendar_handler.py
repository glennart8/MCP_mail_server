"""Google Calendar-integration för mötesbokning."""

import os
import pickle
from datetime import datetime, timedelta

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarHandler:
    """Hanterar Google Calendar-events."""

    def __init__(self):
        self.service = self._authenticate_calendar()

    def _authenticate_calendar(self):
        """Autentiserar mot Google Calendar API."""
        creds = None

        if os.path.exists('token_calendar.pickle'):
            with open('token_calendar.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open('token_calendar.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('calendar', 'v3', credentials=creds)

    def create_event(
        self,
        subject: str,
        body: str,
        start_time: datetime,
        duration_minutes: int = 60
    ) -> str:
        """
        Skapar en kalenderhändelse.

        Args:
            subject: Mötets titel
            body: Beskrivning
            start_time: Starttid
            duration_minutes: Längd i minuter

        Returns:
            Länk till det skapade eventet
        """
        end_time = start_time + timedelta(minutes=duration_minutes)

        event = {
            'summary': subject,
            'description': body,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Europe/Stockholm',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Stockholm',
            },
        }

        created_event = self.service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        link = created_event.get('htmlLink')
        print(f"Möte skapat: {link}")
        return link

    def list_upcoming_events(self, max_results: int = 10) -> list:
        """Listar kommande kalenderhändelser."""
        now = datetime.utcnow().isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])
