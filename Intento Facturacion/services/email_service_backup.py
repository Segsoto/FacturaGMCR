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
        
        imagen_html = ""
        if factura_data.get('imagen_modelo'):
            imagen_html = f'''
            <div style="margin: 20px 0; text-align: center;">
                <h3 style="color: #007bff;">Modelo Seleccionado</h3>
                <img src="cid:modelo_imagen" style="max-width: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" alt="Modelo seleccionado">
            </div>
            '''
        
        color_html = ""
        if factura_data.get('color_seleccionado'):
            color_html = f'''
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Color seleccionado:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{factura_data['color_seleccionado']}</td>
            </tr>
            '''
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Factura - Granimar CR</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid #007bff; }}
                .logo {{ font-size: 28px; font-weight: bold; color: #007bff; margin-bottom: 10px; }}
                .company-info {{ color: #666; font-size: 14px; }}
                .factura-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .details-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .details-table th {{ background: #007bff; color: white; padding: 12px; text-align: left; }}
                .details-table td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                .total-section {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: right; }}
                .total-amount {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }}
                .status-badge {{ display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
                .status-pendiente {{ background: #fff3cd; color: #856404; }}
                .status-pagada {{ background: #d4edda; color: #155724; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🏢 GRANIMAR CR</div>
                    <div class="company-info">
                        Sistema de Facturación Electrónica<br>
                        Email: facturacion@granimar.cr<br>
                        Teléfono: +506 2000-0000
                    </div>
                </div>
                
                <div class="factura-info">
                    <h2 style="margin: 0 0 15px 0; color: #007bff;">Factura Electrónica</h2>
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div>
                            <strong>Número:</strong> {factura_data['numero_factura']}<br>
                            <strong>Fecha:</strong> {factura_data['fecha_emision']}<br>
                            <strong>Cliente:</strong> {factura_data['nombre_cliente']}<br>
                            <strong>Email:</strong> {factura_data['email_cliente']}
                        </div>
                        <div>
                            <span class="status-badge status-{factura_data['estado'].lower()}">{factura_data['estado']}</span>
                        </div>
                    </div>
                </div>
                
                {imagen_html}
                
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Descripción del Servicio</th>
                            <th>Detalles</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Descripción:</strong></td>
                            <td>{factura_data.get('descripcion_servicio', 'Servicio de instalación')}</td>
                        </tr>
                        {color_html}
                        <tr>
                            <td><strong>Metros cuadrados:</strong></td>
                            <td>{factura_data['metros_cuadrados']} m²</td>
                        </tr>
                        <tr>
                            <td><strong>Precio por m²:</strong></td>
                            <td>₡{factura_data['precio_por_metro']:,.2f}</td>
                        </tr>
                        <tr>
                            <td><strong>Subtotal:</strong></td>
                            <td>₡{factura_data['subtotal']:,.2f}</td>
                        </tr>
                        <tr>
                            <td><strong>Impuestos (13%):</strong></td>
                            <td>₡{factura_data['impuestos']:,.2f}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="total-section">
                    <div style="font-size: 18px; margin-bottom: 10px;">
                        <strong>Total a Pagar:</strong>
                    </div>
                    <div class="total-amount">₡{factura_data['total']:,.2f}</div>
                </div>
                
                {f'<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;"><strong>Observaciones:</strong><br>{factura_data["observaciones"]}</div>' if factura_data.get('observaciones') else ''}
                
                <div class="footer">
                    <p><strong>¡Gracias por confiar en Granimar CR!</strong></p>
                    <p>Esta factura fue generada automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                    <p style="font-size: 12px; color: #999;">
                        Este documento es válido sin firma ni sello según la Ley de Facturación Electrónica de Costa Rica
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
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
            
            # Preparar el mensaje
            subject = f"Factura #{factura_data['numero_factura']} - Granimar CR"
            
            # Lista de destinatarios (cliente + empresa)
            recipients = [email_cliente, EmailConfig.EMPRESA_EMAIL]
            
            # Crear mensaje
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_content,
                subtype=MessageType.html,
                attachments=[]
            )
            
            # Agregar imagen si existe
            if imagen_path and os.path.exists(imagen_path):
                message.attachments.append(imagen_path)
            
            # Enviar email
            await self.fastmail.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            return False
    
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
            return False

# Instancia global del servicio de email
email_service = EmailService()
