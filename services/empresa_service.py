"""
Servicio para manejar la lógica de negocio relacionada con empresas.
"""

from api.ruc_api import consultar_ruc, consultar_representante_legal
from services.persona_service import PersonaService
from models.empresa import Empresa
from models.representante import Representante


class EmpresaService:
    """Servicio para gestionar operaciones con personas jurídicas."""

    @staticmethod
    def buscar_por_ruc(ruc: str) -> dict:
        """
        Busca una empresa por RUC y devuelve los datos formateados para el frontend.
        Incluye consulta completa del representante legal.

        Args:
            ruc (str): El número de RUC a consultar

        Returns:
            dict: Respuesta estructurada con los datos de la empresa y representante completo
        """
        try:
            # Validar RUC
            if not ruc or len(ruc) != 11 or not ruc.isdigit():
                return {
                    "success": False,
                    "message": "RUC debe tener exactamente 11 dígitos numéricos",
                }

            # 1. Consultar datos de la empresa
            resultado_ruc = consultar_ruc(ruc)
            if not resultado_ruc.get("success"):
                return {
                    "success": False,
                    "message": f"Error consultando RUC: {resultado_ruc.get('error', 'Error desconocido')}",
                }

            # Crear objeto Empresa
            empresa = Empresa.from_dict(resultado_ruc["data"])

            # 2. Consultar representante legal
            representante = None
            resultado_rep = consultar_representante_legal(ruc)

            if resultado_rep.get("success") and resultado_rep.get("data"):
                representante_data = resultado_rep["data"][0]  # Primer representante
                representante = Representante.from_dict(representante_data)

                # 3. Consultar datos personales del representante usando su DNI
                if representante.dni:
                    resultado_dni = PersonaService.buscar_por_dni(representante.dni)

                    if resultado_dni.get("success"):
                        representante.actualizar_datos_personales(resultado_dni["data"])

            # Procesar dirección (lógica de negocio centralizada)
            direccion_procesada = EmpresaService._procesar_direccion(empresa.direccion)

            # Devolver datos estructurados para el frontend
            response_data = {
                "success": True,
                "data": {
                    # Datos de la empresa
                    "numero": empresa.ruc,
                    "razon_social": empresa.razon_social,
                    "direccion": direccion_procesada,
                    "distrito": empresa.distrito,
                    "provincia": empresa.provincia,
                    "departamento": empresa.departamento,
                    "telefono": empresa.telefono,
                    "correo": empresa.correo,
                    # Datos del representante legal
                    "representante_legal": (
                        representante.get_nombre_formateado() if representante else ""
                    ),
                    "dni_representante": representante.dni if representante else "",
                    "cargo_representante": representante.cargo if representante else "",
                    # Datos personales completos del representante (si se obtuvieron)
                    "rep_nombres": (representante.nombres if representante else ""),
                    "rep_apellido_paterno": (
                        representante.apellido_paterno if representante else ""
                    ),
                    "rep_apellido_materno": (
                        representante.apellido_materno if representante else ""
                    ),
                    "rep_nombre_completo": (
                        representante.nombre_completo if representante else ""
                    ),
                    "rep_direccion": representante.direccion if representante else "",
                    "rep_distrito": representante.distrito if representante else "",
                    "rep_provincia": representante.provincia if representante else "",
                    "rep_departamento": (
                        representante.departamento if representante else ""
                    ),
                },
                "message": f"Datos encontrados para {empresa.razon_social}",
            }

            # Agregar información adicional del representante si está disponible
            if representante and representante.nombre_completo:
                response_data[
                    "message"
                ] += f" - Representante: {representante.nombre_completo}"

            return response_data

        except Exception as e:
            return {"success": False, "message": f"Error al consultar RUC: {str(e)}"}

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
    def validar_datos_empresa(datos: dict) -> dict:
        """
        Valida los datos de una empresa antes de procesarlos.

        Args:
            datos (dict): Datos de la empresa a validar

        Returns:
            dict: Resultado de la validación
        """
        errores = []

        # Validaciones de negocio
        if not datos.get("razon_social"):
            errores.append("Razón social es obligatoria")

        if datos.get("ruc") and len(datos["ruc"]) != 11:
            errores.append("RUC debe tener 11 dígitos")

        if not datos.get("direccion"):
            errores.append("Dirección es obligatoria")

        return {"valido": len(errores) == 0, "errores": errores}
