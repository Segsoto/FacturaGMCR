# 📧 Configuración de Gmail para Envío de Facturas

## ⚙️ Pasos para Configurar Gmail:

### 1. Habilitar la Verificación en 2 Pasos
1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Ve a "Seguridad" → "Verificación en 2 pasos"
3. Actívala si no la tienes habilitada

### 2. Generar una Contraseña de Aplicación
1. En "Seguridad" → "Verificación en 2 pasos"
2. Busca "Contraseñas de aplicaciones"
3. Selecciona "Correo" y "Windows Computer"
4. Google te dará una contraseña de 16 caracteres

### 3. Configurar el archivo .env
Edita el archivo `.env` y reemplaza:

```
MAIL_USERNAME=granimarcr@gmail.com
MAIL_PASSWORD=aqui_pones_la_contraseña_de_aplicacion_de_16_caracteres
MAIL_FROM=granimarcr@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Granimar CR - Facturación
EMPRESA_EMAIL=granimarcr@gmail.com
```

### 4. Reiniciar el Servidor
Después de configurar el `.env`, reinicia el servidor:
```bash
Ctrl + C (para detener)
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

## 📋 Funcionamiento:
- ✅ **Cliente**: Recibe la factura en su email
- ✅ **Empresa**: `granimarcr@gmail.com` recibe una copia
- ✅ **Automático**: Se envía al crear cada factura

## 🔧 Para Probar:
1. Configura la contraseña de aplicación en `.env`
2. Reinicia el servidor
3. Crea una factura de prueba
4. Verifica que lleguen los emails

## ⚠️ Importante:
- Usa la **contraseña de aplicación**, NO tu contraseña normal de Gmail
- Mantén el archivo `.env` seguro y privado
- Si cambias la contraseña de Gmail, tendrás que generar una nueva contraseña de aplicación
