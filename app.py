from flask import Flask, request, render_template
from utils.listas import eventos, tipos_documento, paises, vinculos, unidades, sedes

# Create Flask instance
app = Flask(__name__)

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
            "nombre": nombre_diligencia,
            "correo": correo_diligencia,
            "telefono": telefono_diligencia,
            "año": año,
            "semestre": semestre,
            "modalidad": modalidad,
            "categoria": categoria
        }

    return render_template("registro_movilidad.html",
                           paises=paises,
                           record=record)

@app.route('/registro_eventos', methods=['GET', 'POST'])
def registro_eventos():
    record = None
    error = None

    if request.method == 'POST':
        evento = request.form.getlist('eventos')
        email = request.form['correo']
        tipo_documento = request.form['tipos_documento']
        documento_identidad = request.form['documento']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        pais = request.form['pais']
        ciudad = request.form['ciudad']
        entidad = request.form['entidad']
        vinculo = request.form['vinculo']
        unidad = request.form['unidad']
        sede = request.form['sede']

        record = {
            "evento": evento,
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
            return render_template('registro_eventos.html', eventos=eventos, tipos_documento=tipos_documento, paises=paises, vinculos=vinculos, unidades=unidades, sedes=sedes, record=record, error=error)

        # Aquí puedes agregar la lógica para almacenar los datos en una base de datos

    # Renderiza el formulario sin errores
    return render_template('registro_eventos.html', eventos=eventos, tipos_documento=tipos_documento, paises=paises, vinculos=vinculos, unidades=unidades, sedes=sedes, record=record, error=error)

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