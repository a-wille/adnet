import base64
import os.path
import time
from email.message import EmailMessage
import schedule
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from webapp.view_helpers import get_mongo

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def check_user_accounts(service):
    conn = get_mongo()
    docs = conn.AdNet.users.find({})
    for doc in docs:
        if doc['status'] == 'verified' and doc['email_sent'] == False:
            gmail_send_message(service, doc['id'])
            conn.AdNet.users.update_one(
                {'id': doc['id']},
                {'$set': {'email_sent': True}}
            )



def gmail_send_message(service, email):

    try:
        message = EmailMessage()

        message.set_content('An administrator has officially approved your account for further access to the AdNet page. Sign in to explore genes and start building your first neural network!')

        message['To'] = email
        message['From'] = 'information@adnet.app'
        message['Subject'] = 'Account Approval'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message

def create_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
        return None


if __name__ == '__main__':
    service = create_service()
    schedule.every().day.at("11:30").do(lambda: check_user_accounts(service))
    while True:
        schedule.run_pending()
        time.sleep(1)