import resend
import os
resend.api_key = os.getenv("RESEND_API_KEY")

def enviar_correo_con_adjuntos(destinatario, lista_adjuntos):
    respuesta = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "soycargototal@gmail.com",
        "subject": "Formulario con múltiples adjuntos",
        "html": "<p>Hola, te enviamos tu formulario y archivos adjuntos.</p>",
        "attachments": lista_adjuntos
    })
    print("Respuesta de Resend:", respuesta)