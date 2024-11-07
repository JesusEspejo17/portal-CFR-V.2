from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.test import TestCase
from django.template.loader import render_to_string
from app.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

import smtplib

# Create your tests here.

def send_email_to_validator():
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
        # email_to = 'pasaloalaprimera.informes@gmail.com'
        email_to = 'fortymone9@gmail.com'
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        mensaje['Subject'] = "Tienes un correo"
        content = render_to_string('emails/new-email.html')
        mensaje.attach(MIMEText(content,'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
    except Exception as e:
        print(e)

def send_email_to_user(option):
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
        # email_to = 'pasaloalaprimera.informes@gmail.com'
        email_to = 'fortymone9@gmail.com'
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        if option == 1:
            mensaje['Subject'] = "Solicitud aprobada"
            content = render_to_string('emails/email_solicitud_aprobada.html')
        elif option == 0:
            mensaje['Subject'] = "Solicitud rechazada"
            content = render_to_string('emails/email_solicitud_rechazada.html')
        mensaje.attach(MIMEText(content,'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
    except Exception as e:
        print(e)