from utils import limpiar_datos_api


class Empresa:
    def __init__(
        self,
        ruc,
        razon_social,
        direccion,
        distrito,
        provincia,
        departamento,
        telefono=None,
        correo=None,
    ):
        self.ruc = ruc
        self.razon_social = razon_social
        self.direccion = direccion
        self.distrito = distrito
        self.provincia = provincia
        self.departamento = departamento
        self.telefono = telefono
        self.correo = correo

    def __str__(self):
        return f"{self.razon_social}, RUC: {self.ruc}, Address: {self.direccion}, {self.distrito}, {self.provincia}, {self.departamento}, Phone: {self.telefono}, Email: {self.correo}"

    @classmethod
    def from_dict(cls, data):
        datos_limpios = limpiar_datos_api(data)
        return cls(
            ruc=datos_limpios.get("numero", ""),
            razon_social=datos_limpios.get("nombre_o_razon_social", ""),
            direccion=datos_limpios.get("direccion", ""),
            distrito=datos_limpios.get("distrito", ""),
            provincia=datos_limpios.get("provincia", ""),
            departamento=datos_limpios.get("departamento", ""),
            telefono=datos_limpios.get("telefono"),
            correo=datos_limpios.get("correo"),
        )
