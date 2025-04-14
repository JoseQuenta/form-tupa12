// import { form, firmaCanvas, firmaImgInput } from './dom-elements.js';
// import { setupUppercaseFields } from './uppercase-fields.js';

// import {
//     numeroPagoInput, fechaPagoInput, placaInput, cargaUtilInput,
//     btnEnviar, firmaError
// } from './dom-elements.js';

// // ✅ Validar campos de la página 2
// function validarPagina2() {
//     const errores = [];

//     if (!numeroPagoInput.value.trim()) errores.push("Número de pago es obligatorio.");
//     if (!fechaPagoInput.value.trim()) errores.push("Fecha de pago es obligatoria.");
//     if (!placaInput.value.trim()) errores.push("Placa es obligatoria.");
//     if (!cargaUtilInput.value.trim()) errores.push("Carga útil es obligatoria.");

//     const blank = document.createElement('canvas');
//     blank.width = firmaCanvas.width;
//     blank.height = firmaCanvas.height;

//     if (firmaCanvas.toDataURL() === blank.toDataURL()) {
//         errores.push("Debe ingresar su firma.");
//     }

//     return errores;
// }

// export function setupFormSubmission() {
//     form.addEventListener("submit", (event) => {
//         setupUppercaseFields();

//         const blank = document.createElement('canvas');
//         blank.width = firmaCanvas.width;
//         blank.height = firmaCanvas.height;
//         const isCanvasBlank = firmaCanvas.toDataURL() === blank.toDataURL();

//         if (isCanvasBlank) {
//             alert("Por favor, ingrese su firma.");
//             event.preventDefault();
//             return;
//         }

//         firmaImgInput.value = firmaCanvas.toDataURL("image/png");

//         // Después de enviar y generar el PDF, mostrar pantalla de éxito
//         setTimeout(() => {
//             document.getElementById("pdfForm").style.display = "none";
//             document.getElementById("pantallaExito").style.display = "block";

//             // Asignar enlace al botón de descarga si ya generaste el PDF en backend
//         const btnDescargar = document.getElementById("btnDescargar");
//         if (btnDescargar) {
//             btnDescargar.href = "/ruta/del/pdf/generado.pdf"; // Reemplaza con ruta real
//             btnDescargar.setAttribute("download", "expediente.pdf");
//         }

//         }, 500); // Espera un momento para asegurar que el PDF se procese
//     });
// }

import {
    form,
    firmaCanvas,
    firmaImgInput,
    numeroPagoInput,
    fechaPagoInput,
    placaInput,
    cargaUtilInput,
    btnEnviar
} from './dom-elements.js';

import { setupUppercaseFields } from './uppercase-fields.js';
import { validarPagina1 } from './navigation.js'; // Asegúrate de exportarlo

// ✅ Validar campos de la segunda página
function validarPagina2() {
    const errores = [];

    if (!numeroPagoInput.value.trim()) errores.push("Número de pago es obligatorio.");
    if (!fechaPagoInput.value.trim()) errores.push("Fecha de pago es obligatoria.");
    if (!placaInput.value.trim()) errores.push("Placa es obligatoria.");
    if (!cargaUtilInput.value.trim()) errores.push("Carga útil es obligatoria.");

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

        const errores = [
            ...validarPagina1(),
            ...validarPagina2()
        ];

        if (errores.length > 0) {
            alert("❌ Por favor completa los siguientes campos:\n\n" + errores.join("\n"));
            return;
        }

        // Desactiva botón mientras se procesa
        btnEnviar.disabled = true;
        btnEnviar.textContent = "Generando PDF...";

        firmaImgInput.value = firmaCanvas.toDataURL("image/png");

        try {
            const formData = new FormData(form);
            const response = await fetch("/submit", {
                method: "POST",
                body: formData
            });

            if (!response.ok) throw new Error("Error al generar PDF");

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            document.getElementById("pdfForm").style.display = "none";
            document.getElementById("pantallaExito").style.display = "block";

            const link = document.createElement("a");
            link.href = url;
            link.download = "expediente.pdf";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);


        } catch (error) {
            alert("⚠️ Hubo un error al enviar el formulario.");
            console.error(error);
        } finally {
            // Reactiva el botón
            btnEnviar.disabled = false;
            btnEnviar.textContent = "Generar PDF";
        }
    });
}
