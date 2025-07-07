import {
    form,
    firmaCanvas,
    firmaImgInput,
    numeroPagoInput,
    fechaPagoInput,
    placaInput,
    cargaUtilInput,
    btnEnviar,
    carroceriaSelect,
    campoCarroceriaOtro
} from './dom-elements.js';

import { setupUppercaseFields } from './uppercase-fields.js';
import { validarPagina1 } from './navigation.js';

let urlPDFGenerado = null;

// ✅ Validar campos de la segunda página
function validarPagina2() {
    const errores = [];

    if (!numeroPagoInput.value.trim()) errores.push("Número de pago es obligatorio.");
    if (!fechaPagoInput.value.trim()) errores.push("Fecha de pago es obligatoria.");
    if (!placaInput.value.trim()) errores.push("Placa es obligatoria.");
    if (!cargaUtilInput.value.trim()) errores.push("Carga útil es obligatoria.");

    // ✅ Validación de tipo de carrocería
    const tipoSeleccionado = carroceriaSelect?.value;
    const otroTexto = document.getElementById("tipo_carroceria_otro")?.value.trim();

    if (!tipoSeleccionado) {
        errores.push("Debe seleccionar el tipo de carrocería.");
    } else if (tipoSeleccionado === "Otros" && !otroTexto) {
        errores.push("Debe especificar el tipo de carrocería.");
    }


    const blank = document.createElement('canvas');
    blank.width = firmaCanvas.width;
    blank.height = firmaCanvas.height;

    if (firmaCanvas.toDataURL() === blank.toDataURL()) {
        errores.push("Debe ingresar su firma.");
    }

    return errores;
}

export function setupFormSubmission() {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setupUppercaseFields();

        // Manejar campo de fecha para Edge
        const fechaInput = document.getElementById('fecha_pago');
        if (fechaInput && fechaInput.hasAttribute('data-formatted-value')) {
            const formattedValue = fechaInput.getAttribute('data-formatted-value');
            fechaInput.value = formattedValue;
        }

        const errores = [
            ...validarPagina1(),
            ...validarPagina2()
        ];

        if (errores.length > 0) {
            alert("❌ Por favor completa los siguientes campos:\n\n" + errores.join("\n"));
            return;
        }

        btnEnviar.disabled = true;
        btnEnviar.textContent = "Generando PDF...";

        firmaImgInput.value = firmaCanvas.toDataURL("image/png");

        try {
            const formData = new FormData(form);
            const response = await fetch("/submit", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                // Try to get error message from response
                let errorMessage = "Error al generar PDF";
                try {
                    const errorData = await response.text();
                    if (errorData) {
                        errorMessage = errorData;
                    }
                } catch (e) {
                    // If we can't parse the error, use the status
                    errorMessage = `Error ${response.status}: ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            const blob = await response.blob();
            urlPDFGenerado = URL.createObjectURL(blob);

            // ➕ Obtener la placa formateada para el nombre del archivo
            const placa = placaInput.value.trim().toUpperCase().replace(/\s+/g, "-");
            const nombreArchivo = `TUPA 12 - ${placa || "SIN-PLACA"}.pdf`;

            document.getElementById("pdfForm").style.display = "none";
            document.getElementById("pantallaExito").style.display = "block";

            // ➕ Descarga automática
            const autoLink = document.createElement("a");
            autoLink.href = urlPDFGenerado;
            autoLink.download = nombreArchivo;
            document.body.appendChild(autoLink);
            autoLink.click();
            document.body.removeChild(autoLink);

        } catch (error) {
            let errorMessage = "⚠️ Hubo un error al enviar el formulario.";

            // Try to get more specific error information
            if (error.message) {
                errorMessage += `\n\nDetalle: ${error.message}`;
            }

            alert(errorMessage);
            console.error("Error completo:", error);
        } finally {
            btnEnviar.disabled = false;
            btnEnviar.textContent = "Generar PDF";
        }
    });

    // ➕ Botón para descarga manual
    const btnDescargarManual = document.getElementById("btnDescargarPDF");
    if (btnDescargarManual) {
        btnDescargarManual.addEventListener("click", () => {
            if (urlPDFGenerado) {
                const placa = placaInput.value.trim().toUpperCase().replace(/\s+/g, "-");
                const nombreArchivo = `TUPA 12 - ${placa || "SIN-PLACA"}.pdf`;

                const manualLink = document.createElement("a");
                manualLink.href = urlPDFGenerado;
                manualLink.download = nombreArchivo;
                document.body.appendChild(manualLink);
                manualLink.click();
                document.body.removeChild(manualLink);
            } else {
                alert("⚠️ Aún no se ha generado el PDF.");
            }
        });
    }
}
