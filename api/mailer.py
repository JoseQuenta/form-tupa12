# import resend
# import os
# resend.api_key = os.getenv("RESEND_API_KEY")

# def enviar_correo_con_adjuntos(destinatario, lista_adjuntos):
#     respuesta = resend.Emails.send({
#         "from": "onboarding@resend.dev",
#         "to": "soycargototal@gmail.com",
#         "subject": "Formulario con múltiples adjuntos",
#         "html": "<p>Hola, te enviamos tu formulario y archivos adjuntos.</p>",
#         "attachments": lista_adjuntos
#     })
#     print("Respuesta de Resend:", respuesta)

from datetime import datetime
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def enviar_correo_con_adjuntos(destinatario, lista_adjuntos, form_data=None):
    nombre = form_data.get("nombre_completo2") or form_data.get("razon_social2", "Estimado(a)")
    placa = form_data.get("placa", "vehículo")
    lugar = form_data.get("lugar_auditoria", "").upper()
    fecha = datetime.now().strftime("%d/%m/%Y")

    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 1rem;">
        <p>Estimados representantes de <strong>SANIPES</strong>,</p>
        <p>Mi nombre es <strong>{nombre}</strong> y por este medio solicito el trámite correspondiente al <strong>TUPA 12</strong> para el vehículo con placa <strong>{placa}</strong>.</p>
        <p>Adjunto el formulario completo junto con los documentos requeridos, a fin de que se proceda con la revisión y auditoría programada en la ciudad de <strong>{lugar}</strong>.</p>
        <p>Quedo atento(a) a cualquier observación o comentario adicional. Agradezco de antemano su atención y apoyo.</p>
        <p>Saludos cordiales,</p>
        <p><strong>{nombre}</strong><br>Enviado el {fecha}</p>
    </div>
    """

    respuesta = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": destinatario,
        "subject": f"Solicitud TUPA 12 - {placa}",
        "html": html,
        "attachments": lista_adjuntos
    })
    print("📧 Correo enviado con Resend:", respuesta)
