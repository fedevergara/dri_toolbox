from utils.listas import tipos_documento, paises, vinculos, unidades, sedes
from flask import Flask, request, render_template
from utils.actualizacion_eventos import actualizar_eventos
from pymongo import MongoClient, DESCENDING
from utils.send_email import enviar_correo
from bson.objectid import ObjectId
from time import time
import time as t
import qrcode
import json

db_uri = "mongodb://localhost:27017/"
db_name = "international"
collection_name = "events"
assistants = "assistants"

dbclient = MongoClient(db_uri)
db = dbclient[db_name]
collection = db[collection_name]
collection_assistants = db[assistants]

# Create Flask instance
app = Flask(__name__)

registros_eventos = actualizar_eventos()

eventos_por_dia = {}

for evento in registros_eventos:
    dia = evento['dia']
    if dia in eventos_por_dia:
        eventos_por_dia[dia].append(evento)
    else:
        eventos_por_dia[dia] = [evento]

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
            '_id': ObjectId(),
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
                                   sort=[('_id', DESCENDING)])

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
            unidad = request.form['unidad'] if vinculo != "Externo" else "N/A"
            programa = request.form['programa'] if vinculo != "Externo" else "N/A"
            sede = request.form['sede'] if vinculo != "Externo" else "N/A"

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
                "sede": sede,
                "qr": ""
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
            elif unidad not in unidades and vinculo != "Externo":
                error = "Por favor, seleccione una dependencia."
            elif sede not in sedes and vinculo != "Externo":
                error = "Por favor, seleccione un campus."

            if error:
                # Devuelve el formulario con el mensaje de error y los valores ingresados
                return render_template(
                    'registro_eventos.html',
                    eventos=eventos_por_dia,
                    tipos_documento=tipos_documento,
                    paises=paises, vinculos=vinculos,
                    unidades=unidades,
                    sedes=sedes,
                    record=record,
                    error=error
                )

            else:
                form_success = True


    # Enviar correo electrónico con el código QR
    if form_success:
        dehydrated_record = {
            "email": record['email'],
            "numero_documento_identidad": record['numero_documento_identidad'],
            "nombres": record['nombres'],
            "apellidos": record['apellidos']
        }

        # Genera el código QR
        QR = record['email'].replace('.', '') + '.png'
        PATH = "./static/images/QRs/"

        img = qrcode.make(str(dehydrated_record))
        img.save(PATH + QR)

        # Insertar el documento en la colección de MongoDB
        record['qr'] = QR
        collection.insert_one(record)
        
        del record['_id']
        del record['registro']

        try:
            # Enviar correo electrónico con el código QR
            qr_url = PATH + QR
            enviar_correo(record['email'], f"Registro exitoso De País en País - {dehydrated_record['email']}", dehydrated_record, qr_url, record["eventos"])
        except Exception as e:
            print("Error al enviar el correo electrónico:", e)

    # Renderiza el formulario sin errores
    return render_template(
        'registro_eventos.html',
        eventos=eventos_por_dia,
        tipos_documento=tipos_documento,
        paises=paises,
        vinculos=vinculos,
        unidades=unidades,
        sedes=sedes,
        record=record,
        error=error,
        form_success=form_success
    )


@app.route('/registro_asistencia', methods=['GET', 'POST'])
def registro_asistencia():    
    type_ = request.content_type
    if type_ == "application/json":
        try:
            data = request.json
            registro = json.loads(data['data'].replace("'", "\""))
            evento_registrado = data['evento']
        except Exception as e:
            print("Error al cargar los datos:", e)

        record = {
            '_id': ObjectId(),
            "registro": int(time()),
            "email": registro['email'],
            "numero_documento_identidad": registro['numero_documento_identidad'],
            "nombres": registro['nombres'],
            "apellidos": registro['apellidos'],
            "evento": evento_registrado,
        }

        # Accede a la cámara y captura información del QR (implementación necesaria)
        # Verifica y almacena el registro en MongoDB
        
        existing_record = collection_assistants.find_one({
            "email": registro['email'],
            "numero_documento_identidad": registro['numero_documento_identidad'],
            "nombres": registro['nombres'],
            "apellidos": registro['apellidos'],
            "evento": evento_registrado
        })

        if not existing_record:
            collection_assistants.insert_one(record)
            print("Registro exitoso.")
        else:
            print("Ya se encuentra registrada la asistencia.")
    
    eventos_enviar = []
    for evento_ in registros_eventos:
        e = {
            "dia": evento_['dia'],
            "evento": evento_['evento']
        }
        eventos_enviar.append(e)

    return render_template("registro_asistencia.html",
                           eventos=eventos_enviar)


# Errors handlers
# Invalid URL

@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template("404.html"), 404

# Internal server error


@app.errorhandler(500)
def internal_server_error(e):
    print(e)
    return render_template("505.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
