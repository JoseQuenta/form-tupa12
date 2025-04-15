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

import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def enviar_correo_con_adjuntos(destinatario, lista_adjuntos):
    respuesta = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "soycargototal@gmail.com",
        "subject": "Solicitud de TUPA 12 - Habilitación de vehículo",
        "html": """
            <p>Estimados representantes de <strong>SANIPES</strong>,</p>

            <p>Por medio del presente, me dirijo a ustedes para presentar la <strong>solicitud del trámite TUPA 12</strong> correspondiente a la habilitación sanitaria de mi vehículo para el transporte de productos hidrobiológicos.</p>

            <p>Adjunto a este correo encontrarán los siguientes documentos:</p>
            <ul>
                <li>Formulario de solicitud debidamente llenado</li>
                <li>Voucher de pago</li>
                <li>Tarjeta de propiedad del vehículo</li>
                <li>Otros documentos requeridos</li>
            </ul>

            <p>Agradezco de antemano su atención y quedo atento(a) a cualquier observación o requerimiento adicional.</p>

            <p>Saludos cordiales,<br>
            <strong>[Tu nombre completo]</strong><br>
            [DNI o RUC, si corresponde]<br>
            [Teléfono de contacto]<br>
            [Correo electrónico]</p>
        """,
        "attachments": lista_adjuntos
    })

    print("Respuesta de Resend:", respuesta)
