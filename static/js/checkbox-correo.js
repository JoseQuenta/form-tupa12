import { sinCorreoCheckbox, correoInput } from './dom-elements.js';

export function setupSinCorreoCheckbox() {
    sinCorreoCheckbox.addEventListener("change", () => {
        if (sinCorreoCheckbox.checked) {
            correoInput.value = "soycargototal@gmail.com";
            correoInput.disabled = true;
            correoInput.required = false;
        } else {
            correoInput.value = "";
            correoInput.disabled = false;
            correoInput.required = true;
        }
    });

    // Estado inicial por si la página se recarga con el checkbox marcado
    if (sinCorreoCheckbox.checked) {
        correoInput.disabled = true;
        correoInput.required = false;
    }
}
