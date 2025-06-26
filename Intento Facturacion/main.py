from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from database.connection import engine, Base
from routes import clientes, productos, facturas, dashboard

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Facturación Granimar CR",
    description="Sistema completo de facturación para Granimar CR",
    version="1.0.0"
)

# Configurar archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Incluir rutas de la API
app.include_router(clientes.router, prefix="/api", tags=["clientes"])
app.include_router(productos.router, prefix="/api", tags=["productos"])
app.include_router(facturas.router, prefix="/api", tags=["facturas"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal del sistema"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/clientes", response_class=HTMLResponse)
async def clientes_page(request: Request):
    """Página de gestión de clientes"""
    return templates.TemplateResponse("clientes.html", {"request": request})

@app.get("/productos", response_class=HTMLResponse)
async def productos_page(request: Request):
    """Página de gestión de productos"""
    return templates.TemplateResponse("productos.html", {"request": request})

@app.get("/facturas", response_class=HTMLResponse)
async def facturas_page(request: Request):
    """Página de gestión de facturas"""
    return templates.TemplateResponse("facturas.html", {"request": request})

@app.get("/nueva-factura", response_class=HTMLResponse)
async def nueva_factura_page(request: Request):
    """Página para crear nueva factura"""
    return templates.TemplateResponse("nueva_factura.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
