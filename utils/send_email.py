import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request

from config import SECRET_FILE

def Create_Service(client_secret_file, api_name, api_version, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

    if os.path.exists(f"./pickle/{pickle_file}"):
        with open(f"./pickle/{pickle_file}", 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(f"./pickle/{pickle_file}", 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


def enviar_correo(enviar_a, asunto, registro, qr_url, eventos):
    CLIENT_SECRET_FILE = SECRET_FILE
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    mimeMessage = MIMEMultipart()

    if registro:
        eventos = eventos
        html = """
        <html>
        <body>
            <p>Gracias por registrarse en los eventos: </p>
            {% for evento in eventos %}
                <div>
                    <p>{{ evento }}</p>
                </div>
            {% endfor %}
        </body>
        </html>
        """

    if registro and qr_url:
        with open(qr_url, 'rb') as image_file:
            image_data = image_file.read()
    
        # Adjunta la imagen al correo
        image_attachment = MIMEImage(image_data)
        file = registro['email'].replace('.','')
        image_attachment.add_header("Content-Disposition", "attachment", filename=f"{file}.jpg")
        mimeMessage.attach(image_attachment)

        mimeMessage['to'] = enviar_a
        mimeMessage['subject'] = asunto
        mimeMessage.attach(MIMEText(html, 'html'))
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

        message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        print(message)
        return message
    
    else:
        print("No se pudo enviar el correo electrónico.")
        return None