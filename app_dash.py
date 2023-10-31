from dash import Dash, html, dcc, Output, Input
import pandas as pd
from pymongo import MongoClient
import plotly.express as px


db_uri = "mongodb://localhost:27017/"
db_name = "international"
events = "events"
assistants = "assistants"


def actualizar_eventos(db_uri, db_name, events, url_base_pathname='/DPEP/indicadores_registros'):
    dbclient = MongoClient(db_uri)
    db = dbclient[db_name]

    events = db[events]

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


# APP DASH
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

df = crear_dataframe(actualizar_eventos(db_uri, db_name, events))

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
    df = crear_dataframe(actualizar_eventos(db_uri, db_name, events))

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


if __name__ == '__main__':
    app.run_server(port=8002)
