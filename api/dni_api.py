import requests

DNI_API_URL = "https://miapi.cloud/v1/dni"
DNI_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyOTMsImV4cCI6MTc0ODMwNDExNn0.ebsmsvn7Etx10taoiXkFji0eyGanODE4gCIwjKWnP9U"

def consultar_dni(dni):
    """Consulta datos de una persona por DNI desde la API externa."""
    try:
        headers = {'Authorization': f'Bearer {DNI_API_TOKEN}'}
        response = requests.get(f"{DNI_API_URL}/{dni}", headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('success'):
            return data['datos']
        else:
            print(f"Consulta fallida para DNI {dni}: {data}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error consultando DNI: {e}")
        return None
