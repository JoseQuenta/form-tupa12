# Arquitectura de Servicios

## Separación de Responsabilidades

### Frontend (JavaScript)
- **Responsabilidad**: Únicamente manejo de la interfaz de usuario
- **Ubicación**: `static/js/api-handlers.js`
- **Funciones**:
  - Validación básica de entrada (longitud, formato)
  - Llamadas a APIs del backend
  - Manipulación del DOM (actualizar campos, mostrar mensajes)
  - Gestión de estados de UI (loading, errores, éxito)

### Backend (Python)

#### Servicios de Negocio
- **Ubicación**: `services/`
- **Responsabilidad**: Lógica de negocio centralizada

##### PersonaService (`services/persona_service.py`)
- Consulta y procesamiento de datos de personas naturales
- Validación de DNI
- Procesamiento de direcciones
- Formateo de respuestas para el frontend

##### EmpresaService (`services/empresa_service.py`)
- Consulta y procesamiento de datos de empresas
- Validación de RUC
- Gestión de representantes legales
- Procesamiento de direcciones empresariales

#### APIs Externas
- **Ubicación**: `api/`
- **Responsabilidad**: Comunicación con servicios externos
- `dni_api.py`: Consulta a API de RENIEC
- `ruc_api.py`: Consulta a API de SUNAT

#### Modelos
- **Ubicación**: `models/`
- **Responsabilidad**: Representación de entidades de negocio
- `persona.py`: Modelo de persona natural
- `empresa.py`: Modelo de empresa
- `representante.py`: Modelo de representante legal

#### Controladores (Flask)
- **Ubicación**: `app.py`
- **Responsabilidad**: Endpoints HTTP y orquestación
- Recibe peticiones HTTP
- Llama a servicios apropiados
- Devuelve respuestas estructuradas

## Flujo de Datos

### Consulta de DNI
1. **Frontend**: Usuario ingresa DNI y hace clic en "Buscar"
2. **Frontend**: Validación básica (8 dígitos)
3. **Frontend**: Llamada a `/api/dni/{dni}`
4. **Backend**: Endpoint recibe petición
5. **Backend**: `PersonaService.buscar_por_dni()` procesa la lógica
6. **Backend**: Servicio llama a `consultar_dni()` (API externa)
7. **Backend**: Servicio crea modelo `Persona`
8. **Backend**: Servicio procesa dirección (lógica de negocio)
9. **Backend**: Servicio devuelve datos estructurados
10. **Frontend**: Recibe respuesta y actualiza campos del formulario

### Consulta de RUC
1. **Frontend**: Usuario ingresa RUC y hace clic en "Buscar"
2. **Frontend**: Validación básica (11 dígitos)
3. **Frontend**: Llamada a `/api/ruc/{ruc}`
4. **Backend**: Endpoint recibe petición
5. **Backend**: `EmpresaService.buscar_por_ruc()` procesa la lógica
6. **Backend**: Servicio llama a APIs externas (empresa + representante)
7. **Backend**: Servicio crea modelos `Empresa` y `Representante`
8. **Backend**: Servicio procesa direcciones (lógica de negocio)
9. **Backend**: Servicio devuelve datos estructurados
10. **Frontend**: Recibe respuesta y actualiza campos del formulario

## Ventajas de esta Arquitectura

### ✅ Separación Clara de Responsabilidades
- Frontend solo maneja UI
- Backend maneja toda la lógica de negocio
- APIs externas encapsuladas en módulos específicos

### ✅ Reutilización de Código
- Servicios pueden ser usados por otros endpoints
- Lógica de negocio centralizada
- Modelos reutilizables

### ✅ Testabilidad
- Servicios pueden ser testeados independientemente
- Mocks fáciles para APIs externas
- Validaciones centralizadas

### ✅ Mantenibilidad
- Cambios en lógica de negocio solo afectan servicios
- Frontend desacoplado del backend
- Código más limpio y organizado

### ✅ Escalabilidad
- Servicios pueden evolucionar independientemente
- Fácil agregar nuevos endpoints
- Lógica de negocio reutilizable

## Ejemplo de Respuesta Estructurada

```json
{
  "success": true,
  "data": {
    "numero": "12345678",
    "nombres": "JUAN CARLOS",
    "apellido_paterno": "GARCIA",
    "apellido_materno": "LOPEZ",
    "nombre_completo": "GARCIA LOPEZ, JUAN CARLOS",
    "direccion": "AV. LIMA 123 (LIMA)",
    "distrito": "LIMA",
    "provincia": "LIMA",
    "departamento": "LIMA"
  },
  "message": "Datos encontrados para GARCIA LOPEZ, JUAN CARLOS"
}
```
