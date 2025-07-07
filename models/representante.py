from utils import limpiar_datos_api, formatear_nombre_completo


class Representante:
    def __init__(self, dni, nombre, cargo, tipo_documento="DNI"):
        self.dni = dni
        self.nombre = nombre
        self.cargo = cargo
        self.tipo_documento = tipo_documento

        # Datos adicionales del representante (obtenidos de API de DNI)
        self.nombres = None  # Solo nombres
        self.apellido_paterno = None
        self.apellido_materno = None
        self.nombre_completo = None
        self.direccion = None
        self.distrito = None
        self.provincia = None
        self.departamento = None

    def __str__(self):
        return f"{self.get_nombre_formateado()}, DNI: {self.dni}, Cargo: {self.cargo}"

    def get_nombre_formateado(self):
        """Obtiene el nombre en formato: Nombres Apellido_Paterno Apellido_Materno"""
        if self.nombres and self.apellido_paterno:
            return formatear_nombre_completo(
                self.nombres, self.apellido_paterno, self.apellido_materno
            )
        return self.nombre  # Fallback al nombre original

    @classmethod
    def from_dict(cls, data):
        """Crear instancia desde datos de API de representante."""
        datos_limpios = limpiar_datos_api(data)

        return cls(
            dni=datos_limpios.get(
                "numero_de_documento", datos_limpios.get("dni", "")
            ),  # Mapear correctamente el DNI
            nombre=datos_limpios.get("nombre", ""),
            cargo=datos_limpios.get("cargo", ""),
            tipo_documento=datos_limpios.get(
                "tipo_de_documento", datos_limpios.get("tipo_documento", "DNI")
            ),
        )

    def actualizar_datos_personales(self, datos_persona):
        """Actualizar con datos obtenidos de la API de DNI."""
        if datos_persona:
            datos_limpios = limpiar_datos_api(datos_persona)

            self.nombres = datos_limpios.get("nombres", "")
            self.apellido_paterno = datos_limpios.get("apellido_paterno", "")
            self.apellido_materno = datos_limpios.get("apellido_materno", "")
            self.nombre_completo = datos_limpios.get("nombre_completo", "")
            self.direccion = datos_limpios.get("direccion", "")
            self.distrito = datos_limpios.get("distrito", "")
            self.provincia = datos_limpios.get("provincia", "")
            self.departamento = datos_limpios.get("departamento", "")

    def to_dict(self):
        """Convertir a diccionario para la respuesta del API."""
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "nombres": self.nombres,
            "cargo": self.cargo,
            "tipo_documento": self.tipo_documento,
            "apellido_paterno": self.apellido_paterno,
            "apellido_materno": self.apellido_materno,
            "nombre_completo": self.nombre_completo,
            "nombre_formateado": self.get_nombre_formateado(),
            "direccion": self.direccion,
            "distrito": self.distrito,
            "provincia": self.provincia,
            "departamento": self.departamento,
        }
