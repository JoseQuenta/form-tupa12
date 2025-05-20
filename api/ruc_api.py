# import requests

# API_URL = "https://miapi.cloud/v1/ruc/completo/"
# TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyMzIsImV4cCI6MTc0NDY2MzU0N30.52IulyaYqiwToUirzupz8NOeemSfRe1wfLq1bPupYgY"

# def consultar_ruc(ruc):
#     headers = {
#         "Authorization": f"Bearer {TOKEN}"
#     }

#     try:
#         response = requests.get(f"{API_URL}{ruc}", headers=headers)
#         data = response.json()
#         return data
#     except Exception as e:
#         return {"success": False, "error": str(e)}

import requests
import json

# TOKEN = "AkrmyOTzucAegtqaKO488aBdsxNAD2tX4GiwOUCxiMVvVZXKSULzKpXYlkcR"
TOKEN = "ous9hGXeh3tYildEXDElzq6mOXD0nya8hSIUw5h8xKx8arTS1m799AIDtKza"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# --- Función para consultar datos generales de RUC ---
def consultar_ruc(ruc):
    url = "https://api.migo.pe/api/v1/ruc"
    payload = {"token": TOKEN, "ruc": ruc}

    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()  # lanza excepción si el código HTTP es error
        return response.json()
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}

# --- Función para obtener representante legal ---
def consultar_representante_legal(ruc):
    url = "https://api.migo.pe/api/v1/ruc/representantes-legales"
    payload = {"token": TOKEN, "ruc": ruc}

    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}

# --- (opcional) Prueba rápida solo si se ejecuta directamente ---
if __name__ == "__main__":
    ruc_test = "20131380951"
    datos_ruc = consultar_ruc(ruc_test)
    datos_rep = consultar_representante_legal(ruc_test)

    print("Datos RUC:\n", json.dumps(datos_ruc, indent=2))
    print("\nRepresentante Legal:\n", json.dumps(datos_rep, indent=2))
