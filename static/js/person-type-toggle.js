import {
    tipoPersona, grupoNatural, grupoJuridica,
    // Persona Natural
    dniInput, nombreInput, apellidoInput, direccionInput,
    distritoInput, provinciaInput, departamentoInput, 
    // Persona Jurídica
    rucInput, razonSocialInput, direccionJurInput,
    distritoJurInput, provinciaJurInput, departamentoJurInput,
    repLegalInput, dniRepLegalInput, // 
    // Spans de estado
    statusSpan, statusRucSpan
} from './dom-elements.js';

export function setupPersonTypeToggle() {
    console.log("setupPersonTypeToggle cargado ✅");
    tipoPersona.addEventListener("change", () => {
        console.log("Cambiando tipo de persona:", tipoPersona.value); // <- deberías ver esto en consola
        const tipo = tipoPersona.value;

        // Quitar "requerido" de los campos
        dniInput.removeAttribute("required");
        rucInput.removeAttribute("required");

        // Limpieza de campos
        const limpiarCampos = (campos) => {
            campos.forEach(campo => campo && (campo.value = ""));
        };

        // Limpieza de mensajes de estado
        const limpiarEstado = () => {
            if (statusSpan) statusSpan.textContent = "";
            if (statusRucSpan) statusRucSpan.textContent = "";
        };

        if (tipo === "natural") {
            grupoNatural.style.display = "block";
            grupoJuridica.style.display = "none";

            limpiarCampos([
                rucInput, razonSocialInput, direccionJurInput,
                distritoJurInput, provinciaJurInput, departamentoJurInput,
                repLegalInput, dniRepLegalInput
            ]);

        } else if (tipo === "juridica") {
            grupoNatural.style.display = "none";
            grupoJuridica.style.display = "block";

            limpiarCampos([
                dniInput, nombreInput, apellidoInput, direccionInput,
                distritoInput, provinciaInput, departamentoInput, 
            ]);

        } else {
            grupoNatural.style.display = "none";
            grupoJuridica.style.display = "none";

            limpiarCampos([
                dniInput, nombreInput, apellidoInput, direccionInput,
                distritoInput, provinciaInput, departamentoInput, 
                rucInput, razonSocialInput, direccionJurInput,
                distritoJurInput, provinciaJurInput, departamentoJurInput,
                repLegalInput, dniRepLegalInput
            ]);
        }

        limpiarEstado(); // 👈 Limpia mensaje de estado al cambiar de tipo
    });
}
