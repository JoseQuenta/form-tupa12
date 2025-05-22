// --- Imports ---
import { setupNavigation } from './navigation.js';
import { setupPersonTypeToggle } from './person-type-toggle.js';
import { setupSinCorreoCheckbox } from './checkbox-correo.js';
import { setupNumericInputFilters, setupPlacaInputFormatter } from './input-filters.js';
import { setupUppercaseFields } from './uppercase-fields.js';
import { setupFirmaCanvas } from './firma-canvas.js';
import { setupFormSubmission } from './form-submission.js';

import { buscarDni, buscarRuc } from './api-handlers.js';
import { limpiarFirma } from './firma-canvas.js';
import { limpiarFirmaBtn } from './dom-elements.js'; // Asegúrate que exportas esto
import { buscarDniBtn, buscarRucBtn } from './dom-elements.js';
import { btnLimpiar } from './dom-elements.js';

import { btnEditar } from './dom-elements.js'; // Asegúrate que exportas esto
import { btnNuevo } from './dom-elements.js'; // Asegúrate que exportas esto

import { setupTipoCarroceria } from './tipo-carroceria.js';

// import { setupFlatpickr } from './setup-flatpickr.js';

import {
    dniInput,
    nombreInput,
    apellidoInput,
    direccionInput,
    distritoInput,
    provinciaInput,
    departamentoInput,
    rucInput,
    razonSocialInput,
    direccionJurInput,
    distritoJurInput,
    provinciaJurInput,
    departamentoJurInput,
    repLegalInput,
    dniRepLegalInput,
    telefonoInput,
    correoInput,

    numeroPagoInput,
    fechaPagoInput,
    placaInput,
    cargaUtilInput,

    pagina1,
    pagina2,
    btnAnterior,
    btnSiguiente,
    btnEnviar,
    sinCorreoCheckbox,
    tipoPersona,

} from './dom-elements.js';

// --- Lógica Principal ---
document.addEventListener("DOMContentLoaded", () => {
    setupNavigation();
    setupPersonTypeToggle();
    setupSinCorreoCheckbox();
    setupNumericInputFilters();
    setupPlacaInputFormatter();
    setupUppercaseFields();
    setupFirmaCanvas();
    setupFormSubmission();
    setupTipoCarroceria();
    // setupFlatpickr();

    if (buscarDniBtn) {
        buscarDniBtn.addEventListener('click', buscarDni);
    } else {
        console.warn("Botón buscarDniBtn no encontrado en el DOM.");
    }

    if (buscarRucBtn) {
        buscarRucBtn.addEventListener('click', buscarRuc);
    } else {
        console.warn("Botón buscarRucBtn no encontrado en el DOM.");
    }

    const btnLimpiarHtml = document.querySelector('[onclick="limpiarFirma()"]');
    if (btnLimpiarHtml) {
        window.limpiarFirma = limpiarFirma;
    } else {
        console.warn("No se encontró un botón con onclick='limpiarFirma()'. La función no se expondrá globalmente.");
    }

    // Si el botón de limpiar firma está en el DOM, lo inicializamos
    if (limpiarFirmaBtn) {
        limpiarFirmaBtn.addEventListener('click', limpiarFirma);
    } else {
        console.warn("Botón limpiarFirmaBtn no encontrado en el DOM.");
    }

    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', () => {
            const allFields = [
                dniInput, nombreInput, apellidoInput, direccionInput, distritoInput,
                provinciaInput, departamentoInput, rucInput, razonSocialInput,
                direccionJurInput, distritoJurInput, provinciaJurInput, departamentoJurInput,
                repLegalInput, dniRepLegalInput, telefonoInput, correoInput, 
                numeroPagoInput, fechaPagoInput, placaInput, cargaUtilInput
            ];
            allFields.forEach(field => field && (field.value = ""));
            sinCorreoCheckbox.checked = false;
            tipoPersona.value = ""; // reinicia el selector
            document.getElementById("grupo_natural").style.display = "none";
            document.getElementById("grupo_juridica").style.display = "none";

            // Limpia el canvas de firma
            limpiarFirma();

            document.getElementById("pagina1").style.display = "block";
            document.getElementById("pagina2").style.display = "none";
            document.getElementById("btnSiguiente").style.display = "inline-block";
            document.getElementById("btnAnterior").style.display = "none";
            document.getElementById("btnEnviar").style.display = "none";
        });
    }

    if (btnEditar) {
        btnEditar.addEventListener("click", () => {
            document.getElementById("pantallaExito").style.display = "none";
            document.getElementById("pdfForm").style.display = "block";
            // Puedes mantener los datos o ir a una sección específica
        });
    }
    
    if (btnNuevo) {
        btnNuevo.addEventListener("click", () => {
            window.location.reload(); // recarga todo y limpia
        });
    }


    const dropzone = document.getElementById('dropzone');
    const input = document.getElementById('adjuntos');
    const fileList = document.getElementById('fileList');

    dropzone.addEventListener('click', () => input.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('highlight');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('highlight');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        input.files = e.dataTransfer.files;
        mostrarArchivos(input.files);
    });

    input.addEventListener('change', () => {
        mostrarArchivos(input.files);
    });

    function mostrarArchivos(files) {
        fileList.innerHTML = "";
        for (let i = 0; i < files.length; i++) {
            fileList.innerHTML += `<div>📎 ${files[i].name}</div>`;
        }
    };

     // ✅ Inicializa flatpickr correctamente para Fecha de Pago
     if (window.flatpickr) {
        flatpickr("#fecha_pago", {
            dateFormat: "d/m/Y",
            locale: "es",
            allowInput: true,
            defaultDate: new Date(), // Siempre el día actual
        });
    } else {
        console.warn("Flatpickr no está cargado.");
    }

    // const selectCarroceria = document.getElementById("carroceria_select");
    // const campoOtro = document.getElementById("campo_carroceria_otro");

    // selectCarroceria.addEventListener("change", function () {
    //     if (this.value === "Otros") {
    //         campoOtro.style.display = "block";
    //     } else {
    //         campoOtro.style.display = "none";
    //         // Limpiar si el usuario cambia de idea
    //         document.getElementById("tipo_carroceria_otro").value = "";
    //     }
    // });


});

// --- Imagen expandible ---
document.addEventListener("DOMContentLoaded", () => {
    const img = document.querySelector('img[src$="pagosanipes.png"]');
    if (!img) return;

    img.style.cursor = "zoom-in";

    img.addEventListener("click", function () {
        // Crea el overlay y la imagen expandida
        const overlay = document.createElement("div");
        overlay.className = "img-overlay";
        overlay.innerHTML = `
            <div class="img-modal">
                <button class="img-close" aria-label="Cerrar">&times;</button>
                <img src="${img.src}" alt="Pago SANIPES" />
            </div>
        `;
        document.body.appendChild(overlay);
        document.body.style.overflow = "hidden";

        // Cerrar al hacer click en X o fuera de la imagen
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay || e.target.classList.contains("img-close")) {
                overlay.remove();
                document.body.style.overflow = "";
            }
        });
    });
});
