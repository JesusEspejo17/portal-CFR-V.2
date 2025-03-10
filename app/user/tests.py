from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.test import TestCase
from django.template.loader import render_to_string
from app.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from django.contrib.auth.models import Group
from erp.models import PRQ1

import smtplib


# EMAILS AREA GENERAL

# def send_email_to_general():
#     try:
#         mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         mailServer.starttls()
#         mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
#         # Obtener todos los usuarios del grupo 'Jefe_De_Area'
#         grupo = Group.objects.get(name='Jefe_De_Area')
#         usuarios = grupo.user_set.all()  # Obtener todos los usuarios del grupo
        
#         for user in usuarios:
#             email_to = user.email
#             mensaje = MIMEMultipart()
#             mensaje['From'] = EMAIL_HOST_USER
#             mensaje['To'] = email_to
#             mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
#             content = render_to_string('emails/General/nuevo_email_gen.html')
#             mensaje.attach(MIMEText(content, 'html'))
#             mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
#             print(f"Correo enviado a {email_to}")
        
#     except Group.DoesNotExist:
#         print("El grupo 'Jefe_De_Area' no existe")
#     except Exception as e:
#         print(f"Error al enviar correos al grupo Jefe_De_Area: {str(e)}")


# def send_email_to_user_general(option, user):
#     try:
#         mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         mailServer.starttls()
#         mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
#         # Usar el correo del usuario que creó la solicitud
#         email_to = user.email  # Asume que User tiene un campo 'email'
#         mensaje = MIMEMultipart()
#         mensaje['From'] = EMAIL_HOST_USER
#         mensaje['To'] = email_to
        
#         if option == 1:
#             mensaje['Subject'] = "Solicitud aprobada"
#             content = render_to_string('emails/General/email_aprobada_gen.html')
#         elif option == 0:
#             mensaje['Subject'] = "Solicitud rechazada"  # Cambié el mensaje para reflejar la creación
#             content = render_to_string('emails/General/email_rechazada_gen.html')  # Ajusta la plantilla si es necesario
#         mensaje.attach(MIMEText(content, 'html'))
#         mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
#         print(f"Correo enviado a {email_to}")
#     except Exception as e:
#         print(f"Error al enviar correo a {user.email}: {str(e)}")
        

# EMAILS AREA GENERAL
def send_email_to_general(solicitud):  # Añadimos el argumento solicitud
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Obtener todos los usuarios del grupo 'Jefe_De_Area'
        grupo = Group.objects.get(name='Jefe_De_Area')
        usuarios = grupo.user_set.all()
        
        for user in usuarios:
            email_to = user.email
            mensaje = MIMEMultipart()
            mensaje['From'] = EMAIL_HOST_USER
            mensaje['To'] = email_to
            mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
            
            # Obtener los detalles de PRQ1 asociados a la solicitud (OPRQ)
            detalles = PRQ1.objects.filter(NumDoc=solicitud).select_related('ItemCode')
            
            # Preparar los datos de los detalles para el contexto
            detalles_lista = []
            for detalle in detalles:
                detalles_lista.append({
                    'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                    'description': detalle.Description,
                    'quantity': detalle.Quantity,
                    'precio': detalle.Precio,
                    'total': detalle.total,
                    'totalimpdet': detalle.totalimpdet,
                })
            
            # Contexto con datos de la solicitud y los detalles
            contexto = {
                'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud.ReqIdUser else "Desconocido",
                'tipo_documento': solicitud.DocType,
                'moneda': solicitud.moneda.MonedaAbrev if solicitud.moneda else "No especificada",
                'tax_code': solicitud.TaxCode.Code if solicitud.TaxCode else "No especificado",
                'doc_entry': solicitud.DocEntry,  # DocEntry de la solicitud
                'detalles': detalles_lista  # Lista de detalles para la tabla
            }
            content = render_to_string('emails/General/nuevo_email_gen.html', contexto)
            mensaje.attach(MIMEText(content, 'html'))
            mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
            print(f"Correo enviado a {email_to}")
        
    except Group.DoesNotExist:
        print("El grupo 'Jefe_De_Area' no existe")
    except Exception as e:
        print(f"Error al enviar correos al grupo Jefe_De_Area: {str(e)}")

# Resto de las funciones (send_email_to_user_general, etc.) pueden ajustarse de manera similar si lo necesitas
def send_email_to_user_general(option, user, solicitud=None):
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        email_to = user.email
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        
        if option == 1:
            mensaje['Subject'] = "Solicitud aprobada"
            contexto = {
                'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud and solicitud.ReqIdUser else user.username,
                'tipo_documento': solicitud.DocType if solicitud else "No especificado",
                'moneda': solicitud.moneda.MonedaAbrev if solicitud and solicitud.moneda else "No especificada",
                'tax_code': solicitud.TaxCode.Code if solicitud and solicitud.TaxCode else "No especificado"
            }
            content = render_to_string('emails/General/email_aprobada_gen.html', contexto)
        elif option == 0:
            mensaje['Subject'] = "Solicitud rechazada"
            contexto = {
                'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud and solicitud.ReqIdUser else user.username,
                'tipo_documento': solicitud.DocType if solicitud else "No especificado",
                'moneda': solicitud.moneda.MonedaAbrev if solicitud and solicitud.moneda else "No especificada",
                'tax_code': solicitud.TaxCode.Code if solicitud and solicitud.TaxCode else "No especificado"
            }
            content = render_to_string('emails/General/email_rechazada_gen.html', contexto)
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