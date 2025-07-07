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

from models.persona import Persona
from models.empresa import Empresa
from models.representante import Representante


TEMPLATE_PDF_PATH = "plantilla_A4.pdf"


def sobrescribir_si_vacio(data, campo, valor):
    """Sobrescribe un campo en data solo si está vacío o es None."""
    if not data.get(campo):
        data[campo] = valor


def insertar_texto_adaptado(doc, campo, texto):
    """Inserta texto en el PDF adaptando el tamaño según la longitud."""
    texto = str(texto) if texto else ""
    pagina = campo["page"]
    punto = fitz.Point(*campo["pos"])
    tamano_base = campo.get("size", 11)
    longitud_limite = campo.get("longitud", 40)
    tamano_para_largo = campo.get("size_long", tamano_base - 1)
    fontsize = tamano_para_largo if len(texto) > longitud_limite else tamano_base

    doc[pagina].insert_text(
        punto, texto, fontsize=fontsize, fontname=campo.get("font", "helv")
    )


def procesar_persona_natural(form_data):
    """Procesa datos de persona natural usando la API de Factiliza."""
    dni = form_data.get("dni")
    if not dni:
        return

    print(f"🔍 Consultando DNI: {dni}")
    datos_dni = consultar_dni(dni)

    if not datos_dni:
        print(f"❌ No se encontraron datos para DNI: {dni}")
        return

    try:
        # Crear objeto Persona
        persona = Persona.from_dict(datos_dni)
        print(f"✅ Persona creada: {persona.nombre_completo}")

        # Sobrescribir campos vacíos en form_data
        sobrescribir_si_vacio(form_data, "nombre", persona.nombres)
        sobrescribir_si_vacio(
            form_data,
            "apellido",
            f"{persona.apellido_paterno} {persona.apellido_materno}".strip(),
        )
        sobrescribir_si_vacio(form_data, "direccion_h1", persona.direccion)
        sobrescribir_si_vacio(form_data, "distrito", persona.distrito)
        sobrescribir_si_vacio(form_data, "provincia", persona.provincia)
        sobrescribir_si_vacio(form_data, "departamento", persona.departamento)

        print(f"📝 Datos completados para persona natural")

    except Exception as e:
        print(f"❌ Error procesando persona natural: {e}")


def procesar_persona_juridica(form_data):
    """Procesa datos de persona jurídica usando la API de Factiliza."""
    ruc = form_data.get("ruc")
    if not ruc:
        return

    print(f"🔍 Consultando RUC: {ruc}")

    # Consultar datos de la empresa
    resultado_ruc = consultar_ruc(ruc)
    if not resultado_ruc.get("success"):
        print(f"❌ Error consultando RUC: {resultado_ruc.get('error')}")
        return

    try:
        # Crear objeto Empresa
        empresa = Empresa.from_dict(resultado_ruc["data"])
        print(f"✅ Empresa creada: {empresa.razon_social}")

        # Sobrescribir campos vacíos en form_data
        sobrescribir_si_vacio(form_data, "razon_social", empresa.razon_social)
        sobrescribir_si_vacio(form_data, "direccion_jur", empresa.direccion)
        sobrescribir_si_vacio(form_data, "distrito_jur", empresa.distrito)
        sobrescribir_si_vacio(form_data, "provincia_jur", empresa.provincia)
        sobrescribir_si_vacio(form_data, "departamento_jur", empresa.departamento)

        print(f"📝 Datos de empresa completados")

    except Exception as e:
        print(f"❌ Error procesando empresa: {e}")
        return

    # Consultar representante legal
    print(f"🔍 Consultando representante legal para RUC: {ruc}")
    resultado_rep = consultar_representante_legal(ruc)

    if not resultado_rep.get("success"):
        print(f"❌ Error consultando representante: {resultado_rep.get('error')}")
        return

    try:
        representantes_data = resultado_rep.get("data", [])
        if representantes_data:
            # Crear objeto Representante
            representante = Representante.from_dict(representantes_data[0])
            print(f"✅ Representante creado: {representante.nombre}")

            # Sobrescribir campos vacíos en form_data
            sobrescribir_si_vacio(form_data, "rep_legal", representante.nombre)
            sobrescribir_si_vacio(
                form_data, "dni_rep_legal", representante.numero_documento
            )

            print(f"📝 Datos del representante completados")
        else:
            print(f"⚠️ No se encontraron representantes para RUC: {ruc}")

    except Exception as e:
        print(f"❌ Error procesando representante: {e}")


def procesar_archivos_adjuntos(archivos):
    """Procesa archivos adjuntos y los convierte a base64."""
    lista_adjuntos = []

    for archivo in archivos:
        if archivo and archivo.filename:
            try:
                filename = secure_filename(archivo.filename)
                content_base64 = base64.b64encode(archivo.read()).decode("utf-8")
                lista_adjuntos.append(
                    {
                        "filename": filename,
                        "content": content_base64,
                        "type": archivo.content_type or "application/octet-stream",
                    }
                )
                print(f"📎 Archivo adjunto procesado: {filename}")
            except Exception as e:
                print(f"❌ Error procesando archivo {archivo.filename}: {e}")

    return lista_adjuntos


def completar_campos_formulario(form_data, tipo_persona):
    """Completa campos calculados del formulario."""
    # Campos comunes
    form_data["fecha_hoy"] = datetime.now().strftime("%d/%m/%Y")
    placa = form_data.get("placa", "").upper()
    form_data["placa2"] = placa
    form_data["placa3"] = placa
    form_data["placa4"] = placa

    # Campos específicos para persona natural
    if tipo_persona == "natural":
        form_data["check_natural"] = "X"
        if form_data.get("nombre") and form_data.get("apellido"):
            nombre_completo = f"{form_data['nombre']} {form_data['apellido']}"
            form_data["nombre_completo"] = nombre_completo
            form_data["nombre_completo2"] = nombre_completo.title()
            form_data["nombre_completo3"] = nombre_completo.title()
            form_data["nombre_completo4"] = nombre_completo.title()

        form_data["dni2"] = form_data.get("dni")

    # Campos específicos para persona jurídica
    elif tipo_persona == "juridica":
        form_data["check_juridica"] = "X"
        form_data["razon_social2"] = form_data.get("razon_social", "").title()
        form_data["razon_social3"] = form_data.get("razon_social", "").title()
        form_data["rep_legal2"] = form_data.get("rep_legal")
        form_data["dni_rep_legal2"] = form_data.get("dni_rep_legal")

    # Campos comunes de dirección
    form_data["direccion_h2"] = form_data.get("direccion_h1")

    # Campos de solicitud
    lugar_auditoria = form_data.get("lugar_auditoria", "").title()
    form_data["fundamentos_de_solicitud1"] = (
        f"Solicito la obtención del Protocolo Técnico de Habilitación Sanitaria de mi transporte de placa {placa}"
    )
    form_data["fundamentos_de_solicitud2"] = (
        f"Solicito pasar auditoria en la ciudad de {lugar_auditoria} y recibir el PTH en mi correo electrónico."
    )
    form_data["titulo"] = f"TUPA 12 - {placa}"

    # Mensajes de requisitos
    form_data["mensaje_requisitos1"] = "Solicitud - Formulario TUPA 12"
    form_data["mensaje_requisitos2"] = "Copia de tarjeta de propiedad del vehículo"
    form_data["mensaje_requisitos3"] = "Programa BPM"
    form_data["mensaje_requisitos4"] = "Programa HS"
    form_data["mensaje_requisitos5"] = "Voucher de pago por S/ 550.90"

    # Procesar tipo de carrocería
    tipo_carroceria = form_data.get("tipo_carroceria", "")
    if tipo_carroceria == "Furgón Isotérmico":
        form_data["check_isotermica"] = "X"
    elif tipo_carroceria == "Furgón Frigorífico":
        form_data["check_fria"] = "X"
    elif tipo_carroceria == "Otros":
        form_data["otros_carroceria"] = form_data.get(
            "tipo_carroceria_otro", ""
        ).strip()

    # Carga útil
    form_data["carga_util_texto"] = form_data.get("carga_util", "").strip()


def generar_pdf(form_data, archivos):
    """Función principal para generar el PDF."""
    print("🚀 Iniciando generación de PDF")

    # Procesar archivos adjuntos
    lista_adjuntos = procesar_archivos_adjuntos(archivos)

    # Determinar tipo de persona
    tipo_persona = form_data.get("tipo_persona", "natural").lower()
    print(f"👤 Tipo de persona: {tipo_persona}")

    # Consultar APIs según el tipo de persona
    if tipo_persona == "natural":
        procesar_persona_natural(form_data)
    elif tipo_persona == "juridica":
        procesar_persona_juridica(form_data)

    # Completar campos del formulario
    completar_campos_formulario(form_data, tipo_persona)

    # Verificar que existe la plantilla
    if not os.path.exists(TEMPLATE_PDF_PATH):
        print(f"❌ No se encuentra la plantilla: {TEMPLATE_PDF_PATH}")
        abort(500, "No se encuentra la plantilla PDF")

    # Generar PDF
    try:
        doc = fitz.open(TEMPLATE_PDF_PATH)
        campos = coordenadas.get(tipo_persona, {})
        print(f"📄 Total de páginas del PDF: {len(doc)}")

        if (
            tipo_persona == "natural"
            and form_data.get("nombre")
            and form_data.get("apellido")
        ):
            form_data["nombre_completo"] = (
                f"{form_data['nombre']} {form_data['apellido']}"
            )
            form_data["nombre_completo2"] = form_data["nombre_completo"].title()
            form_data["nombre_completo3"] = form_data["nombre_completo"].title()
            form_data["nombre_completo4"] = form_data["nombre_completo"].title()

        # NUEVO: Para persona jurídica, usar el nombre completo del representante legal si está disponible
        if tipo_persona == "juridica":
            rep_nombre_completo = form_data.get("rep_nombre_completo")
            if rep_nombre_completo:
                form_data["rep_legal"] = rep_nombre_completo
                form_data["rep_legal2"] = rep_nombre_completo
            else:
                form_data["rep_legal2"] = form_data.get("rep_legal")

        form_data["direccion_h2"] = form_data.get("direccion_h1")
        placa = form_data.get("placa", "").upper()
        lugar_auditoria = form_data.get("lugar_auditoria").title()
        form_data["fundamentos_de_solicitud1"] = (
            f"Solicito la obtención del Protocolo Técnico de Habilitación Sanitaria de mi transporte de placa {placa}"
        )
        form_data["fundamentos_de_solicitud2"] = (
            f"Solicito pasar auditoria en la ciudad de {lugar_auditoria} y recibir el PTH en mi correo electrónico."
        )
        form_data["titulo"] = f"TUPA 12 - {placa}"
        form_data["mensaje_requisitos1"] = "Solicitud - Formulario TUPA 12"
        form_data["mensaje_requisitos2"] = "Copia de tarjeta de propiedad del vehículo"
        form_data["mensaje_requisitos3"] = "Programa BPM"
        form_data["mensaje_requisitos4"] = "Programa HS"
        form_data["mensaje_requisitos5"] = "Voucher de pago por S/ 550.90"
        form_data["placa2"] = form_data.get("placa")
        form_data["placa3"] = form_data.get("placa")
        form_data["placa4"] = form_data.get("placa")

        if tipo_persona == "natural":
            form_data["check_natural"] = "X"
        elif tipo_persona == "juridica":
            form_data["check_juridica"] = "X"

        form_data["dni2"] = form_data.get("dni")
        form_data["rep_legal2"] = form_data.get("rep_legal")
        form_data["dni_rep_legal2"] = form_data.get("dni_rep_legal")
        form_data["fecha_hoy"] = datetime.now().strftime("%d/%m/%Y")

        form_data["razon_social2"] = form_data.get("razon_social", "").title()
        form_data["razon_social3"] = form_data.get("razon_social", "").title()

        # Procesar tipo de carrocería para marcar los checks correctos
        tipo_carroceria = form_data.get("tipo_carroceria", "")

        if tipo_carroceria == "Furgón Isotérmico":
            form_data["check_isotermica"] = "X"
        elif tipo_carroceria == "Furgón Frigorífico":
            form_data["check_fria"] = "X"
        elif tipo_carroceria == "Otros":
            form_data["otros_carroceria"] = form_data.get(
                "tipo_carroceria_otro", ""
            ).strip()

        form_data["carga_util_texto"] = form_data.get("carga_util", "").strip()

        for key, val in form_data.items():
            if key in campos and val:
                campo = campos[key]
                page = campo["page"]

                if page >= len(doc):
                    print(f"⚠️ Página {page} no existe para el campo '{key}'")
                    continue

                try:
                    if key == "firma_img":
                        # Insertar imagen de firma
                        image_data = base64.b64decode(val.split(",")[1])
                        rect = fitz.Rect(
                            campo["pos"][0],
                            campo["pos"][1],
                            campo["pos"][0] + 150,
                            campo["pos"][1] + 100,
                        )
                        doc[page].insert_image(rect, stream=image_data)
                    else:
                        # Insertar texto
                        insertar_texto_adaptado(doc, campo, val)

                    campos_procesados += 1

                except Exception as e:
                    print(f"❌ Error insertando '{key}': {e}")

        print(f"✅ Campos procesados: {campos_procesados}")

        # Guardar PDF
        placa = form_data.get("placa", "").upper()
        nombre_archivo = f"TUPA_12_-_{placa.replace('/', '-').replace(' ', '_')}.pdf"
        doc.save(nombre_archivo, garbage=4, deflate=True)
        doc.close()

        print(f"💾 PDF guardado como: {nombre_archivo}")

    except Exception as e:
        print(f"❌ Error creando el PDF: {e}")
        abort(500, f"Error creando el PDF: {e}")

    # Agregar PDF a lista de adjuntos
    try:
        with open(nombre_archivo, "rb") as f:
            lista_adjuntos.append(
                {
                    "filename": nombre_archivo,
                    "content": base64.b64encode(f.read()).decode("utf-8"),
                    "type": "application/pdf",
                }
            )
        print(f"📎 PDF agregado a adjuntos")
    except Exception as e:
        print(f"❌ Error leyendo el PDF generado: {e}")
        abort(500, f"Error leyendo el PDF generado: {e}")

    # Envío opcional por correo
    if form_data.get("correo"):
        try:
            print(f"📧 Enviando correo a: {form_data['correo']}")
            enviar_correo_con_adjuntos(form_data["correo"], lista_adjuntos, form_data)
            print(f"✅ Correo enviado exitosamente")
        except Exception as e:
            print(f"⚠️ Error al enviar el correo: {e}")

    print(f"🎉 PDF generado exitosamente")
    return nombre_archivo, lista_adjuntos
