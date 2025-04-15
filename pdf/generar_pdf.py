import os
import base64
import fitz  # PyMuPDF
from flask import abort, send_file
from werkzeug.utils import secure_filename

from pdf.coordenadas import coordenadas
from api.dni_api import consultar_dni
from api.mailer import enviar_correo_con_adjuntos

TEMPLATE_PDF_PATH = "plantilla_A4.pdf"

def generar_pdf(form_data, archivos):
    # form_data = request.form.to_dict()
    # archivos = request.files.getlist('adjuntos')
    lista_adjuntos = []

    # Guardar adjuntos en base64
    for archivo in archivos:
        if archivo and archivo.filename:
            filename = secure_filename(archivo.filename)
            content_base64 = base64.b64encode(archivo.read()).decode('utf-8')
            lista_adjuntos.append({
                "filename": filename,
                "content": content_base64,
                "type": archivo.content_type or "application/octet-stream"
            })

    # Consultar API DNI si se ingresó
    if form_data.get('dni'):
        datos_dni = consultar_dni(form_data['dni'])
        if datos_dni:
            form_data.update({
                'nombre': datos_dni.get('nombres'),
                'apellido': f"{datos_dni.get('ape_paterno')} {datos_dni.get('ape_materno')}".strip(),
                'direccion_h1': datos_dni.get('domiciliado', {}).get('direccion'),
                'distrito': datos_dni.get('domiciliado', {}).get('distrito'),
                'provincia': datos_dni.get('domiciliado', {}).get('provincia'),
                'departamento': datos_dni.get('domiciliado', {}).get('departamento'),
            })

    if not os.path.exists(TEMPLATE_PDF_PATH):
        abort(500, "No se encuentra la plantilla PDF")

    try:
        doc = fitz.open(TEMPLATE_PDF_PATH)
        tipo_persona = form_data.get("tipo_persona", "natural").lower()
        campos = coordenadas.get(tipo_persona, {})

        print(f"📄 Total de páginas del PDF: {len(doc)}")

        for key, val in form_data.items():
            if key in campos and val:
                campo = campos[key]
                page = campo["page"]

                if page >= len(doc):
                    print(f"⚠️ Página {page} no existe para el campo '{key}'")
                    continue

                try:
                    if key == "firma_img":
                        image_data = base64.b64decode(val.split(',')[1])
                        rect = fitz.Rect(
                            campo["pos"][0], campo["pos"][1],
                            campo["pos"][0] + 150, campo["pos"][1] + 100
                        )
                        doc[page].insert_image(rect, stream=image_data)
                    else:
                        doc[page].insert_text(
                            fitz.Point(*campo["pos"]),
                            str(val),
                            fontsize=campo.get("size", 11),
                            fontname=campo.get("font", "helv")
                        )
                except Exception as e:
                    print(f"❌ Error insertando '{key}': {e}")

        # Guardar PDF generado
        placa = form_data.get('placa', 'vehiculo').replace('/', '-').replace(' ', '_')
        nombre_pdf = f"TUPA_12_-_{placa.upper()}.pdf"
        doc.save(nombre_pdf, garbage=4, deflate=True)
        doc.close()

    except Exception as e:
        abort(500, f"Error creando el PDF: {e}")

    try:
        with open(nombre_pdf, "rb") as f:
            lista_adjuntos.append({
                "filename": nombre_pdf,
                "content": base64.b64encode(f.read()).decode('utf-8'),
                "type": "application/pdf"
            })
    except Exception as e:
        abort(500, f"Error leyendo el PDF generado: {e}")

    # Envío de correo si hay destinatario
    if form_data.get("correo"):
        try:
            enviar_correo_con_adjuntos(form_data["correo"], lista_adjuntos)
        except Exception as e:
            print("⚠️ Error al enviar el correo:", e)

    # return send_file(nombre_pdf, as_attachment=True, download_name=nombre_pdf)
    return nombre_pdf, lista_adjuntos

