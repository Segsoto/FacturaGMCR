from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Sistema de Facturación Granimar CR",
    description="Sistema completo de facturación para Granimar CR",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal del sistema"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Granimar CR - Sistema de Facturación</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .status { background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .features { list-style: none; padding: 0; }
            .features li { background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }
            .btn { display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧾 Sistema de Facturación Granimar CR</h1>
            
            <div class="status">
                ✅ <strong>¡Sistema iniciado correctamente!</strong><br>
                El servidor FastAPI está funcionando y listo para usar.
            </div>
            
            <h2>Características del Sistema:</h2>
            <ul class="features">
                <li><strong>Gestión de Clientes:</strong> Registro, edición y consulta de clientes</li>
                <li><strong>Catálogo de Productos:</strong> Administración completa de productos</li>
                <li><strong>Facturación:</strong> Creación y gestión de facturas</li>
                <li><strong>Reportes:</strong> Dashboard con estadísticas de ventas</li>
                <li><strong>Base de Datos:</strong> Integración con SQL Server</li>
                <li><strong>API REST:</strong> Endpoints para todas las operaciones</li>
            </ul>
            
            <h2>Acciones Disponibles:</h2>
            <a href="/docs" class="btn">📖 Ver Documentación de API</a>
            <a href="/redoc" class="btn">📋 Ver Documentación ReDoc</a>
            
            <h2>Próximos Pasos:</h2>
            <ol>
                <li>Configurar la base de datos SQL Server</li>
                <li>Ejecutar las migraciones de Alembic</li>
                <li>Agregar las plantillas HTML completas</li>
                <li>Probar las funcionalidades</li>
            </ol>
            
            <div style="text-align: center; margin-top: 40px; color: #6c757d;">
                <p>© 2024 Granimar CR - Sistema de Facturación</p>
                <p>Desarrollado con FastAPI + SQL Server</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de desarrollo...")
    print("📍 URL: http://localhost:8000")
    print("📖 Documentación: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
