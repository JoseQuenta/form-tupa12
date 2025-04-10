document.addEventListener("DOMContentLoaded", () => {
    // --- Referencias a Elementos ---
    const form = document.getElementById("pdfForm");
    const dniInput = document.getElementById("dni");
    const nombreInput = document.getElementById("nombre");
    const apellidoInput = document.getElementById("apellido");
    const direccionInput = document.getElementById("direccion_h1");
    const distritoInput = document.getElementById("distrito");
    const provinciaInput = document.getElementById("provincia");
    const departamentoInput = document.getElementById("departamento");
    const ubigeoInput = document.getElementById("ubigeo"); // Considerar si debe ser uppercase
    const telefonoInput = document.getElementById("telefono");
    const correoInput = document.getElementById("correo");
    const sinCorreoCheckbox = document.getElementById("sinCorreo");
    const numeroPagoInput = document.getElementById("numero_pago");
    const fechaPagoInput = document.getElementById("fecha_pago");
    const placaInput = document.getElementById("placa");
    const cargaUtilInput = document.getElementById("carga_util");
    const statusSpan = document.getElementById("status");
    const firmaCanvas = document.getElementById("firma");
    const firmaImgInput = document.getElementById("firma_img");
    const ctx = firmaCanvas.getContext("2d");

    // Campos que deben ir en mayúsculas (añade/quita IDs según necesites)
    const uppercaseFields = [
        nombreInput, apellidoInput, direccionInput, distritoInput,
        provinciaInput, departamentoInput, placaInput
        // ¿DNI? ¿Ubigeo? Si son solo números, no hace falta. Si pueden tener letras, sí.
    ];

    // --- Configuración Inicial Canvas ---
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "black";
    let dibujando = false;
    let lastPoint = null;

    // --- Buscar DNI y completar campos ---
    window.buscarDni = async function () {
        const dni = dniInput.value.trim();
    
        if (dni.length !== 8 || isNaN(dni)) {
            statusSpan.textContent = "Ingrese un DNI válido (8 dígitos)";
            statusSpan.style.color = "red";
            return;
        }
    
        statusSpan.textContent = "Buscando...";
        statusSpan.style.color = "black";
    
        try {
            const response = await fetch(`/api/dni/${dni}`);
            const data = await response.json();
    
            if (data.success) {
                document.getElementById("nombre").value = data.nombres || "";
                document.getElementById("apellido").value = `${data.ape_paterno || ""} ${data.ape_materno || ""}`.trim();
                document.getElementById("direccion_h1").value = data.domiciliado?.direccion || "";
                document.getElementById("distrito").value = data.domiciliado?.distrito || "";
                document.getElementById("provincia").value = data.domiciliado?.provincia || "";
                document.getElementById("departamento").value = data.domiciliado?.departamento || "";
                document.getElementById("ubigeo").value = data.domiciliado?.ubigeo || "";
    
                statusSpan.textContent = "Datos cargados.";
                statusSpan.style.color = "green";
            } else {
                statusSpan.textContent = "DNI no encontrado.";
                statusSpan.style.color = "red";
            }
        } catch (err) {
            console.error(err);
            statusSpan.textContent = "Error al consultar DNI.";
            statusSpan.style.color = "red";
        }
    };

    // --- Checkbox: sin correo ---
    sinCorreoCheckbox.addEventListener("change", () => {
        if (sinCorreoCheckbox.checked) {
            correoInput.value = "soycargototal@gmail.com"; // Correo por defecto
            correoInput.disabled = true;
            correoInput.required = false; // Ya no es requerido si está deshabilitado
        } else {
            correoInput.value = "";
            correoInput.disabled = false;
            correoInput.required = true; // Vuelve a ser requerido
        }
    });
    // Estado inicial por si la página se recarga con el checkbox marcado
    if (sinCorreoCheckbox.checked) {
        correoInput.disabled = true;
        correoInput.required = false;
    }


    // --- Filtro para campos NUMÉRICOS ---
    const filterNumericInput = (event) => {
        event.target.value = event.target.value.replace(/[^\d]/g, ''); // Reemplaza todo lo que NO sea dígito
    };

    telefonoInput.addEventListener('input', filterNumericInput);
    numeroPagoInput.addEventListener('input', filterNumericInput);
    cargaUtilInput.addEventListener('input', filterNumericInput);
    // DNI y Ubigeo también si SÓLO deben ser números
    dniInput.addEventListener('input', filterNumericInput);
    ubigeoInput.addEventListener('input', filterNumericInput);


    // --- Formato y Mayúsculas para PLACA ---
    placaInput.addEventListener('input', (event) => {
        let value = event.target.value.toUpperCase();
        // 1. Quitar caracteres inválidos (todo excepto letras A-Z y números 0-9)
        value = value.replace(/[^A-Z0-9]/g, '');

        // 2. Insertar guion después del 3er caracter si hay más de 3 caracteres
        if (value.length > 3) {
            value = value.slice(0, 3) + '-' + value.slice(3);
        }

        // 3. Limitar longitud total (incluyendo guion)
        if (value.length > 7) {
            value = value.slice(0, 7);
        }

        event.target.value = value;
    });

    // --- Convertir a MAYÚSCULAS en tiempo real ---
    uppercaseFields.forEach(field => {
        if(field) { // Asegurarse que el elemento existe
            field.addEventListener('input', (event) => {
                // Guardar posición del cursor
                const start = event.target.selectionStart;
                const end = event.target.selectionEnd;
                // Convertir a mayúsculas
                event.target.value = event.target.value.toUpperCase();
                // Restaurar posición del cursor
                event.target.setSelectionRange(start, end);
            });
            // Aplicar estilo CSS también (ver CSS)
            field.classList.add('uppercase-input'); // Asegurar que la clase esté
        }
    });


    // --- Eventos del Canvas de Firma ---
    const getPosicion = (e) => {
        const rect = firmaCanvas.getBoundingClientRect();
        let clientX = e.clientX;
        let clientY = e.clientY;
        // Considerar eventos táctiles
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        }
        return {
            x: clientX - rect.left,
            y: clientY - rect.top,
        };
    };

    const startDrawing = (e) => {
        e.preventDefault(); // Prevenir scroll en táctil
        dibujando = true;
        lastPoint = getPosicion(e);
        // Dibuja un punto inicial si es táctil para mejor respuesta
         if (e.touches) {
             ctx.beginPath();
             ctx.arc(lastPoint.x, lastPoint.y, ctx.lineWidth / 2, 0, Math.PI * 2);
             ctx.fillStyle = ctx.strokeStyle;
             ctx.fill();
         }
    };

    const draw = (e) => {
        if (!dibujando) return;
        e.preventDefault();
        const currentPoint = getPosicion(e);
        if (lastPoint) {
            ctx.beginPath();
            ctx.moveTo(lastPoint.x, lastPoint.y);
            ctx.lineTo(currentPoint.x, currentPoint.y);
            ctx.stroke();
        }
        lastPoint = currentPoint;
    };

    const stopDrawing = () => {
        dibujando = false;
        lastPoint = null;
    };

    // Eventos de Mouse
    firmaCanvas.addEventListener("mousedown", startDrawing);
    firmaCanvas.addEventListener("mousemove", draw);
    firmaCanvas.addEventListener("mouseup", stopDrawing);
    firmaCanvas.addEventListener("mouseleave", stopDrawing);

    // Eventos Táctiles (para móviles/tablets)
    firmaCanvas.addEventListener("touchstart", startDrawing);
    firmaCanvas.addEventListener("touchmove", draw);
    firmaCanvas.addEventListener("touchend", stopDrawing);
    firmaCanvas.addEventListener("touchcancel", stopDrawing);


    // --- Limpiar Firma ---
    window.limpiarFirma = function () {
        ctx.clearRect(0, 0, firmaCanvas.width, firmaCanvas.height);
        // Restaurar estilos por si acaso
        ctx.lineWidth = 2;
        ctx.lineCap = "round";
        ctx.strokeStyle = "black";
        firmaImgInput.value = ""; // Limpiar también el input oculto
    };

    // --- Antes de Enviar el Formulario ---
    form.addEventListener("submit", (event) => {
         // 1. Asegurar que todos los campos 'uppercase' estén en mayúsculas
         uppercaseFields.forEach(field => {
             if (field && field.value) {
                 field.value = field.value.toUpperCase();
             }
         });

        // 2. Validar si el canvas de firma está vacío (opcional pero recomendado)
        // Una forma simple es verificar si el input oculto tiene datos
        // Otra es verificar si el canvas está realmente "en blanco" (más complejo)
        const isEmpty = !firmaCanvas.toDataURL().replace(/^data:image\/(png|jpg);base64,/, ""); // Verifica si la data URL está vacía (puede fallar en algunos casos)

        // Una verificación más robusta (compara con un canvas vacío):
        const blank = document.createElement('canvas');
        blank.width = firmaCanvas.width;
        blank.height = firmaCanvas.height;
        const isCanvasBlank = firmaCanvas.toDataURL() === blank.toDataURL();


        if (isCanvasBlank) {
             alert("Por favor, ingrese su firma.");
             event.preventDefault(); // Detener el envío del formulario
             // Podrías añadir un mensaje de error visual cerca del canvas
             return; // Salir de la función
        } else {
             // Si no está vacío, guardar la imagen en el input oculto
             firmaImgInput.value = firmaCanvas.toDataURL("image/png");
        }

        // 3. Aquí podrías añadir más validaciones JS si fueran necesarias
        // Por ejemplo, verificar que la fecha no sea futura, etc.

        // Si todo está bien, el formulario se enviará.
        // ¡RECUERDA VALIDAR TODO DE NUEVO EN EL SERVIDOR (Python/Flask)!
    });

}); // Fin de DOMContentLoaded