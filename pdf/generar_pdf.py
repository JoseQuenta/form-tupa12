from datetime import datetime
import os
import base64
import fitz  # PyMuPDF
from flask import abort, send_file
from werkzeug.utils import secure_filename

from pdf.coordenadas import coordenadas
from api.dni_api import consultar_dni
from api.ruc_api import consultar_ruc, consultar_representante_legal
from api.mailer import enviar_correo_con_adjuntos

TEMPLATE_PDF_PATH = "plantilla_A4.pdf"

def sobrescribir_si_vacio(data, campo, valor):
    if not data.get(campo):  # Si está vacío, None o ""
        data[campo] = valor

def generar_pdf(form_data, archivos):
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

    tipo_persona = form_data.get("tipo_persona", "natural").lower()

    # Enriquecer datos de PN (persona natural)
    if tipo_persona == "natural" and form_data.get('dni'):
        datos_dni = consultar_dni(form_data['dni'])
        if datos_dni:
            sobrescribir_si_vacio(form_data, 'nombre', datos_dni.get('nombres'))
            apellido = f"{datos_dni.get('ape_paterno')} {datos_dni.get('ape_materno')}".strip()
            sobrescribir_si_vacio(form_data, 'apellido', apellido)
            dom = datos_dni.get('domiciliado', {})
            sobrescribir_si_vacio(form_data, 'direccion_h1', dom.get('direccion'))
            sobrescribir_si_vacio(form_data, 'distrito', dom.get('distrito'))
            sobrescribir_si_vacio(form_data, 'provincia', dom.get('provincia'))
            sobrescribir_si_vacio(form_data, 'departamento', dom.get('departamento'))

    # Enriquecer datos de PJ (persona jurídica)
    elif tipo_persona == "juridica" and form_data.get('ruc'):
        datos_ruc = consultar_ruc(form_data['ruc'])
        datos_rep = consultar_representante_legal(form_data['ruc'])

        if datos_ruc.get("success"):
            sobrescribir_si_vacio(form_data, 'razon_social', datos_ruc.get('razon_social'))
            sobrescribir_si_vacio(form_data, 'direccion_jur', datos_ruc.get('direccion'))
            sobrescribir_si_vacio(form_data, 'distrito_jur', datos_ruc.get('distrito'))
            sobrescribir_si_vacio(form_data, 'provincia_jur', datos_ruc.get('provincia'))
            sobrescribir_si_vacio(form_data, 'departamento_jur', datos_ruc.get('departamento'))

        if datos_rep.get("success") and datos_rep.get("data"):
            rep = datos_rep["data"][0]
            sobrescribir_si_vacio(form_data, 'rep_legal', rep.get("nombre"))
            sobrescribir_si_vacio(form_data, 'dni_rep_legal', rep.get("dni"))

    # Verificar existencia de plantilla
    if not os.path.exists(TEMPLATE_PDF_PATH):
        abort(500, "No se encuentra la plantilla PDF")

    try:
        doc = fitz.open(TEMPLATE_PDF_PATH)
        campos = coordenadas.get(tipo_persona, {})

        print(f"📄 Total de páginas del PDF: {len(doc)}")

        # 💡 Unir nombres y apellidos para uso personalizado
        if tipo_persona == "natural" and form_data.get("nombre") and form_data.get("apellido"):
            form_data["nombre_completo"] = f"{form_data['nombre']} {form_data['apellido']}"
            form_data["nombre_completo2"] = form_data["nombre_completo"].title()
            
            
            
        
        form_data["direccion_h2"] = form_data.get("direccion_h1")

        # 💬 Mensaje personalizado
        placa = form_data.get("placa", "").upper()
        lugar_auditoria = form_data.get("lugar_auditoria").title()
        form_data["fundamentos_de_solicitud1"] = f"Solicito la obtención del Protocolo Técnico de Habilitación Sanitaria de mi transporte de placa {placa}"
        
        form_data["fundamentos_de_solicitud2"] = f"Solicito pasar auditoria en la ciudad de {lugar_auditoria} y recibir el PTH en mi correo electrónico."
        
        form_data["titulo"] = f"TUPA 12 - {placa}"
        form_data["mensaje_requisitos1"] = "Solicitud - Formulario TUPA 12"
        form_data["mensaje_requisitos2"] = "Copia de tarjeta de propiedad del vehículo"
        form_data["mensaje_requisitos3"] = "Programa BPM"
        form_data["mensaje_requisitos4"] = "Programa HS"
        form_data["mensaje_requisitos5"] = "Voucher de pago por S/ 550.90"

        if tipo_persona == "natural":
            form_data["check_natural"] = "X"
        elif tipo_persona == "juridica":
            form_data["check_juridica"] = "X"
            
        form_data['dni2'] = form_data.get('dni')
        
        form_data['rep_legal2'] = form_data.get('rep_legal')
        form_data['dni_rep_legal2'] = form_data.get('dni_rep_legal')
        
        form_data['fecha_hoy'] = datetime.now().strftime("%d/%m/%Y")
        
        # Insertar en el PDF
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
        nombre_archivo = f"TUPA_12_-_{placa.replace('/', '-').replace(' ', '_')}.pdf"
        doc.save(nombre_archivo, garbage=4, deflate=True)
        doc.close()

    except Exception as e:
        abort(500, f"Error creando el PDF: {e}")

    # Adjuntar PDF
    try:
        with open(nombre_archivo, "rb") as f:
            lista_adjuntos.append({
                "filename": nombre_archivo,
                "content": base64.b64encode(f.read()).decode('utf-8'),
                "type": "application/pdf"
            })
    except Exception as e:
        abort(500, f"Error leyendo el PDF generado: {e}")

    # # Envío opcional (comentado)
    # if form_data.get("correo"):
    #     try:
    #         enviar_correo_con_adjuntos(form_data["correo"], lista_adjuntos)
    #     except Exception as e:
    #         print("⚠️ Error al enviar el correo:", e)

    return nombre_archivo, lista_adjuntos
