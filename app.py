import os
import base64
import fitz  # PyMuPDF
from flask import Flask, request, render_template, send_file, abort, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
from dotenv import load_dotenv
import resend

from coordenadas import coordenadas
from dni_api import consultar_dni  # Importa la función desde tu módulo separado

from ruc_api import consultar_ruc, consultar_representante_legal

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

app = Flask(__name__)

TEMPLATE_PDF_PATH = "plantilla_A4.pdf"
OUTPUT_PDF_PATH = "temp_output.pdf"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit_form():
    # 1. Tomamos los datos de texto
    form_data = request.form.to_dict()

    # 2. Capturamos los archivos 'adjuntos'
    archivos = request.files.getlist('adjuntos')
    lista_adjuntos = []
    for archivo in archivos:
        if archivo and archivo.filename:
            filename = secure_filename(archivo.filename)
            file_bytes = archivo.read()
            content_base64 = base64.b64encode(file_bytes).decode('utf-8')
            adjunto = {
                "filename": filename,
                "content": content_base64,
                "type": archivo.content_type or "application/octet-stream"
            }
            lista_adjuntos.append(adjunto)

    # 3. Consulta API DNI
    dni_ingresado = form_data.get('dni')
    if dni_ingresado:
        datos_dni = consultar_dni(dni_ingresado)
        if datos_dni:
            form_data['nombre'] = datos_dni.get('nombres', form_data.get('nombre'))
            form_data['apellido'] = f"{datos_dni.get('ape_paterno', '')} {datos_dni.get('ape_materno', '')}".strip()
            domi = datos_dni.get('domiciliado', {})
            form_data['direccion_h1'] = domi.get('direccion', form_data.get('direccion_h1'))
            form_data['distrito']     = domi.get('distrito', form_data.get('distrito'))
            form_data['provincia']    = domi.get('provincia', form_data.get('provincia'))
            form_data['departamento'] = domi.get('departamento', form_data.get('departamento'))
            form_data['ubigeo']       = domi.get('ubigeo', form_data.get('ubigeo'))



    # 4. Generar PDF
    if not os.path.exists(TEMPLATE_PDF_PATH):
        print(f"No se encuentra la plantilla '{TEMPLATE_PDF_PATH}'")
        abort(500, "No se encuentra la plantilla PDF")

    try:
        doc = fitz.open(TEMPLATE_PDF_PATH)
        for key, value in form_data.items():
            if key in coordenadas and value:
                info = coordenadas[key]
                page_num = info['page']
                if 0 <= page_num < len(doc):
                    if key == 'firma_img':
                        # Insertar firma
                        try:
                            sig_data = base64.b64decode(value.split(',')[1])
                            sig_rect = fitz.Rect(info['pos'][0], info['pos'][1],
                                                 info['pos'][0] + 150, info['pos'][1] + 100)
                            doc[page_num].insert_image(sig_rect, stream=sig_data)
                        except Exception as e:
                            print("Error al insertar firma:", e)
                    else:
                        # Insertar texto normal
                        try:
                            doc[page_num].insert_text(
                                fitz.Point(*info['pos']),
                                str(value),
                                fontsize=info.get('size', 11),
                                fontname=info.get('font', 'helv')
                            )
                        except Exception as e:
                            print(f"No se pudo insertar '{key}': {e}")
        doc.save(OUTPUT_PDF_PATH, garbage=4, deflate=True)
        doc.close()
    except Exception as e:
        print("Error creando el PDF:", e)
        abort(500, "Error creando PDF")

    # 5. Añadir el PDF generado a la lista de adjuntos
    try:
        with open(OUTPUT_PDF_PATH, "rb") as f:
            pdf_data = f.read()
            pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')
            lista_adjuntos.append({
                "filename": "documento_generado.pdf",
                "content": pdf_b64,
                "type": "application/pdf"
            })
    except Exception as e:
        print("Error al leer el PDF final:", e)
        abort(500, "Error interno al leer el PDF")

    # 6. Enviar correo (solo 1 destinatario) con TODOS los adjuntos
    correo_destinatario = form_data.get("correo")
    if correo_destinatario:
        try:
            enviar_correo_con_adjuntos(correo_destinatario, lista_adjuntos)
        except Exception as e:
            print("Error enviando el correo:", e)

    # 7. Devolver PDF al usuario
    try:
        return send_file(OUTPUT_PDF_PATH, as_attachment=True, download_name='documento_generado.pdf')
    except Exception as e:
        print("Error al enviar el PDF al usuario:", e)
        abort(500, "Error al enviar el PDF")


@app.after_request
def limpiar_pdf_temp(response):
    """Elimina el PDF temporal después de la respuesta."""
    if os.path.exists(OUTPUT_PDF_PATH):
        try:
            os.remove(OUTPUT_PDF_PATH)
            print("PDF temporal eliminado")
        except Exception as e:
            print("No se pudo eliminar PDF temporal:", e)
    return response

@app.route("/api/ruc/<ruc>", methods=["GET"])
def api_ruc(ruc):
    datos_ruc = consultar_ruc(ruc)
    datos_rep = consultar_representante_legal(ruc)

    if datos_ruc.get("success") and datos_rep.get("success"):
        representante = datos_rep.get("data", [])
        if representante:
            # Solo tomamos el primero si hay varios
            datos_ruc["representante_legal"] = representante[0].get("nombre", "")
            datos_ruc["dni_representante"] = representante[0].get("dni", "")
        else:
            datos_ruc["representante_legal"] = ""
            datos_ruc["dni_representante"] = ""

    return jsonify({"success": True, "datos": datos_ruc})


@app.route('/api/dni/<dni>')
def api_dni(dni):
    datos = consultar_dni(dni)
    if datos:
        return {"success": True, **datos}
    return {"success": False}, 404


def enviar_correo_con_adjuntos(destinatario, lista_adjuntos):
    """Envía un correo a 'destinatario' con cualquier cantidad de adjuntos."""
    respuesta = resend.Emails.send({
        "from": "onboarding@resend.dev",  # Verificar en Resend
        # "to": [destinatario],
        # "to": "jose.quenta@sanipes.gob.pe",
        "to": "soycargototal@gmail.com",
        
        "subject": "Formulario con múltiples adjuntos",
        "html": "<p>Hola, te enviamos tu formulario y archivos adjuntos.</p>",
        "attachments": lista_adjuntos
    })
    print("Respuesta de Resend:", respuesta)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
