import {
    carroceriaSelect,
    campoCarroceriaOtro
} from './dom-elements.js';

export function setupTipoCarroceria() {
    if (!carroceriaSelect || !campoCarroceriaOtro) return;

    // Mostrar/ocultar campo adicional si selecciona "Otros"
    carroceriaSelect.addEventListener("change", () => {
        campoCarroceriaOtro.style.display = carroceriaSelect.value === "Otros" ? "block" : "none";
    });

    // Inyectar el valor final antes de enviar el formulario
    const form = document.getElementById("pdfForm");
    form.addEventListener("submit", () => {
        const otroInput = document.querySelector("#tipo_carroceria_otro");

        // Si se seleccionó "Otros" y hay un valor
        if (carroceriaSelect.value === "Otros" && otroInput?.value.trim()) {
            // Si ya existe un input oculto, lo actualizamos
            let hiddenInput = form.querySelector("input[name='tipo_carroceria']");
            if (!hiddenInput) {
                hiddenInput = document.createElement("input");
                hiddenInput.type = "hidden";
                hiddenInput.name = "tipo_carroceria";
                form.appendChild(hiddenInput);
            }
            hiddenInput.value = otroInput.value.trim();
        } else {
            // Si es una opción del select, lo usamos como valor
            let hiddenInput = form.querySelector("input[name='tipo_carroceria']");
            if (!hiddenInput) {
                hiddenInput = document.createElement("input");
                hiddenInput.type = "hidden";
                hiddenInput.name = "tipo_carroceria";
                form.appendChild(hiddenInput);
            }
            hiddenInput.value = carroceriaSelect.value;
        }
    });
}
