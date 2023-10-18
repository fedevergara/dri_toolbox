# listas.py
eventos = []
ecards = []

def get_eventos():
    return eventos, ecards

tipos_documento = ["Tarjeta de Identidad", "Cédula de Ciudadanía", "Pasaporte", "Documento Extranjero", "Cédula de extranjería"]
paises = ["Argentina", "Brasil", "Chile", "Colombia", "México", "Perú", "España", "Estados Unidos", "Canadá"]
vinculos = ["Estudiante de pregrado", "Estudiante de posgrado", "Profesor/Investigador", "Personal Administrativo", "Egresado", "Externo"]
unidades = [
    "Corporación Académica Ambiental",
    "Corporación Académica de Ciencias Básicas Biomédicas",
    "Corporación Académica para el Estudio de Patologías Tropicales",
    "Dirección de Bienestar Universitario",
    "Dirección de Comunicaciones",
    "Dirección de Planeación y Desarrollo Institucional",
    "Dirección de Posgrado",
    "Dirección de Regionalización",
    "Dirección de Relaciones Internacionales",
    "Dirección Jurídica",
    "Escuela de Idiomas",
    "Escuela de Microbiología",
    "Escuela de Nutrición y Dietética",
    "Escuela Interamericana de Bibliotecología",
    "Facultad de Artes",
    "Facultad de Ciencias Agrarias",
    "Facultad de Ciencias Económicas",
    "Facultad de Ciencias Exactas y Naturales",
    "Facultad de Ciencias Farmacéuticas y Alimentarias",
    "Facultad de Ciencias Sociales y Humanas",
    "Facultad de Comunicaciones y Filología",
    "Facultad de Derecho y Ciencias Políticas",
    "Facultad de Educación",
    "Facultad de Enfermería",
    "Facultad de Ingeniería",
    "Facultad de Medicina",
    "Facultad de Odontología",
    "Facultad Nacional de Salud Pública",
    "Instituto de Estudios Políticos",
    "Instituto de Estudios Regionales",
    "Instituto de Filosofía",
    "Instituto Universitario de Educación Física y Deporte",
    "Oficina de Auditoría Institucional",
    "Rectoría",
    "Secretaría General",
    "Unidad de Asuntos Disciplinarios",
    "Vicerrectoría Administrativa",
    "Vicerrectoría de Docencia",
    "Vicerrectoría de Extensión",
    "Vicerrectoría de Investigación",
    "Vicerrectoría General"]
sedes = [
    "Campus Amalfi",
    "Campus Andes",
    "Campus Apartadó",
    "Campus El Carmen de Viboral",
    "Campus Carepa",
    "Campus Caucasia",
    "Campus La Pintada",
    "Campus Medellín",
    "Campus Puerto Berrío",
    "Campus Segovia - Remedios",
    "Campus Santa Fe de Antioquia",
    "Campus Sonsón",
    "Campus Turbo",
    "Campus Yarumal"
]