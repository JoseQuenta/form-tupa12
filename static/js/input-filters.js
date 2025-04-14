// input-filters.js

import {
    telefonoInput,
    numeroPagoInput,
    cargaUtilInput,
    dniInput,
    // ubigeoInput,
    placaInput
  } from './dom-elements.js';
  
  // --- Filtro para campos NUMÉRICOS ---
  const filterNumericInput = (event) => {
    event.target.value = event.target.value.replace(/[^\d]/g, '');
  };
  
  export function setupNumericInputFilters() {
    telefonoInput.addEventListener('input', filterNumericInput);
    numeroPagoInput.addEventListener('input', filterNumericInput);
    cargaUtilInput.addEventListener('input', filterNumericInput);
    dniInput.addEventListener('input', filterNumericInput);
    // ubigeoInput.addEventListener('input', filterNumericInput);
  }
  
  // --- Formato y Mayúsculas para PLACA ---
  export function setupPlacaInputFormatter() {
    placaInput.addEventListener('input', (event) => {
      let value = event.target.value.toUpperCase();
  
      // Quitar caracteres inválidos (solo letras A-Z y números 0-9)
      value = value.replace(/[^A-Z0-9]/g, '');
  
      // Insertar guion después del 3er carácter si hay más de 3
      if (value.length > 3) {
        value = value.slice(0, 3) + '-' + value.slice(3);
      }
  
      // Limitar longitud total (incluyendo guion)
      if (value.length > 7) {
        value = value.slice(0, 7);
      }
  
      event.target.value = value;
    });
  }