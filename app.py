import os
from flask import Flask, request, render_template, send_file, abort, jsonify
from dotenv import load_dotenv

from pdf.coordenadas import coordenadas
from api.dni_api import consultar_dni
from api.ruc_api import consultar_ruc, consultar_representante_legal
from pdf.generar_pdf import generar_pdf
from api.mailer import enviar_correo_con_adjuntos

load_dotenv()

app = Flask(__name__)
TEMPLATE_PDF_PATH = "plantilla_A4.pdf"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit_form():
    form_data = request.form.to_dict()
    archivos = request.files.getlist('adjuntos')

    # Enriquecer con datos del DNI
    if dni := form_data.get('dni'):
        datos_dni = consultar_dni(dni)
        if datos_dni:
            form_data['nombre'] = datos_dni.get('nombres', form_data.get('nombre'))
            form_data['apellido'] = f"{datos_dni.get('ape_paterno', '')} {datos_dni.get('ape_materno', '')}".strip()
            domi = datos_dni.get('domiciliado', {})
            form_data['direccion_h1'] = domi.get('direccion', form_data.get('direccion_h1'))
            form_data['distrito'] = domi.get('distrito', form_data.get('distrito'))
            form_data['provincia'] = domi.get('provincia', form_data.get('provincia'))
            form_data['departamento'] = domi.get('departamento', form_data.get('departamento'))

    try:
        pdf_generado, adjuntos = generar_pdf(form_data, archivos)
    except Exception as e:
        print("❌ Error general al generar PDF:", e)
        abort(500, "Error interno en la generación del PDF")

    # Enviar correo si hay destinatario
    if correo := form_data.get("correo"):
        try:
            enviar_correo_con_adjuntos(correo, adjuntos)
        except Exception as e:
            print("❌ Error al enviar el correo:", e)

    # Descargar PDF generado
    try:
        return send_file(pdf_generado, as_attachment=True, download_name=pdf_generado)
    except Exception as e:
        print("❌ Error al enviar el archivo:", e)
        abort(500, "No se pudo enviar el PDF al usuario")


@app.route("/api/ruc/<ruc>")
def api_ruc(ruc):
    datos_ruc = consultar_ruc(ruc)
    datos_rep = consultar_representante_legal(ruc)

    if datos_ruc.get("success") and datos_rep.get("success"):
        rep = datos_rep.get("data", [])
        datos_ruc["representante_legal"] = rep[0].get("nombre", "") if rep else ""
        datos_ruc["dni_representante"] = rep[0].get("dni", "") if rep else ""

    return jsonify({"success": True, "datos": datos_ruc})


@app.route("/api/dni/<dni>")
def api_dni(dni):
    datos = consultar_dni(dni)
    return {"success": True, **datos} if datos else {"success": False}, 404


@app.after_request
def limpiar_pdf_temp(response):
    for archivo in os.listdir("."):
        if archivo.startswith("TUPA_12_-_") and archivo.endswith(".pdf"):
            try:
                os.remove(archivo)
                print(f"🧹 PDF temporal eliminado: {archivo}")
            except Exception as e:
                print(f"❌ No se pudo eliminar '{archivo}': {e}")
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
