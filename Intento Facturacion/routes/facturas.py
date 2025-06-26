from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from database.connection import get_db
from models import Factura, Cliente
from schemas import FacturaCreate, FacturaUpdate, FacturaResponse, EmailFactura, FiltroFacturas
from services.email_service import email_service
from services.image_service import image_service
import random
import string

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from database.connection import get_db
from models import Factura, Cliente
from schemas import FacturaCreate, FacturaUpdate, FacturaResponse, EmailFactura, FiltroFacturas
from services.email_service import email_service
from services.image_service import image_service
import random
import string

router = APIRouter()

def generar_numero_factura() -> str:
    """Generar un número de factura único"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"GR-{timestamp}-{random_part}"

@router.get("/facturas", response_model=List[FacturaResponse])
async def obtener_facturas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    estado: Optional[str] = Query(None),
    nombre_cliente: Optional[str] = Query(None),
    email_cliente: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    metros_min: Optional[float] = Query(None),
    metros_max: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de facturas con filtros opcionales"""
    query = db.query(Factura)
    
    # Aplicar filtros
    if estado:
        query = query.filter(Factura.estado == estado)
    
    if nombre_cliente:
        query = query.filter(Factura.nombre_cliente.ilike(f"%{nombre_cliente}%"))
    
    if email_cliente:
        query = query.filter(Factura.email_cliente.ilike(f"%{email_cliente}%"))
    
    if color:
        query = query.filter(Factura.color_seleccionado.ilike(f"%{color}%"))
    
    if fecha_desde:
        query = query.filter(Factura.fecha_emision >= fecha_desde)
    
    if fecha_hasta:
        fecha_hasta_full = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(Factura.fecha_emision <= fecha_hasta_full)
    
    if metros_min:
        query = query.filter(Factura.metros_cuadrados >= metros_min)
    
    if metros_max:
        query = query.filter(Factura.metros_cuadrados <= metros_max)
    
    facturas = query.order_by(Factura.fecha_emision.desc()).offset(skip).limit(limit).all()
    return facturas

@router.get("/facturas/{factura_id}", response_model=FacturaResponse)
async def obtener_factura(factura_id: int, db: Session = Depends(get_db)):
    """Obtener una factura específica por ID"""
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

@router.post("/facturas", response_model=FacturaResponse)
async def crear_factura(factura: FacturaCreate, db: Session = Depends(get_db)):
    """Crear una nueva factura"""
    
    # Verificar que el cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == factura.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Generar número de factura único
    numero_factura = generar_numero_factura()
    while db.query(Factura).filter(Factura.numero_factura == numero_factura).first():
        numero_factura = generar_numero_factura()
    
    # Calcular totales
    subtotal = factura.metros_cuadrados * factura.precio_por_metro
    impuestos = subtotal * 0.13  # 13% de impuestos en Costa Rica
    total = subtotal + impuestos
    
    # Crear la factura
    db_factura = Factura(
        numero_factura=numero_factura,
        cliente_id=factura.cliente_id,
        nombre_cliente=factura.nombre_cliente,
        email_cliente=factura.email_cliente,
        color_seleccionado=factura.color_seleccionado,
        metros_cuadrados=factura.metros_cuadrados,
        precio_por_metro=factura.precio_por_metro,
        descripcion_servicio=factura.descripcion_servicio,
        subtotal=subtotal,
        impuestos=impuestos,
        total=total,
        observaciones=factura.observaciones
    )
    
    db.add(db_factura)
    db.commit()
    db.refresh(db_factura)
    
    return db_factura

@router.post("/facturas/{factura_id}/upload-imagen")
async def subir_imagen_modelo(
    factura_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Subir imagen del modelo para una factura"""
    
    # Verificar que la factura existe
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    try:
        # Eliminar imagen anterior si existe
        if factura.imagen_modelo:
            image_service.delete_image(factura.imagen_modelo)
        
        # Guardar nueva imagen
        imagen_path = await image_service.save_upload_image(file)
        
        # Actualizar factura
        factura.imagen_modelo = imagen_path
        db.commit()
        
        return {
            "message": "Imagen subida correctamente",
            "imagen_path": imagen_path,
            "imagen_url": image_service.get_image_url(imagen_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

@router.post("/facturas/{factura_id}/enviar-email")
async def enviar_factura_por_email(
    factura_id: int,
    email_data: EmailFactura,
    db: Session = Depends(get_db)
):
    """Enviar factura por email al cliente y a la empresa"""
    
    # Obtener factura
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    try:
        # Preparar datos para el email
        factura_data = {
            'numero_factura': factura.numero_factura,
            'fecha_emision': factura.fecha_emision.strftime('%d/%m/%Y'),
            'nombre_cliente': factura.nombre_cliente,
            'email_cliente': factura.email_cliente,
            'color_seleccionado': factura.color_seleccionado,
            'metros_cuadrados': factura.metros_cuadrados,
            'precio_por_metro': factura.precio_por_metro,
            'descripcion_servicio': factura.descripcion_servicio,
            'subtotal': factura.subtotal,
            'impuestos': factura.impuestos,
            'total': factura.total,
            'estado': factura.estado,
            'observaciones': factura.observaciones,
            'imagen_modelo': factura.imagen_modelo
        }
        
        # Enviar email
        success = await email_service.enviar_factura_email(
            factura_data=factura_data,
            email_cliente=factura.email_cliente,
            imagen_path=factura.imagen_modelo,
            mensaje_adicional=email_data.mensaje_personalizado
        )
        
        if success:
            # Actualizar estado de envío
            factura.email_enviado = 1
            factura.fecha_envio_email = datetime.utcnow()
            if factura.estado == "PENDIENTE":
                factura.estado = "ENVIADA"
            db.commit()
            
            return {"message": "Factura enviada por email correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error enviando email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/facturas/{factura_id}", response_model=FacturaResponse)
async def actualizar_factura(
    factura_id: int, 
    factura_update: FacturaUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar una factura existente"""
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Actualizar campos permitidos
    if factura_update.estado:
        if factura_update.estado not in ["PENDIENTE", "ENVIADA", "PAGADA", "ANULADA"]:
            raise HTTPException(status_code=400, detail="Estado inválido")
        factura.estado = factura_update.estado
    
    if factura_update.observaciones is not None:
        factura.observaciones = factura_update.observaciones
    
    if factura_update.color_seleccionado is not None:
        factura.color_seleccionado = factura_update.color_seleccionado
    
    if factura_update.imagen_modelo is not None:
        factura.imagen_modelo = factura_update.imagen_modelo
    
    db.commit()
    db.refresh(factura)
    return factura

@router.post("/facturas/{factura_id}/anular")
async def anular_factura(factura_id: int, db: Session = Depends(get_db)):
    """Anular una factura"""
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    if factura.estado == "ANULADA":
        raise HTTPException(status_code=400, detail="La factura ya está anulada")
    
    # Cambiar estado a anulada
    factura.estado = "ANULADA"
    db.commit()
    
    return {"message": "Factura anulada correctamente"}

@router.get("/facturas/numero/{numero_factura}", response_model=FacturaResponse)
async def obtener_factura_por_numero(numero_factura: str, db: Session = Depends(get_db)):
    """Obtener una factura por su número"""
    factura = db.query(Factura).filter(Factura.numero_factura == numero_factura).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

@router.get("/facturas/buscar/avanzada", response_model=List[FacturaResponse])
async def busqueda_avanzada_facturas(
    filtros: FiltroFacturas = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Búsqueda avanzada de facturas con múltiples filtros"""
    
    query = db.query(Factura)
    
    # Aplicar filtros del objeto FiltroFacturas
    if filtros.fecha_desde:
        query = query.filter(Factura.fecha_emision >= filtros.fecha_desde)
    
    if filtros.fecha_hasta:
        fecha_hasta_full = datetime.combine(filtros.fecha_hasta, datetime.max.time())
        query = query.filter(Factura.fecha_emision <= fecha_hasta_full)
    
    if filtros.estado:
        query = query.filter(Factura.estado == filtros.estado)
    
    if filtros.nombre_cliente:
        query = query.filter(Factura.nombre_cliente.ilike(f"%{filtros.nombre_cliente}%"))
    
    if filtros.email_cliente:
        query = query.filter(Factura.email_cliente.ilike(f"%{filtros.email_cliente}%"))
    
    if filtros.color:
        query = query.filter(Factura.color_seleccionado.ilike(f"%{filtros.color}%"))
    
    if filtros.metros_min:
        query = query.filter(Factura.metros_cuadrados >= filtros.metros_min)
    
    if filtros.metros_max:
        query = query.filter(Factura.metros_cuadrados <= filtros.metros_max)
    
    facturas = query.order_by(Factura.fecha_emision.desc()).offset(skip).limit(limit).all()
    return facturas

@router.get("/facturas/estadisticas/resumen")
async def obtener_estadisticas_facturas(db: Session = Depends(get_db)):
    """Obtener estadísticas resumidas de facturas"""
    
    from sqlalchemy import func
    
    # Estadísticas generales
    total_facturas = db.query(func.count(Factura.id)).scalar()
    total_ventas = db.query(func.sum(Factura.total)).scalar() or 0
    
    # Por estado
    stats_por_estado = db.query(
        Factura.estado,
        func.count(Factura.id).label('cantidad'),
        func.sum(Factura.total).label('total_monto')
    ).group_by(Factura.estado).all()
    
    # Promedio de metros cuadrados
    promedio_metros = db.query(func.avg(Factura.metros_cuadrados)).scalar() or 0
    
    return {
        "total_facturas": total_facturas,
        "total_ventas": total_ventas,
        "promedio_metros_cuadrados": round(promedio_metros, 2),
        "estadisticas_por_estado": [
            {
                "estado": stat.estado,
                "cantidad": stat.cantidad,
                "total_monto": stat.total_monto or 0
            }
            for stat in stats_por_estado
        ]
    }
