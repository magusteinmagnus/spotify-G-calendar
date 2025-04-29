import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ==== GOOGLE CALENDAR AUTH ====
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

# ==== SPOTIFY AUTH ====
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='YOUR_SPOTIFY_CLIENT_ID',
    client_secret='YOUR_SPOTIFY_CLIENT_SECRET',
    redirect_uri='http://localhost:8888/callback',
    scope='user-read-playback-state user-modify-playback-state app-remote-control streaming'
))

# ==== GET UPCOMING CALENDAR EVENTS ====
now = datetime.datetime.utcnow().isoformat() + 'Z'
print('🔍 Fetching your next 5 events...\n')

events_result = service.events().list(
    calendarId='primary', timeMin=now,
    maxResults=5, singleEvents=True,
    orderBy='startTime').execute()
events = events_result.get('items', [])

if not events:
    print('No upcoming events found.')
else:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No Title')

        print(f"🗓️ {start} → {summary}")

        # ==== SYNC TO SPOTIFY BASED ON EVENT TITLE ====
        summary_lower = summary.lower()

        if 'workout' in summary_lower:
            print("💪 Workout detected. Playing workout playlist...\n")
            sp.start_playback(context_uri="spotify:playlist:YOUR_WORKOUT_PLAYLIST_URI")

        elif 'study' in summary_lower or 'lofi' in summary_lower:
            print("📚 Study session detected. Playing lofi playlist...\n")
            sp.start_playback(context_uri="spotify:playlist:YOUR_LOFI_PLAYLIST_URI")

        elif 'meeting' in summary_lower:
            print("📵 Meeting detected. Pausing playback...\n")
            sp.pause_playback()

        else:
            print("🟡 Event not mapped to any Spotify action.\n")
        # Optional: Add more conditions for different event types
        # You can also add a default action if no conditions are met
        # For example, play a specific playlist or pause playback
        # Optional: Add a delay between actions to avoid rate limiting
        # time.sleep(1)  # Uncomment if needed
        # Note: Make sure to replace YOUR_SPOTIFY_CLIENT_ID, YOUR_SPOTIFY_CLIENT_SECRET,
        # YOUR_WORKOUT_PLAYLIST_URI, and YOUR_LOFI_PLAYLIST_URI with your actual values.
        # You can also add more conditions for different event types
        # You can also add a default action if no conditions are met
        # For example, play a specific playlist or pause playback
        # Optional: Add a delay between actions to avoid rate limiting      