import { form, firmaCanvas, firmaImgInput } from './dom-elements.js';
import { setupUppercaseFields } from './uppercase-fields.js';

export function setupFormSubmission() {
    form.addEventListener("submit", (event) => {
        setupUppercaseFields();

        const blank = document.createElement('canvas');
        blank.width = firmaCanvas.width;
        blank.height = firmaCanvas.height;
        const isCanvasBlank = firmaCanvas.toDataURL() === blank.toDataURL();

        if (isCanvasBlank) {
            alert("Por favor, ingrese su firma.");
            event.preventDefault();
            return;
        }

        firmaImgInput.value = firmaCanvas.toDataURL("image/png");

        
    });
}