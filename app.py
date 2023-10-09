from flask import Flask, request, render_template
from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired


# Create Flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fede'

# Create a from class
class mobility_form(FlaskForm):
    nombre_diligencia = wtforms.StringField("", validators=[DataRequired()])
    correo_diligencia = wtforms.EmailField("", validators=[DataRequired()])
    telefono_diligencia = wtforms.TelField("")

    año = wtforms.RadioField("año", choices=[('2022','2022'), ('2023','2023'), ('2024','2024')], validators=[DataRequired()], render_kw={'class': 'form-check-input'})
    semestre = wtforms.RadioField("semestre", choices=[(1, '1'), (2, '2')], validators=[DataRequired()], render_kw={'class': 'form-check-input'})
    modalidad = wtforms.RadioField("modalidad", choices=[('presencial', 'Presencial'), ('virtual', 'Virtual')], validators=[DataRequired()], render_kw={'class': 'form-check-input'})
    categoria = wtforms.RadioField("categoria", choices=[('internacional', 'Internacional'), ('nacional', 'Nacional')], validators=[DataRequired()], render_kw={'class': 'form-check-input'})

    enviar = wtforms.SubmitField("Enviar")

# Create a route
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    nombre_diligencia = None
    correo_diligencia = None
    telefono_diligencia = None
    año = None
    semestre = None
    modalidad = None
    categoria = None

    record = None
    form = mobility_form()
    
    if form.validate_on_submit():
        nombre_diligencia = form.nombre_diligencia.data
        correo_diligencia = form.correo_diligencia.data
        telefono_diligencia = form.telefono_diligencia.data
        año = form.año.data
        semestre = form.semestre.data
        modalidad = form.modalidad.data
        categoria = form.categoria.data
        
        record = {
            "nombre": nombre_diligencia,
            "correo": correo_diligencia,
            "telefono": telefono_diligencia,
            "año": año,
            "semestre": semestre,
            "modalidad": modalidad,
            "categoria": categoria
        }
        
        form.nombre_diligencia.data = ""
        form.correo_diligencia.data = ""
        form.telefono_diligencia.data = ""
        form.año.data = ""
        form.semestre.data = ""
        form.modalidad.data = ""
        form.categoria.data = ""

    return render_template("registro.html",
                            nombre_diligencia=nombre_diligencia,
                            correo_diligencia=correo_diligencia,
                            telefono_diligencia=telefono_diligencia,
                            año=año,
                            semestre=semestre,
                            modalidad=modalidad,
                            categoria=categoria,
                            form=form,
                            record=record)

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