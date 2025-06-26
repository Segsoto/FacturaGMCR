from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from database.connection import get_db
from models import Factura, Cliente, Producto, DetalleFactura
from schemas import EstadisticasVentas

router = APIRouter()

@router.get("/dashboard/estadisticas", response_model=EstadisticasVentas)
async def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas del dashboard"""
    
    # Fecha actual y primer día del mes
    hoy = datetime.now()
    primer_dia_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total de ventas del mes actual
    ventas_mes = db.query(func.sum(Factura.total)).filter(
        Factura.fecha_emision >= primer_dia_mes,
        Factura.estado != "ANULADA"
    ).scalar() or 0.0
    
    # Total de facturas del mes actual
    facturas_mes = db.query(func.count(Factura.id)).filter(
        Factura.fecha_emision >= primer_dia_mes,
        Factura.estado != "ANULADA"
    ).scalar() or 0
    
    # Total de clientes activos
    total_clientes = db.query(func.count(Cliente.id)).filter(
        Cliente.activo == 1
    ).scalar() or 0
    
    # Total de productos activos
    total_productos = db.query(func.count(Producto.id)).filter(
        Producto.activo == 1
    ).scalar() or 0
    
    # Facturas pendientes
    facturas_pendientes = db.query(func.count(Factura.id)).filter(
        Factura.estado == "PENDIENTE"
    ).scalar() or 0
    
    return EstadisticasVentas(
        total_ventas_mes=ventas_mes,
        total_facturas_mes=facturas_mes,
        total_clientes=total_clientes,
        total_productos=total_productos,
        facturas_pendientes=facturas_pendientes
    )

@router.get("/dashboard/ventas-por-mes")
async def obtener_ventas_por_mes(db: Session = Depends(get_db)):
    """Obtener ventas agrupadas por mes para gráficos"""
    
    # Obtener ventas de los últimos 12 meses
    fecha_limite = datetime.now() - timedelta(days=365)
    
    ventas_por_mes = db.query(
        extract('year', Factura.fecha_emision).label('year'),
        extract('month', Factura.fecha_emision).label('month'),
        func.sum(Factura.total).label('total_ventas'),
        func.count(Factura.id).label('total_facturas')
    ).filter(
        Factura.fecha_emision >= fecha_limite,
        Factura.estado != "ANULADA"
    ).group_by(
        extract('year', Factura.fecha_emision),
        extract('month', Factura.fecha_emision)
    ).order_by(
        extract('year', Factura.fecha_emision),
        extract('month', Factura.fecha_emision)
    ).all()
    
    # Formatear los datos
    datos = []
    for venta in ventas_por_mes:
        mes_nombre = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][int(venta.month) - 1]
        
        datos.append({
            "mes": f"{mes_nombre} {int(venta.year)}",
            "total_ventas": float(venta.total_ventas or 0),
            "total_facturas": int(venta.total_facturas or 0)
        })
    
    return datos

@router.get("/dashboard/productos-mas-vendidos")
async def obtener_productos_mas_vendidos(db: Session = Depends(get_db)):
    """Obtener los productos más vendidos"""
    
    # Obtener datos de los últimos 30 días
    fecha_limite = datetime.now() - timedelta(days=30)
    
    productos_vendidos = db.query(
        Producto.nombre,
        Producto.codigo,
        func.sum(DetalleFactura.cantidad).label('total_vendido'),
        func.sum(DetalleFactura.subtotal).label('total_ingresos')
    ).join(
        DetalleFactura, Producto.id == DetalleFactura.producto_id
    ).join(
        Factura, DetalleFactura.factura_id == Factura.id
    ).filter(
        Factura.fecha_emision >= fecha_limite,
        Factura.estado != "ANULADA"
    ).group_by(
        Producto.id, Producto.nombre, Producto.codigo
    ).order_by(
        func.sum(DetalleFactura.cantidad).desc()
    ).limit(10).all()
    
    # Formatear los datos
    datos = []
    for producto in productos_vendidos:
        datos.append({
            "nombre": producto.nombre,
            "codigo": producto.codigo,
            "total_vendido": int(producto.total_vendido or 0),
            "total_ingresos": float(producto.total_ingresos or 0)
        })
    
    return datos

@router.get("/dashboard/clientes-top")
async def obtener_clientes_top(db: Session = Depends(get_db)):
    """Obtener los mejores clientes por compras"""
    
    # Obtener datos de los últimos 90 días
    fecha_limite = datetime.now() - timedelta(days=90)
    
    clientes_top = db.query(
        Cliente.nombre,
        Cliente.apellidos,
        Cliente.cedula,
        func.count(Factura.id).label('total_facturas'),
        func.sum(Factura.total).label('total_compras')
    ).join(
        Factura, Cliente.id == Factura.cliente_id
    ).filter(
        Factura.fecha_emision >= fecha_limite,
        Factura.estado != "ANULADA"
    ).group_by(
        Cliente.id, Cliente.nombre, Cliente.apellidos, Cliente.cedula
    ).order_by(
        func.sum(Factura.total).desc()
    ).limit(10).all()
    
    # Formatear los datos
    datos = []
    for cliente in clientes_top:
        datos.append({
            "nombre_completo": f"{cliente.nombre} {cliente.apellidos}",
            "cedula": cliente.cedula,
            "total_facturas": int(cliente.total_facturas or 0),
            "total_compras": float(cliente.total_compras or 0)
        })
    
    return datos
