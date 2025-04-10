import os
import base64
import fitz  # PyMuPDF
from flask import Flask, request, render_template, send_file, after_this_request, abort
from coordenadas import coordenadas
from dotenv import load_dotenv
import resend

from dni_api import consultar_dni  # Importa la función desde tu módulo separado

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")
# --- INICIALIZACIÓN DE FLASK ---


app = Flask(__name__)

# --- CONFIGURACIÓN ---
TEMPLATE_PDF_PATH = "plantilla_A4.pdf"
OUTPUT_PDF_PATH = "temp_output.pdf"

# --- COORDENADAS PARA INSERTAR TEXTO EN EL PDF ---
# Las coordenadas se definen en el archivo coordenadas.py

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    form_data = request.form.to_dict()

    # --- Consulta a API DNI ---
    dni_ingresado = form_data.get('dni')
    if dni_ingresado:
        datos_dni = consultar_dni(dni_ingresado)
        if datos_dni:
            form_data['nombre'] = datos_dni.get('nombres', form_data.get('nombre'))
            form_data['apellido'] = f"{datos_dni.get('ape_paterno', '')} {datos_dni.get('ape_materno', '')}".strip()
            form_data['direccion_h1'] = datos_dni.get('domiciliado', {}).get('direccion', form_data.get('direccion_h1'))
            form_data['distrito'] = datos_dni.get('domiciliado', {}).get('distrito', form_data.get('distrito'))
            form_data['provincia'] = datos_dni.get('domiciliado', {}).get('provincia', form_data.get('provincia'))
            form_data['departamento'] = datos_dni.get('domiciliado', {}).get('departamento', form_data.get('departamento'))
            form_data['ubigeo'] = datos_dni.get('domiciliado', {}).get('ubigeo', form_data.get('ubigeo'))

    # --- Abrir PDF plantilla ---
    if not os.path.exists(TEMPLATE_PDF_PATH):
        print(f"Error: No se encuentra la plantilla '{TEMPLATE_PDF_PATH}'")
        abort(500, "Error interno del servidor: Falta el archivo PDF base.")

    try:
        doc = fitz.open(TEMPLATE_PDF_PATH)
    except Exception as e:
        print(f"Error abriendo PDF: {e}")
        abort(500, f"No se pudo abrir el PDF base: {e}")

    # --- Insertar datos en el PDF ---
    print("Datos a insertar:", form_data)
    for key, value in form_data.items():
        if key in coordenadas and value:
            info = coordenadas[key]
            page_num = info['page']
            if 0 <= page_num < len(doc):
                if key == 'firma_img':
                    try:
                        img_data = base64.b64decode(value.split(',')[1])
                        img_rect = fitz.Rect(info['pos'][0], info['pos'][1], info['pos'][0] + 150, info['pos'][1] + 100)
                        doc[page_num].insert_image(img_rect, stream=img_data)
                    except Exception as e:
                        print(f"No se pudo insertar la firma: {e}")
                else:
                    pos = fitz.Point(*info['pos'])
                    try:
                        doc[page_num].insert_text(
                            pos,
                            str(value),
                            fontsize=info.get('size', 11),
                            fontname=info.get('font', 'helv')
                        )
                    except Exception as e:
                        print(f"No se pudo insertar '{key}': {e}")
            else:
                print(f"Página {page_num} inválida para '{key}'")

    # --- Guardar PDF generado ---
    try:
        doc.save(OUTPUT_PDF_PATH, garbage=4, deflate=True)
        doc.close()
    except Exception as e:
        print(f"No se pudo guardar el PDF: {e}")
        try: doc.close()
        except: pass
        abort(500, f"Error guardando el PDF final: {e}")

    # --- Enviar por correo si se proporcionó un correo ---
    correo_destinatario = form_data.get("correo")
    if correo_destinatario:
        try:
            enviar_pdf_por_correo(correo_destinatario, OUTPUT_PDF_PATH)
        except Exception as e:
            print(f"Error al enviar correo: {e}")


    @after_this_request
    def eliminar_archivo(response):
        try:
            if os.path.exists(OUTPUT_PDF_PATH):
                os.remove(OUTPUT_PDF_PATH)
                print(f"Eliminado: {OUTPUT_PDF_PATH}")
        except Exception as e:
            app.logger.error("Error eliminando archivo: %s", e)
        return response


    try:
        
        return send_file(OUTPUT_PDF_PATH, as_attachment=True, download_name='documento_generado.pdf')
    except Exception as e:
        print(f"Error al enviar archivo: {e}")
        abort(500, f"No se pudo enviar el PDF generado: {e}")

@app.route('/api/dni/<dni>')
def api_dni(dni):
    datos = consultar_dni(dni)
    if datos:
        return {
            "success": True,
            **datos
        }
    else:
        return {'success': False}, 404


def enviar_pdf_por_correo(destinatario, archivo_pdf):
    with open(archivo_pdf, "rb") as f:
        contenido_pdf = f.read()
        contenido_base64 = base64.b64encode(contenido_pdf).decode("utf-8")

    respuesta = resend.Emails.send({
        "from": "Carla<onboarding@resend.dev>",  # este debe estar verificado en Resend
        "to": [destinatario],
        "subject": "Documento generado por el formulario",
        "html": "<p>Adjunto el PDF solicitado.</p>",
        "attachments": [
            {
                "filename": "documento_generado.pdf",
                "content": contenido_base64,
                "type": "application/pdf"
            }
        ]
    })

    print("Respuesta de Resend:", respuesta)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')