from utils.listas import get_eventos
from config import ONEDRIVE_TENANT, ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET, ONEDRIVE_CLIENT_USERNAME
from getpass import getpass
import json
import adal
import requests

tenant = ONEDRIVE_TENANT
client_id = ONEDRIVE_CLIENT_ID
username = ONEDRIVE_CLIENT_USERNAME
password = ONEDRIVE_CLIENT_SECRET

if not password:
    password = getpass("Contraseña: ")

authority = "https://login.microsoftonline.com/" + tenant
RESOURCE = "https://graph.microsoft.com"

context = adal.AuthenticationContext(authority)

token = context.acquire_token_with_username_password(RESOURCE, username, password, client_id)

URL = 'https://graph.microsoft.com/v1.0/'
HEADERS = {'Authorization': 'Bearer ' + token['accessToken']}
response = requests.get(URL + 'me/drive/', headers = HEADERS)

if (response.status_code == 200):
    response = json.loads(response.text)
    #print('Connected to the OneDrive of', response['owner']['user']['displayName']+' (',response['driveType']+' ).', \
    #     '\nConnection valid for one hour. Reauthenticate if required.')
elif (response.status_code == 401):
    response = json.loads(response.text)
    print('API Error! : ', response['error']['code'],\
         '\nSee response for more details.')
else:
    response = json.loads(response.text)
    print('Unknown error! See response for more details.')

def actualizar_eventos():
# Importa la lista de eventos
    eventos, ecards = get_eventos()

    def descarga_eventos(HEADERS):
        url = URL + "me/drive/items/01E3F34DQXJK3ATV6QJFHKNUH6HAI6UFPJ/workbook/tables('1')/rows"
        try:
            r = requests.get(url, headers=HEADERS)
            r.raise_for_status()  # Genera una excepción si la solicitud no fue exitosa

            events_names = []
            events_ecards = []
            for event in r.json().get('value', []):
                event_reg = event['values'][0]
                event_name = event_reg[0]
                event_ecard = event_reg[1]
                events_names.append(event_name)
                events_ecards.append(event_ecard)
                
            return events_names, events_ecards

        except requests.exceptions.RequestException as e:
            print("Error en la solicitud:", e)
            return None
        except Exception as e:
            print("Error inesperado:", e)
            return None
    
    def descarga_ecards(HEADERS):
        #List folders under root directory
        data = json.loads(requests.get(URL + 'me/drive/items/01E3F34DUV536AD3PM4ZCYJ6AGGKZXCCPH/children', headers=HEADERS).text)

        # Itera a través de los archivos y descarga las imágenes
        try:
            for item in data["value"]:
                if item["file"]["mimeType"].startswith("image"):
                    # Este es un archivo de imagen
                    image_url = item["@microsoft.graph.downloadUrl"]
                    image_name = item["name"]

                    # Realiza la solicitud GET para descargar la imagen
                    image_response = requests.get(image_url)

                    # Guarda la imagen en un archivo local
                    with open(f"images/ecards/{image_name}", "wb") as f:
                        f.write(image_response.content)

        except requests.exceptions.RequestException as e:
            print("Error en la solicitud:", e)
        except Exception as e:
            print("Error inesperado:", e)
    
    # Descarga los eventos de la hoja de cálculo
    nuevos_eventos, ecards = descarga_eventos(HEADERS)
    # Descarga las eCards
    descarga_ecards(HEADERS)

    # Modifica la lista de eventos
    eventos.extend(nuevos_eventos)

    # Guarda la lista actualizada en el módulo "eventos"
    from utils.listas import eventos as eventos_originales
    from utils.listas import ecards as ecards_originales

    eventos_originales[:] = eventos
    ecards_originales[:] = ecards

    return eventos, ecards