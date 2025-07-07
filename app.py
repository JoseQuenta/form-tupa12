import os
from flask import Flask, request, render_template, send_file, abort, jsonify
from dotenv import load_dotenv

# from supabase import create_client, Client

from pdf.generar_pdf import generar_pdf
from services.persona_service import PersonaService
from services.empresa_service import EmpresaService

load_dotenv()

app = Flask(__name__)

# SUPABASE_URL = "https://qxeiglgklzejwayczsxs.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4ZWlnbGdrbHplandheWN6c3hzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5MzI4MDIsImV4cCI6MjA2MzUwODgwMn0.kCnTz6VVvm71uPZNV7qhZ7y3EBgm9y3rogXju9BCGsA"
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
    """Página principal del formulario."""
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_form():
    form_data = request.form.to_dict()
    archivos = request.files.getlist("adjuntos")

    # --- Modelo limpio para Supabase ---
    data_to_save = {}
    # Copiar campos básicos
    campos_basicos = [
        "tipo_persona",
        "dni",
        "nombre",
        "apellido",
        "direccion_h1",
        "distrito",
        "provincia",
        "departamento",
        "ruc",
        "razon_social",
        "rep_legal",
        "dni_rep_legal",
        "direccion_jur",
        "distrito_jur",
        "provincia_jur",
        "departamento_jur",
        "telefono",
        "correo",
        "placa",
        "carga_util",
        "tipo_carroceria",
        "tipo_carroceria_otro",
        "numero_pago",
        "fecha_pago",
        "lugar_auditoria",
    ]
    for campo in campos_basicos:
        data_to_save[campo] = form_data.get(campo)
    data_to_save["sin_correo"] = bool(form_data.get("sinCorreo"))
    data_to_save["fecha_envio"] = None  # Supabase puede poner default now()
    if "firma_img" in form_data:
        data_to_save["firma_img"] = form_data["firma_img"]

    # --- Si es persona jurídica, obtener datos pulverizados del representante legal ---
    if form_data.get("tipo_persona") == "juridica" and form_data.get("dni_rep_legal"):
        resultado_dni = PersonaService.buscar_por_dni(form_data["dni_rep_legal"])
        if resultado_dni.get("success"):
            datos_rep = resultado_dni["data"]
            data_to_save["rep_nombres"] = datos_rep.get("nombres")
            data_to_save["rep_ape_paterno"] = datos_rep.get("apellido_paterno")
            data_to_save["rep_ape_materno"] = datos_rep.get("apellido_materno")
            # Nombre completo ordenado
            nombre_completo = f"{datos_rep.get('nombres', '')} {datos_rep.get('apellido_paterno', '')} {datos_rep.get('apellido_materno', '')}".strip()
            data_to_save["rep_nombre_completo"] = nombre_completo
            # También lo ponemos en form_data para el PDF
            form_data["rep_nombre_completo"] = nombre_completo
        else:
            data_to_save["rep_nombres"] = None
            data_to_save["rep_ape_paterno"] = None
            data_to_save["rep_ape_materno"] = None
            data_to_save["rep_nombre_completo"] = None
            form_data["rep_nombre_completo"] = None
    else:
        data_to_save["rep_nombres"] = None
        data_to_save["rep_ape_paterno"] = None
        data_to_save["rep_ape_materno"] = None
        data_to_save["rep_nombre_completo"] = None
        form_data["rep_nombre_completo"] = None

    # Guardar en Supabase
    # try:
    #     supabase.table("formularios_tupa12").insert(data_to_save).execute()
    # except Exception as e:
    #     print("❌ Error al guardar en Supabase:", e)
    #     # No abortar, solo loguear

    try:
        # Generar PDF usando los datos ya procesados
        pdf_generado, adjuntos = generar_pdf(form_data, archivos)

        # Construir la ruta absoluta del archivo PDF
        pdf_path = os.path.abspath(pdf_generado)

        # Verificar que el archivo existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF generado no existe: {pdf_path}")

        # Enviar archivo al usuario
        return send_file(pdf_path, as_attachment=True, download_name=pdf_generado)

    except Exception as e:
        print(f"❌ Error al generar PDF: {e}")
        import traceback

        traceback.print_exc()  # Esto ayudará a ver el error completo en los logs
        abort(500, f"Error interno en la generación del PDF: {str(e)}")


@app.route("/api/ruc/<ruc>")
def api_ruc(ruc):
    """API endpoint para consultar datos de RUC."""
    try:
        # Usar el servicio para obtener los datos
        resultado = EmpresaService.buscar_por_ruc(ruc)

        if resultado["success"]:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404

    except Exception as e:
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500


@app.route("/api/dni/<dni>")
def api_dni(dni):
    """API endpoint para consultar datos de DNI."""
    try:
        # Usar el servicio para obtener los datos
        resultado = PersonaService.buscar_por_dni(dni)

        if resultado["success"]:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404

    except Exception as e:
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500


@app.route("/api/health")
def health_check():
    """Endpoint para verificar el estado de la aplicación."""
    return jsonify(
        {
            "status": "OK",
            "message": "Aplicación funcionando correctamente",
            "endpoints": {
                "ruc": "/api/ruc/<ruc>",
                "dni": "/api/dni/<dni>",
                "submit": "/submit (POST)",
            },
        }
    )


@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404."""
    return jsonify({"success": False, "message": "Recurso no encontrado"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500."""
    # Durante desarrollo, mostrar el error real
    if hasattr(error, "description") and error.description:
        return jsonify({"success": False, "message": str(error.description)}), 500
    return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@app.after_request
def limpiar_pdf_temp(response):
    """Limpia archivos PDF temporales después de cada request."""
    try:
        archivos_eliminados = 0
        for archivo in os.listdir("."):
            if archivo.startswith("TUPA_12_-_") and archivo.endswith(".pdf"):
                try:
                    os.remove(archivo)
                    archivos_eliminados += 1
                except Exception:
                    pass  # Ignorar errores de eliminación

    except Exception:
        pass  # Ignorar errores de limpieza

    return response


if __name__ == "__main__":
    print("🚀 Iniciando aplicación TUPA 12...")
    app.run(debug=False, host="0.0.0.0", port=5000)
