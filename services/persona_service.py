"""
Servicio para manejar la lógica de negocio relacionada con personas naturales.
"""

from api.dni_api import consultar_dni
from models.persona import Persona


class PersonaService:
    """Servicio para gestionar operaciones con personas naturales."""

    @staticmethod
    def buscar_por_dni(dni: str) -> dict:
        """
        Busca una persona por DNI y devuelve los datos formateados para el frontend.

        Args:
            dni (str): El número de DNI a consultar

        Returns:
            dict: Respuesta estructurada con los datos de la persona o error
        """
        try:
            # Validar DNI
            if not dni or len(dni) != 8 or not dni.isdigit():
                return {
                    "success": False,
                    "message": "DNI debe tener exactamente 8 dígitos numéricos",
                }

            # Consultar DNI en API externa
            datos_dni = consultar_dni(dni)
            if not datos_dni:
                return {
                    "success": False,
                    "message": f"No se encontró información para el DNI {dni}",
                }

            # Crear objeto Persona usando el modelo
            persona = Persona.from_dict(datos_dni)

            # Procesar dirección (lógica de negocio centralizada)
            direccion_procesada = PersonaService._procesar_direccion(persona.direccion)

            # Devolver datos estructurados para el frontend
            resultado = {
                "success": True,
                "data": {
                    "numero": persona.dni,
                    "nombres": persona.nombres,
                    "apellido_paterno": persona.apellido_paterno,
                    "apellido_materno": persona.apellido_materno,
                    "nombre_completo": persona.nombre_completo,
                    "direccion": direccion_procesada,
                    "distrito": persona.distrito,
                    "provincia": persona.provincia,
                    "departamento": persona.departamento,
                },
                "message": f"Datos encontrados para {persona.nombre_completo}",
            }

            return resultado

        except Exception as e:
            return {"success": False, "message": f"Error al consultar DNI: {str(e)}"}

    @staticmethod
    def _procesar_direccion(direccion: str) -> str:
        """
        Procesa la dirección para extraer solo la parte relevante.
        Lógica de negocio centralizada para el procesamiento de direcciones.

        Args:
            direccion (str): Dirección cruda de la API

        Returns:
            str: Dirección procesada
        """
        if not direccion:
            return ""

        # Recortar dirección hasta paréntesis (lógica de negocio)
        import re

        match = re.match(r"^(.+?\))\s*", direccion)
        return match.group(1).strip() if match else direccion.strip()

    @staticmethod
    def validar_datos_persona(datos: dict) -> dict:
        """
        Valida los datos de una persona antes de procesarlos.

        Args:
            datos (dict): Datos de la persona a validar

        Returns:
            dict: Resultado de la validación
        """
        errores = []

        # Validaciones de negocio
        if not datos.get("nombres"):
            errores.append("Nombres es obligatorio")

        if not datos.get("apellido_paterno") and not datos.get("apellido_materno"):
            errores.append("Al menos un apellido es obligatorio")

        if datos.get("dni") and len(datos["dni"]) != 8:
            errores.append("DNI debe tener 8 dígitos")

        return {"valido": len(errores) == 0, "errores": errores}
