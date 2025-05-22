/* Flatpickr Spanish locale - es.js (copiado desde CDN)
   Fuente: https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/es.js */

(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
    typeof define === 'function' && define.amd ? define(factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, (global.flatpickr = global.flatpickr || {}).l10ns = (global.flatpickr.l10ns || {}), global.flatpickr.l10ns.es = factory());
})(this, function () {
    "use strict";
    var fp = typeof window !== "undefined" && window.flatpickr !== undefined ? window.flatpickr : { l10ns: {} };
    var Spanish = {
        weekdays: {
            shorthand: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"],
            longhand: [
                "Domingo",
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes",
                "Sábado"
            ]
        },
        months: {
            shorthand: [
                "Ene",
                "Feb",
                "Mar",
                "Abr",
                "May",
                "Jun",
                "Jul",
                "Ago",
                "Sep",
                "Oct",
                "Nov",
                "Dic"
            ],
            longhand: [
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre"
            ]
        },
        firstDayOfWeek: 1,
        ordinal: function () {
            return "º";
        },
        rangeSeparator: " a ",
        weekAbbreviation: "Sem",
        scrollTitle: "Desplazar para aumentar",
        toggleTitle: "Haga clic para alternar",
        amPM: ["AM", "PM"],
        yearAriaLabel: "Año",
        time_24hr: true
    };
    fp.l10ns.es = Spanish;
    return fp.l10ns.es;
});
