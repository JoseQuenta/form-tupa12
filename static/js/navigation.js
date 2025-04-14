// export function setupNavigation() {
//     btnSiguiente.addEventListener("click", () => {
//         pagina1.style.display = "none";
//         pagina2.style.display = "block";
//         btnSiguiente.style.display = "none";
//         btnAnterior.style.display = "inline-block";
//         btnEnviar.style.display = "inline-block";
//     });

//     btnAnterior.addEventListener("click", () => {
//         pagina1.style.display = "block";
//         pagina2.style.display = "none";
//         btnSiguiente.style.display = "inline-block";
//         btnAnterior.style.display = "none";
//         btnEnviar.style.display = "none";
//     });
// }
import {
    pagina1, pagina2,
    btnSiguiente, btnAnterior, btnEnviar,
    tipoPersona,

    // Persona Natural
    dniInput, nombreInput, apellidoInput, direccionInput,
    distritoInput, provinciaInput, departamentoInput, 

    // Persona Jurídica
    rucInput, razonSocialInput, direccionJurInput,
    distritoJurInput, provinciaJurInput, departamentoJurInput,
    repLegalInput, dniRepLegalInput,

    // Comunes
    telefonoInput, correoInput, sinCorreoCheckbox,

    // Página 2
    numeroPagoInput
} from './dom-elements.js';

function validarPagina1() {
    const tipo = tipoPersona.value;
    const errores = [];

    if (!tipo) {
        errores.push("Debes seleccionar el tipo de persona.");
        return errores;
    }

    if (tipo === "natural") {
        if (!dniInput.value.trim()) errores.push("DNI es obligatorio.");
        if (!nombreInput.value.trim()) errores.push("Nombre es obligatorio.");
        if (!apellidoInput.value.trim()) errores.push("Apellido es obligatorio.");
        if (!direccionInput.value.trim()) errores.push("Dirección es obligatoria.");
        if (!distritoInput.value.trim()) errores.push("Distrito es obligatorio.");
        if (!provinciaInput.value.trim()) errores.push("Provincia es obligatoria.");
        if (!departamentoInput.value.trim()) errores.push("Departamento es obligatorio.");
    }

    if (tipo === "juridica") {
        if (!rucInput.value.trim()) errores.push("RUC es obligatorio.");
        if (!razonSocialInput.value.trim()) errores.push("Razón Social es obligatoria.");
        if (!repLegalInput.value.trim()) errores.push("Representante legal es obligatorio.");
        if (!dniRepLegalInput.value.trim()) errores.push("DNI del representante es obligatorio.");
        if (!direccionJurInput.value.trim()) errores.push("Dirección de la empresa es obligatoria.");
        if (!distritoJurInput.value.trim()) errores.push("Distrito es obligatorio.");
        if (!provinciaJurInput.value.trim()) errores.push("Provincia es obligatoria.");
        if (!departamentoJurInput.value.trim()) errores.push("Departamento es obligatorio.");
    }

    if (!telefonoInput.value.trim()) errores.push("Teléfono es obligatorio.");

    if (!sinCorreoCheckbox.checked && !correoInput.value.trim()) {
        errores.push("Debe ingresar un correo o marcar 'No tengo correo'.");
    }

    return errores;
}

export function setupNavigation() {
    if (btnSiguiente) {
        btnSiguiente.addEventListener('click', () => {
            const errores = validarPagina1();
            if (errores.length > 0) {
                alert("⚠️ Por favor completa:\n\n" + errores.join("\n"));
                return;
            }

            pagina1.style.display = "none";
            pagina2.style.display = "block";
            btnSiguiente.style.display = "none";
            btnAnterior.style.display = "inline-block";
            btnEnviar.style.display = "inline-block";

            // ✅ Enfocar el campo 'número de pago'
            if (numeroPagoInput) numeroPagoInput.focus();
        });
    }

    if (btnAnterior) {
        btnAnterior.addEventListener('click', () => {
            pagina2.style.display = "none";
            pagina1.style.display = "block";
            btnSiguiente.style.display = "inline-block";
            btnAnterior.style.display = "none";
            btnEnviar.style.display = "none";

            // Enfocar nuevamente tipo_persona o DNI
            if (tipoPersona.value === "natural" && dniInput) dniInput.focus();
            else if (tipoPersona.value === "juridica" && rucInput) rucInput.focus();
        });
    }
}


export { validarPagina1 }; // Al final del archivo
