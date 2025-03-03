from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.test import TestCase
from django.template.loader import render_to_string
from app.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from django.contrib.auth.models import Group

import smtplib


# EMAILS AREA GENERAL

def send_email_to_general():
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Obtener todos los usuarios del grupo 'Jefe_De_Area'
        grupo = Group.objects.get(name='Jefe_De_Area')
        usuarios = grupo.user_set.all()  # Obtener todos los usuarios del grupo
        
        for user in usuarios:
            email_to = user.email
            mensaje = MIMEMultipart()
            mensaje['From'] = EMAIL_HOST_USER
            mensaje['To'] = email_to
            mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
            content = render_to_string('emails/General/nuevo_email_gen.html')
            mensaje.attach(MIMEText(content, 'html'))
            mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
            print(f"Correo enviado a {email_to}")
        
    except Group.DoesNotExist:
        print("El grupo 'Jefe_De_Area' no existe")
    except Exception as e:
        print(f"Error al enviar correos al grupo Jefe_De_Area: {str(e)}")


def send_email_to_user_general(option, user):
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Usar el correo del usuario que creó la solicitud
        email_to = user.email  # Asume que User tiene un campo 'email'
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        
        if option == 1:
            mensaje['Subject'] = "Solicitud aprobada"
            content = render_to_string('emails/General/email_aprobada_gen.html')
        elif option == 0:
            mensaje['Subject'] = "Solicitud rechazada"  # Cambié el mensaje para reflejar la creación
            content = render_to_string('emails/General/email_rechazada_gen.html')  # Ajusta la plantilla si es necesario
        mensaje.attach(MIMEText(content, 'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
        print(f"Correo enviado a {email_to}")
    except Exception as e:
        print(f"Error al enviar correo a {user.email}: {str(e)}")
        


# EMAILS AREA PRESUPUESTOS

def send_email_to_presupuesto():
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Obtener todos los usuarios del grupo 'Jefe_de_Presupuestos'
        grupo = Group.objects.get(name='Jefe_de_Presupuestos')
        usuarios = grupo.user_set.all()  # Obtener todos los usuarios del grupo
        
        for user in usuarios:
            email_to = user.email
            mensaje = MIMEMultipart()
            mensaje['From'] = EMAIL_HOST_USER
            mensaje['To'] = email_to
            mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
            content = render_to_string('emails/Presupuestos/nuevo_email_pre.html')
            mensaje.attach(MIMEText(content, 'html'))
            mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
            print(f"Correo enviado a {email_to}")
        
    except Group.DoesNotExist:
        print("El grupo 'Jefe_de_Presupuestos' no existe")
    except Exception as e:
        print(f"Error al enviar correos al grupo Jefe_de_Presupuestos: {str(e)}")

def send_email_to_user_presupuesto(option, user):
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
        
        email_to = user.email
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        if option == 1:
            mensaje['Subject'] = "Solicitud contabilizada"
            content = render_to_string('emails/Presupuestos/email_aprobada_pre.html')
        elif option == 0:
            mensaje['Subject'] = "Solicitud rechazada"
            content = render_to_string('emails/Presupuestos/email_rechazada_pre.html')
        mensaje.attach(MIMEText(content,'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
        print(f"Correo enviado a {email_to}")
    except Exception as e:
        print(f"Error al enviar correo a {user.email}: {str(e)}")
        
        
        
# EMAILS LOGISTICA        

def send_email_to_logistica():
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Obtener todos los usuarios del grupo 'Jefe_Logistica'
        grupo = Group.objects.get(name='Jefe_Logistica')
        usuarios = grupo.user_set.all()  # Obtener todos los usuarios del grupo
        
        for user in usuarios:
            email_to = user.email
            mensaje = MIMEMultipart()
            mensaje['From'] = EMAIL_HOST_USER
            mensaje['To'] = email_to
            mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
            content = render_to_string('emails/Logistica/nuevo_email_log.html')
            mensaje.attach(MIMEText(content, 'html'))
            mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
            print(f"Correo enviado a {email_to}")
        
    except Group.DoesNotExist:
        print("El grupo 'Jefe_Logistica' no existe")
    except Exception as e:
        print(f"Error al enviar correos al grupo Jefe_Logistica: {str(e)}")

def send_email_to_user_logistica(option, user):
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)

        email_to = user.email
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        if option == 1:
            mensaje['Subject'] = "Tu solicitud ahora es una Orden de Compra"
            content = render_to_string('emails/Logistica/email_aprobada_log.html')
        elif option == 0:
            mensaje['Subject'] = "Solicitud rechazada"
            content = render_to_string('emails/Logistica/email_rechazada_log.html')
        mensaje.attach(MIMEText(content,'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
        print(f"Correo enviado a {email_to}")
    except Exception as e:
        print(e)
        print(f"Error al enviar correo a {user.email}: {str(e)}")