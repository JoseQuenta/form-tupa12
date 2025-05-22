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

function updateStatus(message, color, targetSpan) {
    if (targetSpan) {
        targetSpan.textContent = message;
        targetSpan.style.color = color;
    }
}

function recortarDireccionHastaParentesis(direccion) {
    const match = direccion.match(/^(.+?\))\s*/);
    return match ? match[1].trim() : direccion;
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

    updateStatus("Buscando DNI...", "black", statusSpan);
    buscarDniBtn.disabled = true;

    try {
        const response = await fetch(`/api/dni/${dni}`);
        if (!response.ok) throw new Error("Error al consultar API de DNI");

        const data = await response.json();

        if (data.success) {
            const direccionCruda = data.domiciliado?.direccion || "";
            nombreInput.value = data.nombres || "";
            apellidoInput.value = `${data.ape_paterno || ""} ${data.ape_materno || ""}`.trim();
            direccionInput.value = recortarDireccionHastaParentesis(direccionCruda);
            distritoInput.value = data.domiciliado?.distrito || "";
            provinciaInput.value = data.domiciliado?.provincia || "";
            departamentoInput.value = data.domiciliado?.departamento || "";
            // ubigeoInput.value = data.domiciliado?.ubigeo || "";
            updateStatus("Datos de DNI cargados.", "green", statusSpan);

            document.getElementById("telefono").focus();
        } else {
            clearFields(fieldsToClear);
            updateStatus(data.message || "DNI no encontrado.", "red", statusSpan);

            document.getElementById("nombre").focus();
        }
    } catch (error) {
        console.error("Error al buscar DNI:", error);
        clearFields(fieldsToClear);
        updateStatus("Error al consultar DNI", "red", statusSpan);

        document.getElementById("nombre").focus();
    } finally {
        buscarDniBtn.disabled = false;
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

    updateStatus("Buscando RUC...", "black", statusRucSpan);
    buscarRucBtn.disabled = true;

    try {
        const response = await fetch(`/api/ruc/${ruc}`);
        if (!response.ok) throw new Error("Error al consultar API de RUC");

        const result = await response.json();

        if (result.success && result.datos) {
            const datos = result.datos;
            razonSocialInput.value = datos.nombre_o_razon_social || "";
            direccionJurInput.value = recortarDireccionHastaParentesis(datos.direccion_simple || "");
            distritoJurInput.value = datos.distrito || "";
            provinciaJurInput.value = datos.provincia || "";
            departamentoJurInput.value = datos.departamento || "";

            // numeroJurInput.value = datos.numero_juridico || "";

            // Llenar DNI del representante legal
            const dniRep = datos.dni_representante || "";
            dniRepLegalInput.value = dniRep;

            // Si hay DNI de representante, buscar sus datos para el nombre completo
            if (dniRep && repLegalInput) {
                try {
                    const dniResponse = await fetch(`/api/dni/${dniRep}`);
                    if (dniResponse.ok) {
                        const dniData = await dniResponse.json();
                        if (dniData.success) {
                            repLegalInput.value = `${dniData.nombres || ''} ${dniData.ape_paterno || ''} ${dniData.ape_materno || ''}`.trim();
                        } else {
                            // Si la API de DNI falla o no encuentra, usar el nombre que viene del RUC si existe
                            repLegalInput.value = datos.representante_legal || "";
                        }
                    } else {
                        // Si la llamada a la API de DNI falla, usar el nombre que viene del RUC
                        repLegalInput.value = datos.representante_legal || "";
                    }
                } catch (dniError) {
                    console.error("Error al buscar DNI del representante:", dniError);
                    // En caso de error, usar el nombre que viene del RUC
                    repLegalInput.value = datos.representante_legal || "";
                }
            } else if (repLegalInput) {
                // Si no hay DNI de representante, usar el nombre que viene del RUC
                repLegalInput.value = datos.representante_legal || "";
            }

            updateStatus("Datos de RUC cargados.", "green", statusRucSpan);

            document.getElementById("telefono").focus();
        } else {
            clearFields(fieldsToClear);
            updateStatus(result.message || "RUC no encontrado.", "red", statusRucSpan);

            document.getElementById("razon_social").focus();

        }
    } catch (error) {
        console.error("Error al buscar RUC:", error);
        clearFields(fieldsToClear);
        updateStatus("Error al consultar RUC", "red", statusRucSpan);
        document.getElementById("razon_social").focus();

    } finally {
        buscarRucBtn.disabled = false;
    }
}
