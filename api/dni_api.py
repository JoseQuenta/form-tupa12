import requests

# Configuración de la API de Factiliza para DNI
DNI_API_URL = "https://api.factiliza.com/v1/dni/info"
DNI_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzODc1NSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6ImNvbnN1bHRvciJ9.-CN4BnRQg7nlKmvnEIZM0DdICETaMy5MInpIZ37cQt0"


def consultar_dni(dni):
    """Consulta datos de una persona por DNI desde la API de Factiliza."""
    try:
        headers = {"Authorization": f"Bearer {DNI_API_TOKEN}"}
        url = f"{DNI_API_URL}/{dni}"

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success") and data.get("status") == 200:
            return data["data"]
        else:
            print(
                f"Consulta fallida para DNI {dni}: {data.get('message', 'Error desconocido')}"
            )
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error consultando DNI: {e}")
        return None


# # Función de prueba (opcional)
# if __name__ == "__main__":
#     dni_test = "27427864"
#     datos_dni = consultar_dni(dni_test)

#     if datos_dni:
#         print("Datos DNI encontrados:")
#         print(f"Nombre: {datos_dni.get('nombre_completo', 'N/A')}")
#         print(f"Dirección: {datos_dni.get('direccion_completa', 'N/A')}")
#     else:
#         print("No se pudieron obtener los datos del DNI")
