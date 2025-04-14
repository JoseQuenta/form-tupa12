import {
    nombreInput,
    apellidoInput,
    direccionInput,
    distritoInput,
    provinciaInput,
    departamentoInput,
    placaInput
} from './dom-elements.js';

const uppercaseFields = [
    nombreInput,
    apellidoInput,
    direccionInput,
    distritoInput,
    provinciaInput,
    departamentoInput,
    placaInput
];

export function setupUppercaseFields() {
    uppercaseFields.forEach(field => {
        if (field) {
            field.addEventListener('input', (event) => {
                const start = event.target.selectionStart;
                const end = event.target.selectionEnd;
                event.target.value = event.target.value.toUpperCase();
                event.target.setSelectionRange(start, end);
            });
            field.classList.add('uppercase-input');
        }
    });
}