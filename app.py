import os
from flask import Flask, request, render_template, send_file, abort, jsonify
from dotenv import load_dotenv

from pdf.generar_pdf import generar_pdf
from services.persona_service import PersonaService
from services.empresa_service import EmpresaService

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    """Página principal del formulario."""
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_form():
    """Procesa el formulario y genera el PDF."""
    try:
        form_data = request.form.to_dict()
        archivos = request.files.getlist("adjuntos")

        print(f"📋 Formulario recibido - Tipo: {form_data.get('tipo_persona')}")
        print(f"📎 Archivos adjuntos: {len(archivos)}")

        # Generar PDF
        pdf_generado, adjuntos = generar_pdf(form_data, archivos)

        print(f"✅ PDF generado exitosamente: {pdf_generado}")

        # Enviar archivo al usuario
        return send_file(pdf_generado, as_attachment=True, download_name=pdf_generado)

    except Exception as e:
        print(f"❌ Error general al generar PDF: {e}")
        abort(500, "Error interno en la generación del PDF")


@app.route("/api/ruc/<ruc>")
def api_ruc(ruc):
    """API endpoint para consultar datos de RUC."""
    try:
        print(f"🔍 API RUC consultando: {ruc}")

        # Usar el servicio para obtener los datos
        resultado = EmpresaService.buscar_por_ruc(ruc)

        if resultado["success"]:
            print(f"✅ Datos RUC encontrados: {resultado['data']['razon_social']}")
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404

    except Exception as e:
        print(f"❌ Error en API RUC: {e}")
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500


@app.route("/api/dni/<dni>")
def api_dni(dni):
    """API endpoint para consultar datos de DNI."""
    try:
        print(f"🔍 API DNI consultando: {dni}")

        # Usar el servicio para obtener los datos
        resultado = PersonaService.buscar_por_dni(dni)

        if resultado["success"]:
            print(f"✅ Datos DNI encontrados: {resultado['data']['nombre_completo']}")
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404

    except Exception as e:
        print(f"❌ Error en API DNI: {e}")
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
                    print(f"🧹 PDF temporal eliminado: {archivo}")
                except Exception as e:
                    print(f"❌ No se pudo eliminar '{archivo}': {e}")

        if archivos_eliminados > 0:
            print(
                f"🧹 Total de archivos PDF temporales eliminados: {archivos_eliminados}"
            )

    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")

    return response


if __name__ == "__main__":
    print("🚀 Iniciando aplicación Flask...")
    print("📋 Endpoints disponibles:")
    print("   - GET  /              -> Formulario principal")
    print("   - POST /submit        -> Procesar formulario")
    print("   - GET  /api/ruc/<ruc> -> Consultar RUC")
    print("   - GET  /api/dni/<dni> -> Consultar DNI")
    print("   - GET  /api/health    -> Estado de la aplicación")

    app.run(debug=True, host="0.0.0.0", port=5000)
