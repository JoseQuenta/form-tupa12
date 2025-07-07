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
    }

    if (buscarRucBtn) {
        buscarRucBtn.addEventListener('click', buscarRuc);
    }

    // Eliminar la siguiente sección obsoleta que busca onclick="limpiarFirma()"
    // const btnLimpiarHtml = document.querySelector('[onclick="limpiarFirma()"]');
    // if (btnLimpiarHtml) {
    //     window.limpiarFirma = limpiarFirma;
    // } else {
    //     console.warn("No se encontró un botón con onclick='limpiarFirma()'. La función no se expondrá globalmente.");
    // }

    // Si el botón de limpiar firma está en el DOM, lo inicializamos
    if (limpiarFirmaBtn) {
        limpiarFirmaBtn.addEventListener('click', limpiarFirma);
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

    // ✅ Inicializa flatpickr correctamente
    flatpickr("#fecha_pago", {
        dateFormat: "d/m/Y",
        locale: 'es',
        allowInput: true
    });
    // Elimina la inicialización de flatpickr aquí, se moverá a un script inline en el HTML

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

        // Permitir zoom con gestos (pinch-zoom y doble click)
        const modalImg = overlay.querySelector('img');
        let scale = 1;
        let lastTouchDist = null;
        let lastX = 0, lastY = 0, isDragging = false;

        // Pinch zoom
        modalImg.addEventListener('touchmove', function (e) {
            if (e.touches.length === 2) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (lastTouchDist) {
                    let delta = dist - lastTouchDist;
                    scale = Math.max(1, Math.min(4, scale + delta / 200));
                    modalImg.style.transform = `scale(${scale})`;
                }
                lastTouchDist = dist;
            }
        });
        modalImg.addEventListener('touchend', function (e) {
            if (e.touches.length < 2) lastTouchDist = null;
        });
        // Doble click para zoom
        modalImg.addEventListener('dblclick', function (e) {
            scale = scale === 1 ? 2 : 1;
            modalImg.style.transform = `scale(${scale})`;
        });
        // Arrastrar imagen
        modalImg.addEventListener('mousedown', function (e) {
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            modalImg.style.cursor = 'grabbing';
        });
        document.addEventListener('mousemove', function (e) {
            if (isDragging) {
                modalImg.parentElement.scrollLeft -= (e.clientX - lastX);
                modalImg.parentElement.scrollTop -= (e.clientY - lastY);
                lastX = e.clientX;
                lastY = e.clientY;
            }
        });
        document.addEventListener('mouseup', function () {
            isDragging = false;
            modalImg.style.cursor = 'grab';
        });

        // Cerrar al hacer click en X o fuera de la imagen
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay || e.target.classList.contains("img-close")) {
                overlay.remove();
                document.body.style.overflow = "";
            }
        });
    });

    // --- Buscar con Enter en DNI/RUC ---
    const dniInput = document.getElementById('dni');
    const buscarDniBtn = document.getElementById('buscarDniBtn');
    if (dniInput && buscarDniBtn) {
        dniInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === 'Search') {
                e.preventDefault();
                buscarDniBtn.click();
            }
        });
    }
    const rucInput = document.getElementById('ruc');
    const buscarRucBtn = document.getElementById('buscarRucBtn');
    if (rucInput && buscarRucBtn) {
        rucInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === 'Search') {
                e.preventDefault();
                buscarRucBtn.click();
            }
        });
    }

    // --- Flatpickr para fecha de pago ---
    const fechaPagoInput = document.getElementById("fecha_pago");
    if (fechaPagoInput) {
        // Configuración para input type="date" nativo
        const hoy = new Date();
        const offset = hoy.getTimezoneOffset();
        const hoyLocal = new Date(hoy.getTime() - (offset * 60 * 1000));
        fechaPagoInput.value = hoyLocal.toISOString().split('T')[0];
        fechaPagoInput.max = hoyLocal.toISOString().split('T')[0];
    }
});
