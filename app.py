from utils.listas import eventos, tipos_documento, paises, vinculos, unidades, sedes
from flask import Flask, request, render_template, redirect, url_for
from utils.actualizacion_eventos import actualizar_eventos
from pymongo import MongoClient, DESCENDING
from utils.send_email import enviar_correo
from flask_mail import Mail, Message
from bson.objectid import ObjectId
from time import time
import qrcode
import json

db_uri="mongodb://localhost:27017/"
db_name="international"
collection_name="events"

dbclient = MongoClient(db_uri)
db = dbclient[db_name]
collection = db[collection_name]

# Create Flask instance
app = Flask(__name__)

dias, eventos, ecards = actualizar_eventos()
print(dias, eventos, ecards)

# Create a route
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registro_movilidad", methods=["GET", "POST"])
def registro_movilidad():
    record = None

    if request.method == 'POST':
        nombre_diligencia = request.form['nombre_diligencia']
        correo_diligencia = request.form['correo_diligencia']
        telefono_diligencia = request.form['telefono_diligencia']
        año = request.form['año']
        semestre = request.form['semestre']
        modalidad = request.form['modalidad']
        categoria = request.form['categoria']   
        
        record = {
            '_id':ObjectId(),
            "nombre": nombre_diligencia,
            "email": correo_diligencia,
            "telefono": telefono_diligencia,
            "año": año,
            "semestre": semestre,
            "modalidad": modalidad,
            "categoria": categoria
        }

    return render_template("registro_movilidad.html",
                           paises=paises,
                           record=record)


@app.route('/buscar_correo')
def buscar_correo():
    email = request.args.get('email')
    document = collection.find_one({'email': email},
        sort=[( '_id', DESCENDING )])
    
    response = json.dumps(document, default=str, ensure_ascii=False)
    return response

@app.route('/registro_eventos', methods=['GET', 'POST'])
def registro_eventos():
    record = None
    error = None
    form_success = False

    if request.method == 'POST':
        email = request.form['email'].lower()
        evento = request.form.getlist('eventos')
        documento_identidad = request.form['documento']

        # Añade una verificación para evitar registros duplicados basados en correo y eventos
        existing_record = collection.find_one({
            "email": email,
            "eventos": {"$in": evento},
            "numero_documento_identidad": documento_identidad
            })

        if existing_record:
            error = "Ya existe un registro para el/los eventos seleccionados con este correo electrónico y número de documento."

        else:
            tipo_documento = request.form['tipos_documento']
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            pais = request.form['pais']
            ciudad = request.form['ciudad']
            entidad = request.form['entidad']
            vinculo = request.form['vinculo']
            unidad = request.form['unidad']
            programa = request.form['programa']
            sede = request.form['sede']

            record = {
                '_id': ObjectId(),
                "registro": int(time()),
                "eventos": evento,
                "email": email,
                "tipo_documento_identidad": tipo_documento,
                "numero_documento_identidad": documento_identidad,
                "nombres": nombres,
                "apellidos": apellidos,
                "pais": pais,
                "ciudad": ciudad,
                "entidad": entidad,
                "vinculo": vinculo,
                "unidad": unidad,
                "programa": programa,
                "sede": sede
            }

            # Realiza todas las verificaciones
            if not evento:
                error = "Por favor, seleccione al menos un evento."
            elif tipo_documento not in tipos_documento:
                error = "Por favor, seleccione un tipo de documento."
            elif pais not in paises:
                error = "Por favor, seleccione un país."
            elif vinculo not in vinculos:
                error = "Por favor, seleccione un vínculo."
            elif unidad not in unidades:
                error = "Por favor, seleccione una dependencia."
            elif sede not in sedes:
                error = "Por favor, seleccione un campus."

            if error:
                # Devuelve el formulario con el mensaje de error y los valores ingresados
                return render_template('registro_eventos.html', dias=dias, eventos=eventos, ecards=ecards, tipos_documento=tipos_documento, paises=paises, vinculos=vinculos, unidades=unidades, sedes=sedes, record=record, error=error)

            else:
                form_success = True

            # Insertar el documento en la colección de MongoDB
            collection.insert_one(record)
            del record['_id']
            del record['registro']

    
    # Enviar correo electrónico con el código QR
    if form_success:
        dehydrated_record =  {
            "email": record['email'],
            "numero_documento_identidad": record['numero_documento_identidad'],
            "nombres": record['nombres'],
            "apellidos": record['apellidos']
        }
        print(dehydrated_record)
        # Genera el código QR
        QR =  record['email'].replace('.','') + '.png'
        PATH = "./images/QRs/"

        img = qrcode.make(str(dehydrated_record))
        img.save(PATH+QR)

        try:
            # Enviar correo electrónico con el código QR
            qr_url = PATH + QR
            #enviar_correo(record['email'], f"Registro exitoso De País en País - {dehydrated_record['email']}", dehydrated_record, qr_url, record["eventos"])
        except Exception as e:
            print("Error al enviar el correo electrónico:", e)
        

    # Renderiza el formulario sin errores
    return render_template('registro_eventos.html', dias=dias, eventos=eventos, ecards=ecards, tipos_documento=tipos_documento, paises=paises, vinculos=vinculos, unidades=unidades, sedes=sedes, record=record, error=error, form_success=form_success)

# Errors handlers
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("505.html"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)