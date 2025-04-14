import { firmaCanvas, firmaImgInput } from './dom-elements.js';

export function setupFirmaCanvas() {
    const ctx = firmaCanvas.getContext("2d");
    ctx.lineCap = "round";
    ctx.strokeStyle = "black";

    let dibujando = false;
    let lastPoint = null;
    let lastTime = null;
    let lastLineWidth = 2;

    const smoothing = 0.2; // suavizado del grosor para evitar saltos bruscos

    const getPosicion = (e) => {
        const rect = firmaCanvas.getBoundingClientRect();
        let clientX = e.clientX;
        let clientY = e.clientY;
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        }
        return { x: clientX - rect.left, y: clientY - rect.top };
    };

    const getLineWidth = (currentTime, currentPoint, lastPoint, lastTime) => {
        if (!lastPoint || !lastTime) return lastLineWidth;
        const dx = currentPoint.x - lastPoint.x;
        const dy = currentPoint.y - lastPoint.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const dt = currentTime - lastTime;
        const speed = distance / (dt || 1);
        const maxLineWidth = 3.5;
        const minLineWidth = 1;
        let newLineWidth = Math.max(minLineWidth, maxLineWidth - speed * 2);
        newLineWidth = lastLineWidth * (1 - smoothing) + newLineWidth * smoothing;
        lastLineWidth = newLineWidth;
        return newLineWidth;
    };

    const startDrawing = (e) => {
        e.preventDefault();
        dibujando = true;
        lastPoint = getPosicion(e);
        lastTime = Date.now();
        if (e.touches) {
            ctx.beginPath();
            ctx.arc(lastPoint.x, lastPoint.y, lastLineWidth / 2, 0, Math.PI * 2);
            ctx.fillStyle = ctx.strokeStyle;
            ctx.fill();
        }
    };

    const draw = (e) => {
        if (!dibujando) return;
        e.preventDefault();
        const currentPoint = getPosicion(e);
        const currentTime = Date.now();

        if (lastPoint) {
            const lineWidth = getLineWidth(currentTime, currentPoint, lastPoint, lastTime);
            ctx.lineWidth = lineWidth;
            ctx.beginPath();
            ctx.moveTo(lastPoint.x, lastPoint.y);
            ctx.lineTo(currentPoint.x, currentPoint.y);
            ctx.stroke();
        }

        lastPoint = currentPoint;
        lastTime = currentTime;
    };

    const stopDrawing = () => {
        dibujando = false;
        lastPoint = null;
        lastTime = null;
    };

    firmaCanvas.addEventListener("mousedown", startDrawing);
    firmaCanvas.addEventListener("mousemove", draw);
    firmaCanvas.addEventListener("mouseup", stopDrawing);
    firmaCanvas.addEventListener("mouseleave", stopDrawing);

    firmaCanvas.addEventListener("touchstart", startDrawing);
    firmaCanvas.addEventListener("touchmove", draw);
    firmaCanvas.addEventListener("touchend", stopDrawing);
    firmaCanvas.addEventListener("touchcancel", stopDrawing);

    }

export function limpiarFirma() {
    const ctx = firmaCanvas.getContext("2d");
    ctx.clearRect(0, 0, firmaCanvas.width, firmaCanvas.height);
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "black";
    firmaImgInput.value = "";
}
