from utils import limpiar_datos_api, formatear_nombre_completo


class Persona:
    def __init__(
        self,
        dni,
        nombres,
        apellido_paterno,
        apellido_materno,
        direccion,
        distrito,
        provincia,
        departamento,
    ):
        self.dni = dni
        self.nombres = nombres
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.direccion = direccion
        self.distrito = distrito
        self.provincia = provincia
        self.departamento = departamento

    @property
    def nombre_completo(self):
        """Retorna el nombre completo en formato: Apellidos, Nombres"""
        apellidos = f"{self.apellido_paterno} {self.apellido_materno}".strip()
        return f"{apellidos}, {self.nombres}".strip() if apellidos else self.nombres

    @property
    def nombre_formateado(self):
        """Retorna el nombre en formato: Nombres Apellido_Paterno Apellido_Materno"""
        return formatear_nombre_completo(
            self.nombres, self.apellido_paterno, self.apellido_materno
        )

    def __str__(self):
        return f"{self.nombre_formateado}, DNI: {self.dni}, Address: {self.direccion}, {self.distrito}, {self.provincia}, {self.departamento}"

    @classmethod
    def from_dict(cls, data):
        datos_limpios = limpiar_datos_api(data)

        nombres = datos_limpios.get("nombres", "")
        ape_paterno = datos_limpios.get("apellido_paterno", "")
        ape_materno = datos_limpios.get("apellido_materno", "")
        return cls(
            dni=datos_limpios.get("dni", ""),
            nombres=nombres,
            apellido_paterno=ape_paterno,
            apellido_materno=ape_materno,
            direccion=datos_limpios.get("direccion", ""),
            distrito=datos_limpios.get("distrito", ""),
            provincia=datos_limpios.get("provincia", ""),
            departamento=datos_limpios.get("departamento", ""),
        )
