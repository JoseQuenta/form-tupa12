import requests

# Configuración de la API de Factiliza
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzODc1NSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6ImNvbnN1bHRvciJ9.-CN4BnRQg7nlKmvnEIZM0DdICETaMy5MInpIZ37cQt0"

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# URLs de la API de Factiliza
RUC_INFO_URL = "https://api.factiliza.com/v1/ruc/info"
RUC_REPRESENTANTE_URL = "https://api.factiliza.com/v1/ruc/representante"


def consultar_ruc(ruc):
    """Consulta datos generales de RUC desde la API de Factiliza."""
    try:
        url = f"{RUC_INFO_URL}/{ruc}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success") and data.get("status") == 200:
            return {"success": True, "data": data["data"]}
        else:
            return {"success": False, "error": data.get("message", "Error desconocido")}

    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def consultar_representante_legal(ruc):
    """Consulta representantes legales de un RUC desde la API de Factiliza."""
    try:
        url = f"{RUC_REPRESENTANTE_URL}/{ruc}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == 200:
            return {"success": True, "data": data["data"]}
        else:
            return {"success": False, "error": data.get("message", "Error desconocido")}

    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


# # Función de prueba (opcional)
# if __name__ == "__main__":
#     ruc_test = "20552103816"

#     print("=== Consultando datos de RUC ===")
#     datos_ruc = consultar_ruc(ruc_test)
#     print(json.dumps(datos_ruc, indent=2, ensure_ascii=False))

#     print("\n=== Consultando representante legal ===")
#     datos_rep = consultar_representante_legal(ruc_test)
#     print(json.dumps(datos_rep, indent=2, ensure_ascii=False))
