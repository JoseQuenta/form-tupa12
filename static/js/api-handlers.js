import {
    dniInput, nombreInput, apellidoInput, direccionInput, distritoInput,
    provinciaInput, departamentoInput, statusSpan,
    rucInput, razonSocialInput, direccionJurInput, distritoJurInput,
    provinciaJurInput, departamentoJurInput, statusRucSpan,
    repLegalInput, dniRepLegalInput, buscarDniBtn, buscarRucBtn
} from './dom-elements.js';

function clearFields(fields) {
    fields.forEach(field => {
        if (field) field.value = "";
    });
}

function updateStatus(message, color, targetSpan, showSpinner = false) {
    if (targetSpan) {
        targetSpan.textContent = message;
        targetSpan.style.color = color;
        const spinner = targetSpan.querySelector('.spinner') || targetSpan.parentNode.querySelector('.spinner');
        if (spinner) {
            spinner.style.display = showSpinner ? 'inline-block' : 'none';
        }
    }
}

export async function buscarDni() {
    const dni = dniInput.value.trim();
    const fieldsToClear = [
        nombreInput, apellidoInput, direccionInput,
        distritoInput, provinciaInput, departamentoInput,
    ];

    if (dni.length !== 8 || isNaN(dni)) {
        updateStatus("Ingrese un DNI válido (8 dígitos)", "red", statusSpan);
        clearFields(fieldsToClear);
        return;
    }

    updateStatus("Buscando DNI...", "black", statusSpan, true);
    buscarDniBtn.disabled = true;

    try {
        const response = await fetch(`/api/dni/${dni}`);
        if (!response.ok) throw new Error("Error al consultar API de DNI");

        const result = await response.json();

        if (result.success && result.data) {
            const data = result.data;
            nombreInput.value = data.nombres || "";
            apellidoInput.value = `${data.apellido_paterno || ""} ${data.apellido_materno || ""}`.trim();
            direccionInput.value = data.direccion || "";
            distritoInput.value = data.distrito || "";
            provinciaInput.value = data.provincia || "";
            departamentoInput.value = data.departamento || "";
            updateStatus("Datos de DNI cargados.", "green", statusSpan);

            document.getElementById("telefono").focus();
        } else {
            clearFields(fieldsToClear);
            updateStatus(result.message || "DNI no encontrado.", "red", statusSpan);
            document.getElementById("nombre").focus();
        }
        updateStatus("Datos de DNI cargados.", "green", statusSpan); // Mover aquí para que el spinner se oculte después de cargar
    } catch (error) {
        console.error("Error al buscar DNI:", error);
        clearFields(fieldsToClear);
        updateStatus("Error al consultar DNI", "red", statusSpan);
        document.getElementById("nombre").focus();
    } finally {
        buscarDniBtn.disabled = false;
        updateStatus(statusSpan.textContent, statusSpan.style.color, statusSpan, false); // Asegurar que el spinner se oculte
    }
}

export async function buscarRuc() {
    const ruc = rucInput.value.trim();
    const fieldsToClear = [
        razonSocialInput, direccionJurInput,
        distritoJurInput, provinciaJurInput, departamentoJurInput,
        repLegalInput, dniRepLegalInput
    ];

    if (ruc.length !== 11 || isNaN(ruc)) {
        updateStatus("Ingrese un RUC válido (11 dígitos)", "red", statusRucSpan);
        clearFields(fieldsToClear);
        return;
    }

    updateStatus("Buscando RUC...", "black", statusRucSpan, true);
    buscarRucBtn.disabled = true;

    try {
        const response = await fetch(`/api/ruc/${ruc}`);
        if (!response.ok) throw new Error("Error al consultar API de RUC");

        const result = await response.json();

        if (result.success && result.datos) {
            const datos = result.datos;
            razonSocialInput.value = datos.nombre_o_razon_social || "";
            direccionJurInput.value = datos.direccion_simple || "";
            distritoJurInput.value = datos.distrito || "";
            provinciaJurInput.value = datos.provincia || "";
            departamentoJurInput.value = datos.departamento || "";

            // numeroJurInput.value = datos.numero_juridico || "";

            // Llenar DNI del representante legal
            const dniRep = datos.dni_representante || "";
            dniRepLegalInput.value = dniRep;

            // Usar el nombre del representante que ya viene procesado del backend
            if (repLegalInput) {
                repLegalInput.value = datos.representante_legal || "";
            }

            updateStatus("Datos de RUC cargados.", "green", statusRucSpan);

            document.getElementById("telefono").focus();
        } else {
            clearFields(fieldsToClear);
            updateStatus(result.message || "RUC no encontrado.", "red", statusRucSpan);
            document.getElementById("razon_social").focus();
        }
        updateStatus("Datos de RUC cargados.", "green", statusRucSpan); // Mover aquí para que el spinner se oculte después de cargar
    } catch (error) {
        console.error("Error al buscar RUC:", error);
        clearFields(fieldsToClear);
        updateStatus("Error al consultar RUC", "red", statusRucSpan);
        document.getElementById("razon_social").focus();
    } finally {
        buscarRucBtn.disabled = false;
        updateStatus(statusRucSpan.textContent, statusRucSpan.style.color, statusRucSpan, false); // Asegurar que el spinner se oculte
    }
}
