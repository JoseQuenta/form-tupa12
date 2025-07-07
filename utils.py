"""
Utilidades comunes para el proyecto TUPA 12
"""


def limpiar_datos_api(datos):
    """
    Limpia los datos recibidos de APIs externos eliminando espacios en blanco.
    
    Args:
        datos (dict): Diccionario con datos de API
        
    Returns:
        dict: Diccionario con datos limpiados
    """
    if not isinstance(datos, dict):
        return datos
    
    datos_limpios = {}
    
    for clave, valor in datos.items():
        if isinstance(valor, str):
            # Limpiar strings: strip + eliminar espacios extra
            datos_limpios[clave] = " ".join(valor.strip().split())
        elif isinstance(valor, dict):
            # Recursivo para diccionarios anidados
            datos_limpios[clave] = limpiar_datos_api(valor)
        elif isinstance(valor, list):
            # Limpiar cada elemento de la lista
            datos_limpios[clave] = [
                limpiar_datos_api(item) if isinstance(item, (dict, str)) 
                else item for item in valor
            ]
        else:
            # Mantener otros tipos de datos sin cambios
            datos_limpios[clave] = valor
    
    return datos_limpios


def formatear_nombre_completo(nombres, apellido_paterno, apellido_materno):
    """
    Formatea un nombre completo en el orden: Nombres Apellido_Paterno Apellido_Materno
    
    Args:
        nombres (str): Nombres de la persona
        apellido_paterno (str): Apellido paterno
        apellido_materno (str): Apellido materno
        
    Returns:
        str: Nombre completo formateado y limpio
    """
    partes = []
    
    if nombres and nombres.strip():
        partes.append(nombres.strip())
    
    if apellido_paterno and apellido_paterno.strip():
        partes.append(apellido_paterno.strip())
        
    if apellido_materno and apellido_materno.strip():
        partes.append(apellido_materno.strip())
    
    return " ".join(partes)


def validar_datos_obligatorios(datos, campos_obligatorios):
    """
    Valida que los campos obligatorios estén presentes y no vacíos.
    
    Args:
        datos (dict): Diccionario con datos a validar
        campos_obligatorios (list): Lista de campos que son obligatorios
        
    Returns:
        dict: {"valido": bool, "errores": list}
    """
    errores = []
    
    for campo in campos_obligatorios:
        valor = datos.get(campo)
        if not valor or (isinstance(valor, str) and not valor.strip()):
            errores.append(f"El campo '{campo}' es obligatorio")
    
    return {
        "valido": len(errores) == 0,
        "errores": errores
    }
