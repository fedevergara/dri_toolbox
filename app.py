from utils.listas import tipos_documento, paises, vinculos, unidades, sedes
from flask import Flask, request, render_template
from utils.actualizacion_eventos import actualizar_eventos
from pymongo import MongoClient, DESCENDING
from utils.send_email import enviar_correo
from dash import Dash, html, dcc, Output, Input
from bson.objectid import ObjectId
from time import time
import qrcode
import json
import os
import pandas as pd
import plotly.express as px

db_uri = "mongodb://localhost:27017/"
db_name = "international"
events_collection = "events"
assistants_collection = "assistants"

dbclient = MongoClient(db_uri)
db = dbclient[db_name]
events = db[events_collection]
assistants = db[assistants_collection]

# Create Flask instance
server = Flask(__name__)

registros_eventos = actualizar_eventos()

eventos_por_dia = {}

for evento in registros_eventos:
    dia = evento['dia']
    if dia in eventos_por_dia:
        eventos_por_dia[dia].append(evento)
    else:
        eventos_por_dia[dia] = [evento]

# Create a route


@server.route("/")
def index():
    return render_template("index.html")


@server.route("/registro_movilidad", methods=["GET", "POST"])
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


@server.route('/buscar_correo')
def buscar_correo():
    email = request.args.get('email')
    document = events.find_one({'email': email},
                               sort=[('_id', DESCENDING)])

    response = json.dumps(document, default=str, ensure_ascii=False)
    return response


@server.route('/registro_eventos', methods=['GET', 'POST'])
def registro_eventos():
    record = None
    error = None
    form_success = False

    if request.method == 'POST':
        email = request.form['email'].lower()
        evento = request.form.getlist('eventos')
        documento_identidad = request.form['documento']

        # Añade una verificación para evitar registros duplicados basados en correo y eventos
        existing_record = events.find_one({
            "email": email,
            "eventos": {"$in": evento},
            "numero_documento_identidad": documento_identidad
        })

        if existing_record:
            error = "Ya existe un registro para el/los eventos seleccionados con este correo electrónico y número de documento."

        else:
            tipo_documento = request.form['tipos_documento']
            nombres = request.form['nombres'].strip().title()
            apellidos = request.form['apellidos'].strip().title()
            pais = request.form['pais']
            ciudad = request.form['ciudad'].strip().title()
            entidad = request.form['entidad'].strip().title()
            vinculo = request.form['vinculo']
            unidad = request.form['unidad'] if vinculo != "Externo" else "N/A"
            programa = request.form['programa'].strip(
            ).title() if vinculo != "Externo" else "N/A"
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
            elif unidad == "Unidad Académica/Administrativa:" and vinculo != "Externo":
                error = "Por favor, seleccione una dependencia."
            elif sede == "Campus de origen:" and vinculo != "Externo":
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

        if not os.path.exists(PATH):
            os.makedirs(PATH)

        img = qrcode.make(str(dehydrated_record))
        img.save(PATH + QR)

        # Insertar el documento en la colección de MongoDB
        record['qr'] = QR
        events.insert_one(record)

        del record['_id']
        del record['registro']

        try:
            # Enviar correo electrónico con el código QR
            qr_url = PATH + QR
            enviar_correo(
                record['email'], f"Registro exitoso - De País en País Centroamérica y el Caribe - {dehydrated_record['email']}", dehydrated_record, qr_url, record["eventos"])
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


@server.route('/registro_asistencia', methods=['GET', 'POST'])
def registro_asistencia():
    registro = None

    type_ = request.content_type
    if type_ == "application/json":
        try:
            data = request.json
            registro = json.loads(data['data'].replace("'", "\""))
            data_evento = data['evento']
            json_text = data_evento.replace("'", "\"")
            evento_json = json.loads(json_text)
            evento_registrado = evento_json['dia'] + \
                " | " + evento_json['evento']

        except Exception as e:
            print("Error al cargar los datos:", e)

        if registro:
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

            existing_record = assistants.find_one({
                "email": registro['email'],
                "numero_documento_identidad": registro['numero_documento_identidad'],
                "nombres": registro['nombres'],
                "apellidos": registro['apellidos'],
                "evento": evento_registrado
            })

            if not existing_record:
                assistants.insert_one(record)
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


# app = Dash(server=server, routes_pathname_prefix="/dash/")
# app.layout = create_app()

# Aplicación Dash

def actualizacion_eventos(events):
    datos_events = list(events.find())
    return datos_events


def crear_dataframe(datos_events):

    # Inicializa listas para construir el DataFrame
    asistencias = []
    vinculos = []
    sedes = []

    # Itera sobre los documentos para obtener asistencias únicas a cada evento
    for documento in datos_events:
        eventos = documento['eventos']
        email = documento['email']
        vinculo = documento['vinculo']
        sede = documento['sede']

        for evento in eventos:
            asistencias.append({'email': email, 'dia': evento.split(
                "|")[0].strip(), 'evento': evento.split("|")[1].strip()})
            vinculos.append(vinculo)
            sedes.append(sede)

    # Crea un DataFrame con las asistencias
    df = pd.DataFrame(asistencias)

    # Agrega las columnas 'vinculo' y 'sede' al DataFrame
    df['vinculo'] = vinculos
    df['sede'] = sedes

    # Calcula el conteo de eventos
    conteo_eventos = df['evento'].value_counts()
    conteo_eventos_dict = conteo_eventos.to_dict()
    df['conteo_evento'] = df['evento'].map(conteo_eventos_dict)

    return df


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(server=server, routes_pathname_prefix="/dash/")
df = crear_dataframe(actualizacion_eventos(events))

app.layout = html.Div([
    html.H1("Conteo de registros - eventos de De País en País Centroamérica y el Caribe",
            style={"textAlign": "center"}),
    html.Hr(),
    html.Div(id="bar-div", children=[]),
    html.Hr(),
    html.P("Eventos:"),
    html.Div(html.Div([
        dcc.Dropdown(id='dia-lista', clearable=False,
                     value="Viernes 3 de noviembre",
                     options=[{'label': x, 'value': x} for x in
                              df["dia"].unique()]),
    ]), className="row"),


    html.Div(id="output-div", children=[]),
])


@app.callback([
    Output(component_id="bar-div", component_property="children"),
    Output(component_id="output-div", component_property="children")],
    Input(component_id="dia-lista", component_property="value"),
)
def make_graphs(dia_escogido):
    df = crear_dataframe(actualizacion_eventos(events))

    # BAR CHART
    df_bar = df['vinculo'].value_counts().reset_index()
    df_bar.columns = ['vinculo', 'total_asistentes']
    total_inscritos = df_bar['total_asistentes'].sum()
    total_inscritos_df = pd.DataFrame(
        {'vinculo': ['Total de Inscritos'], 'total_asistentes': [total_inscritos]})
    df_bar = pd.concat([df_bar, total_inscritos_df])

    # Crear el gráfico de barras
    fig_bar = px.bar(df_bar, x="total_asistentes", y="vinculo",
                     color="vinculo", text="total_asistentes")
    fig_bar.update_layout(
        title="Total de Asistentes por Vínculo",
        xaxis_title="Número de Asistentes",
        yaxis_title="Vínculo",
    )

    fig_bar.update_traces(marker=dict(line=dict(width=1)))
    fig_bar.update_xaxes(dtick=1)

    # HISTOGRAM
    df_hist_ = df[df["dia"] == dia_escogido]
    df_hist = df_hist_.pivot_table(values='email', index=[
        'dia', 'evento', 'vinculo'], aggfunc='count').reset_index().sort_values(by='email', ascending=False)
    fig_hist = px.bar(df_hist, x='email', y="evento",
                      color="vinculo", text="email")
    fig_hist.update_xaxes(dtick=1)
    fig_hist.update_layout(
        title="Asistentes por Vínculo a eventos del día {}".format(
            dia_escogido),
        xaxis_title="Número de Asistentes",
        yaxis_title="Vínculo",
    )

    return [
        html.Div([
            html.Div([dcc.Graph(figure=fig_bar)], className="twelve columns"),
        ], className="row"),
        html.Div([
            html.Div([dcc.Graph(figure=fig_hist)], className="twelve columns"),
        ], className="row")]


# Errors handlers
# Invalid URL
@server.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template("404.html"), 404

# Internal server error


@server.errorhandler(500)
def internal_server_error(e):
    print(e)
    return render_template("505.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
