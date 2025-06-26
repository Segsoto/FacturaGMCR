from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List, Optional
import os
from pathlib import Path
from datetime import datetime
import asyncio

class EmailConfig:
    """Configuración para el envío de emails"""
    
    # Configuración SMTP
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "facturacion@granimar.cr")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "facturacion@granimar.cr")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Granimar CR - Facturación")
    
    # Email de la empresa para copia
    EMPRESA_EMAIL = os.getenv("EMPRESA_EMAIL", "admin@granimar.cr")

# Configuración de FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=EmailConfig.MAIL_USERNAME,
    MAIL_PASSWORD=EmailConfig.MAIL_PASSWORD,
    MAIL_FROM=EmailConfig.MAIL_FROM,
    MAIL_PORT=EmailConfig.MAIL_PORT,
    MAIL_SERVER=EmailConfig.MAIL_SERVER,
    MAIL_FROM_NAME=EmailConfig.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.fastmail = FastMail(conf)
    
    def generar_html_factura(self, factura_data: dict) -> str:
        """Generar HTML para la factura"""
        
        # HTML simplificado para la factura
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Factura {factura_data['numero_factura']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                .table th {{ background-color: #f2f2f2; }}
                .total {{ font-size: 18px; font-weight: bold; color: #007bff; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Granimar CR</h1>
                <p>Factura Electrónica</p>
            </div>
            
            <div class="content">
                <h2>Factura #{factura_data['numero_factura']}</h2>
                <p><strong>Fecha:</strong> {factura_data['fecha_emision']}</p>
                <p><strong>Cliente:</strong> {factura_data['nombre_cliente']}</p>
                <p><strong>Email:</strong> {factura_data['email_cliente']}</p>
                
                <table class="table">
                    <tr>
                        <th>Descripción</th>
                        <th>Detalles</th>
                    </tr>
                    <tr>
                        <td>Descripción del Servicio</td>
                        <td>{factura_data.get('descripcion_servicio', 'Servicio de instalación')}</td>
                    </tr>
                    <tr>
                        <td>Color Seleccionado</td>
                        <td>{factura_data.get('color_seleccionado', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Metros Cuadrados</td>
                        <td>{factura_data['metros_cuadrados']} m²</td>
                    </tr>
                    <tr>
                        <td>Precio por m²</td>
                        <td>₡{factura_data['precio_por_metro']:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Subtotal</td>
                        <td>₡{factura_data['subtotal']:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Impuestos (13%)</td>
                        <td>₡{factura_data['impuestos']:,.2f}</td>
                    </tr>
                    <tr class="total">
                        <td>TOTAL</td>
                        <td>₡{factura_data['total']:,.2f}</td>
                    </tr>
                </table>
                
                <p>Gracias por confiar en Granimar CR para sus proyectos.</p>
                
                <hr>
                <p><small>
                    Granimar CR<br>
                    Email: facturacion@granimar.cr<br>
                    Teléfono: +506 2000-0000
                </small></p>
            </div>
        </body>
        </html>
        """
    
    async def enviar_factura_email(
        self,
        factura_data: dict,
        email_cliente: str,
        imagen_path: Optional[str] = None,
        mensaje_adicional: Optional[str] = None
    ) -> bool:
        """Enviar factura por email al cliente y a la empresa"""
        
        try:
            # Generar HTML de la factura
            html_content = self.generar_html_factura(factura_data)
            
            # Asunto del email
            asunto = f"Factura #{factura_data['numero_factura']} - Granimar CR"
            
            # Lista de destinatarios (cliente + empresa)
            destinatarios = [email_cliente]
            if EmailConfig.EMPRESA_EMAIL and EmailConfig.EMPRESA_EMAIL != email_cliente:
                destinatarios.append(EmailConfig.EMPRESA_EMAIL)
            
            # Crear mensaje
            message = MessageSchema(
                subject=asunto,
                recipients=destinatarios,
                body=html_content,
                subtype=MessageType.html
            )
            
            # Adjuntar imagen si existe (comentado por simplicidad)
            # if imagen_path and os.path.exists(imagen_path):
            #     message.attachments.append(imagen_path)
            
            # Enviar email
            await self.fastmail.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            # No fallar si el email no se puede enviar
            return True  # Devolvemos True para que la factura se guarde aunque el email falle
    
    async def enviar_email_simple(
        self,
        destinatario: str,
        asunto: str,
        contenido: str,
        es_html: bool = True
    ) -> bool:
        """Enviar email simple"""
        
        try:
            message = MessageSchema(
                subject=asunto,
                recipients=[destinatario],
                body=contenido,
                subtype=MessageType.html if es_html else MessageType.plain
            )
            
            await self.fastmail.send_message(message)
            return True
            
        except Exception as e:
            print(f"Error enviando email simple: {str(e)}")
            return True  # No fallar por problemas de email

# Instancia global del servicio de email
email_service = EmailService()
