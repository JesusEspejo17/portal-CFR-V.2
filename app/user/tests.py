from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.test import TestCase
from django.template.loader import render_to_string
from app.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from django.contrib.auth.models import Group
from erp.models import PRQ1

import smtplib


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
        

def send_email_to_user_general(option, user, solicitud):  # Añadimos el parámetro solicitud
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        email_to = user.email
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        
        # Preparar el contexto base que será común para ambos casos
        contexto = {
            'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud.ReqIdUser else "Desconocido",
            'tipo_documento': solicitud.DocType,
            'moneda': solicitud.moneda.MonedaAbrev if solicitud.moneda else "No especificada",
            'tax_code': solicitud.TaxCode.Code if solicitud.TaxCode else "No especificado",
            'doc_entry': solicitud.DocEntry,
        }

        if option == 1:
            mensaje['Subject'] = "Solicitud aprobada"
            
            # Obtener los detalles aprobados y rechazados
            detalles_aprobados = PRQ1.objects.filter(
                NumDoc=solicitud,
                LineStatus='A'
            ).select_related('ItemCode')
            
            detalles_rechazados = PRQ1.objects.filter(
                NumDoc=solicitud,
                LineStatus='R'
            ).select_related('ItemCode')
            
            # Preparar las listas de detalles
            detalles_aprobados_lista = []
            for detalle in detalles_aprobados:
                detalles_aprobados_lista.append({
                    'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                    'description': detalle.Description,
                    'quantity': detalle.Quantity,
                    'precio': detalle.Precio,
                    'total': detalle.total,
                    'totalimpdet': detalle.totalimpdet,
                })
            
            detalles_rechazados_lista = []
            for detalle in detalles_rechazados:
                detalles_rechazados_lista.append({
                    'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                    'description': detalle.Description,
                    'quantity': detalle.Quantity,
                    'precio': detalle.Precio,
                    'total': detalle.total,
                    'totalimpdet': detalle.totalimpdet,
                })
            
            # Agregar los detalles al contexto
            contexto.update({
                'detalles_aprobados': detalles_aprobados_lista,
                'detalles_rechazados': detalles_rechazados_lista
            })
            
            content = render_to_string('emails/General/email_aprobada_gen.html', contexto)
        elif option == 0:
            mensaje['Subject'] = "Solicitud rechazada"
            
            # Obtener conteos de estados
            total_items = PRQ1.objects.filter(NumDoc=solicitud).count()
            items_rechazados = PRQ1.objects.filter(NumDoc=solicitud, LineStatus='R').count()
            
            # Determinar si es rechazo total o parcial
            contexto['es_rechazo_total'] = (total_items == items_rechazados)
            
            # Obtener detalles rechazados
            detalles_rechazados = PRQ1.objects.filter(
                NumDoc=solicitud,
                LineStatus='R'
            ).select_related('ItemCode')
            
            detalles_rechazados_lista = []
            for detalle in detalles_rechazados:
                detalles_rechazados_lista.append({
                    'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                    'description': detalle.Description,
                    'quantity': detalle.Quantity,
                    'precio': detalle.Precio,
                    'total': detalle.total,
                    'totalimpdet': detalle.totalimpdet,
                })
            
            contexto['detalles_rechazados'] = detalles_rechazados_lista
            
            content = render_to_string('emails/General/email_rechazada_gen.html', contexto)
            
            
        mensaje.attach(MIMEText(content, 'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
        print(f"Correo enviado a {email_to}")
    except Exception as e:
        print(f"Error al enviar correo a {user.email}: {str(e)}")











# EMAILS AREA PRESUPUESTOS

# def send_email_to_presupuesto():
#     try:
#         mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         mailServer.starttls()
#         mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
#         # Obtener todos los usuarios del grupo 'Jefe_de_Presupuestos'
#         grupo = Group.objects.get(name='Jefe_de_Presupuestos')
#         usuarios = grupo.user_set.all()  # Obtener todos los usuarios del grupo
        
#         for user in usuarios:
#             email_to = user.email
#             mensaje = MIMEMultipart()
#             mensaje['From'] = EMAIL_HOST_USER
#             mensaje['To'] = email_to
#             mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
#             content = render_to_string('emails/Presupuestos/nuevo_email_pre.html')
#             mensaje.attach(MIMEText(content, 'html'))
#             mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
#             print(f"Correo enviado a {email_to}")
        
#     except Group.DoesNotExist:
#         print("El grupo 'Jefe_de_Presupuestos' no existe")
#     except Exception as e:
#         print(f"Error al enviar correos al grupo Jefe_de_Presupuestos: {str(e)}")

def send_email_to_presupuesto(solicitud):  # Añadimos el parámetro solicitud
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Obtener todos los usuarios del grupo 'Jefe_de_Presupuestos'
        grupo = Group.objects.get(name='Jefe_de_Presupuestos')
        usuarios = grupo.user_set.all()
        
        # Obtener solo los detalles aprobados
        detalles_aprobados = PRQ1.objects.filter(
            NumDoc=solicitud,
            LineStatus='A'
        ).select_related('ItemCode')
        
        # Preparar la lista de detalles aprobados
        detalles_aprobados_lista = []
        for detalle in detalles_aprobados:
            detalles_aprobados_lista.append({
                'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                'description': detalle.Description,
                'quantity': detalle.Quantity,
                'precio': detalle.Precio,
                'total': detalle.total,
                'totalimpdet': detalle.totalimpdet,
            })
        
        # Contexto con datos de la solicitud y los detalles aprobados
        contexto = {
            'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud.ReqIdUser else "Desconocido",
            'tipo_documento': solicitud.DocType,
            'moneda': solicitud.moneda.MonedaAbrev if solicitud.moneda else "No especificada",
            'tax_code': solicitud.TaxCode.Code if solicitud.TaxCode else "No especificado",
            'doc_entry': solicitud.DocEntry,
            'detalles_aprobados': detalles_aprobados_lista
        }
        
        for user in usuarios:
            email_to = user.email
            mensaje = MIMEMultipart()
            mensaje['From'] = EMAIL_HOST_USER
            mensaje['To'] = email_to
            mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
            content = render_to_string('emails/Presupuestos/nuevo_email_pre.html', contexto)
            mensaje.attach(MIMEText(content, 'html'))
            mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
            print(f"Correo enviado a {email_to}")
        
    except Group.DoesNotExist:
        print("El grupo 'Jefe_de_Presupuestos' no existe")
    except Exception as e:
        print(f"Error al enviar correos al grupo Jefe_de_Presupuestos: {str(e)}")




# def send_email_to_user_presupuesto(option, user):
#     try:
#         mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         mailServer.starttls()
#         mailServer.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
        
#         email_to = user.email
#         mensaje = MIMEMultipart()
#         mensaje['From'] = EMAIL_HOST_USER
#         mensaje['To'] = email_to
#         if option == 1:
#             mensaje['Subject'] = "Solicitud contabilizada"
#             content = render_to_string('emails/Presupuestos/email_aprobada_pre.html')
#         elif option == 0:
#             mensaje['Subject'] = "Solicitud rechazada"
#             content = render_to_string('emails/Presupuestos/email_rechazada_pre.html')
#         mensaje.attach(MIMEText(content,'html'))
#         mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
#         print(f"Correo enviado a {email_to}")
#     except Exception as e:
#         print(f"Error al enviar correo a {user.email}: {str(e)}")


def send_email_to_user_presupuesto(option, user, solicitud):
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        email_to = user.email
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to
        
        # Contexto base común
        contexto = {
            'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud.ReqIdUser else "Desconocido",
            'tipo_documento': solicitud.DocType,
            'moneda': solicitud.moneda.MonedaAbrev if solicitud.moneda else "No especificada",
            'tax_code': solicitud.TaxCode.Code if solicitud.TaxCode else "No especificado",
            'doc_entry': solicitud.DocEntry,
        }

        if option == 1:
            mensaje['Subject'] = "Solicitud contabilizada"
            
            # Obtener detalles contabilizados (L)
            detalles_contabilizados = PRQ1.objects.filter(
                NumDoc=solicitud,
                LineStatus='L'
            ).select_related('ItemCode')
            
            # Obtener detalles pendientes (A)
            detalles_pendientes = PRQ1.objects.filter(
                NumDoc=solicitud,
                LineStatus='A'
            ).select_related('ItemCode')
            
            # Obtener detalles rechazados (usando el nuevo campo LineRechazo)
            detalles_rechazados = PRQ1.objects.filter(
                NumDoc=solicitud,
                LineStatus='R',
                LineRechazo='RP'  # Solo los rechazados por presupuesto
            ).select_related('ItemCode')
            
            # Preparar las listas de detalles
            def prepare_details_list(detalles):
                return [{
                    'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                    'description': detalle.Description,
                    'quantity': detalle.Quantity,
                    'precio': detalle.Precio,
                    'total': detalle.total,
                    'totalimpdet': detalle.totalimpdet,
                } for detalle in detalles]
            
            contexto.update({
                'detalles_contabilizados': prepare_details_list(detalles_contabilizados),
                'detalles_pendientes': prepare_details_list(detalles_pendientes),
                'detalles_rechazados': prepare_details_list(detalles_rechazados)
            })
            
            content = render_to_string('emails/Presupuestos/email_aprobada_pre.html', contexto)
            
        elif option == 0:
            mensaje['Subject'] = "Solicitud rechazada"
            
            # Obtener conteos de estados, solo considerando los rechazos de presupuesto
            total_items = PRQ1.objects.filter(NumDoc=solicitud).count()
            items_rechazados = PRQ1.objects.filter(
                NumDoc=solicitud, 
                LineStatus='R',
                LineRechazo='RP'  # Solo los rechazados por presupuesto
            ).count()
            
            # Determinar si es rechazo total o parcial
            contexto['es_rechazo_total'] = (total_items == items_rechazados)
            
            # Obtener detalles rechazados por presupuesto
            detalles_rechazados = PRQ1.objects.filter(
                NumDoc=solicitud,
                LineStatus='R',
                LineRechazo='RP'  # Solo los rechazados por presupuesto
            ).select_related('ItemCode')
            
            # Preparar la lista de detalles rechazados
            detalles_rechazados_lista = [{
                'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                'description': detalle.Description,
                'quantity': detalle.Quantity,
                'precio': detalle.Precio,
                'total': detalle.total,
                'totalimpdet': detalle.totalimpdet,
            } for detalle in detalles_rechazados]
            
            contexto['detalles_rechazados'] = detalles_rechazados_lista
            
            content = render_to_string('emails/Presupuestos/email_rechazada_pre.html', contexto)
            
        mensaje.attach(MIMEText(content, 'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
        print(f"Correo enviado a {email_to}")
    except Exception as e:
        print(f"Error al enviar correo a {user.email}: {str(e)}")









# EMAILS LOGISTICA        
# def send_email_to_logistica():
#     try:
#         mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         mailServer.starttls()
#         mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
#         # Obtener todos los usuarios del grupo 'Jefe_Logistica'
#         grupo = Group.objects.get(name='Jefe_Logistica')
#         usuarios = grupo.user_set.all()  # Obtener todos los usuarios del grupo
        
#         for user in usuarios:
#             email_to = user.email
#             mensaje = MIMEMultipart()
#             mensaje['From'] = EMAIL_HOST_USER
#             mensaje['To'] = email_to
#             mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
#             content = render_to_string('emails/Logistica/nuevo_email_log.html')
#             mensaje.attach(MIMEText(content, 'html'))
#             mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
#             print(f"Correo enviado a {email_to}")
        
#     except Group.DoesNotExist:
#         print("El grupo 'Jefe_Logistica' no existe")
#     except Exception as e:
#         print(f"Error al enviar correos al grupo Jefe_Logistica: {str(e)}")


def send_email_to_logistica(solicitud):  # Añadimos el parámetro solicitud
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Obtener todos los usuarios del grupo 'Jefe_Logistica'
        grupo = Group.objects.get(name='Jefe_Logistica')
        usuarios = grupo.user_set.all()
        
        # Obtener los detalles en logística (L)
        detalles_logistica = PRQ1.objects.filter(
            NumDoc=solicitud,
            LineStatus='L'
        ).select_related('ItemCode')
        
        # Obtener los detalles pendientes (A)
        detalles_pendientes = PRQ1.objects.filter(
            NumDoc=solicitud,
            LineStatus='A'
        ).select_related('ItemCode')
        
        # Preparar las listas de detalles
        def prepare_details_list(detalles):
            return [{
                'code': detalle.ItemCode.ItemCode if detalle.ItemCode else "No especificado",
                'description': detalle.Description,
                'quantity': detalle.Quantity,
                'precio': detalle.Precio,
                'total': detalle.total,
                'totalimpdet': detalle.totalimpdet,
            } for detalle in detalles]
        
        # Contexto con datos de la solicitud y los detalles
        contexto = {
            'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud.ReqIdUser else "Desconocido",
            'tipo_documento': solicitud.DocType,
            'moneda': solicitud.moneda.MonedaAbrev if solicitud.moneda else "No especificada",
            'tax_code': solicitud.TaxCode.Code if solicitud.TaxCode else "No especificado",
            'doc_entry': solicitud.DocEntry,
            'detalles_logistica': prepare_details_list(detalles_logistica),
            'detalles_pendientes': prepare_details_list(detalles_pendientes)
        }
        
        for user in usuarios:
            email_to = user.email
            mensaje = MIMEMultipart()
            mensaje['From'] = EMAIL_HOST_USER
            mensaje['To'] = email_to
            mensaje['Subject'] = "Tienes un correo del Portal de Requerimientos"
            content = render_to_string('emails/Logistica/nuevo_email_log.html', contexto)
            mensaje.attach(MIMEText(content, 'html'))
            mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
            print(f"Correo enviado a {email_to}")
        
    except Group.DoesNotExist:
        print("El grupo 'Jefe_Logistica' no existe")
    except Exception as e:
        print(f"Error al enviar correos al grupo Jefe_Logistica: {str(e)}")





def send_email_to_user_logistica(option, user, solicitud):
    try:
        mailServer = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        mailServer.starttls()
        mailServer.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        email_to = user.email
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_HOST_USER
        mensaje['To'] = email_to

        if option == 1:
            mensaje['Subject'] = "Tu solicitud ahora es una Orden de Compra"
            
            # Corregido: usando ItemCodeOCD en lugar de ItemCode
            detalles_oc = OCD1.objects.filter(
                BaseEntryOCD=solicitud.DocNumSAP
            ).select_related('ItemCodeOCD')  # Cambiado aquí
            
            # Preparar la lista de detalles
            detalles_lista = []
            for detalle in detalles_oc:
                detalles_lista.append({
                    'code': detalle.ItemCodeOCD.ItemCode if detalle.ItemCodeOCD else "No especificado",  # Cambiado aquí
                    'description': detalle.DescriptionOCD,
                    'quantity': detalle.QuantityOCD,
                    'precio': detalle.PrecioOCD,
                    'total': detalle.totalOCD,
                    # 'totalimpdet': detalles_oc.totalimpdetOCD,   PENDIENTE AGREGAR AL MODELO OCD1 ESTE CAMPO, MODIFICAR GUARDADO QUE * POR RATE
                })
            
            # Contexto con datos de la solicitud y los detalles
            contexto = {
                'nombre_empleado': f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}" if solicitud.ReqIdUser else "Desconocido",
                'tipo_documento': solicitud.DocType,
                'moneda': solicitud.moneda.MonedaAbrev if solicitud.moneda else "No especificada",
                'tax_code': solicitud.TaxCode.Code if solicitud.TaxCode else "No especificado",
                'doc_entry': solicitud.DocEntry,
                'doc_num_sap': solicitud.DocNumSAP,
                'detalles_oc': detalles_lista
            }
            
            content = render_to_string('emails/Logistica/email_aprobada_log.html', contexto)
            
        mensaje.attach(MIMEText(content, 'html'))
        mailServer.sendmail(EMAIL_HOST_USER, email_to, mensaje.as_string())
        print(f"Correo enviado a {email_to}")
    except Exception as e:
        print(e)
        print(f"Error al enviar correo a {user.email}: {str(e)}")