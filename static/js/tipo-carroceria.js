import { carroceriaSelect, campoCarroceriaOtro } from './dom-elements.js';

export function setupTipoCarroceria() {
    if (!carroceriaSelect || !campoCarroceriaOtro) return;

    carroceriaSelect.addEventListener("change", () => {
        campoCarroceriaOtro.style.display = carroceriaSelect.value === "Otros" ? "block" : "none";
    });
}
