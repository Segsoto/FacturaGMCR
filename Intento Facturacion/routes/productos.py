from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from models import Producto
from schemas import ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter()

@router.get("/productos", response_model=List[ProductoResponse])
async def obtener_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[int] = Query(None),
    categoria: Optional[str] = Query(None),
    buscar: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos con filtros opcionales"""
    query = db.query(Producto)
    
    if activo is not None:
        query = query.filter(Producto.activo == activo)
    
    if categoria:
        query = query.filter(Producto.categoria == categoria)
    
    if buscar:
        buscar_term = f"%{buscar}%"
        query = query.filter(
            (Producto.nombre.like(buscar_term)) |
            (Producto.codigo.like(buscar_term)) |
            (Producto.descripcion.like(buscar_term))
        )
    
    productos = query.offset(skip).limit(limit).all()
    return productos

@router.get("/productos/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtener un producto específico por ID"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.get("/productos/codigo/{codigo}", response_model=ProductoResponse)
async def obtener_producto_por_codigo(codigo: str, db: Session = Depends(get_db)):
    """Obtener un producto específico por código"""
    producto = db.query(Producto).filter(Producto.codigo == codigo).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/productos", response_model=ProductoResponse)
async def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo producto"""
    # Verificar si ya existe un producto con el mismo código
    producto_existente = db.query(Producto).filter(Producto.codigo == producto.codigo).first()
    if producto_existente:
        raise HTTPException(status_code=400, detail="Ya existe un producto con este código")
    
    # Crear nuevo producto
    db_producto = Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.put("/productos/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: int, 
    producto_update: ProductoUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar un producto existente"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar código único si se está actualizando
    if producto_update.codigo and producto_update.codigo != producto.codigo:
        codigo_existente = db.query(Producto).filter(
            Producto.codigo == producto_update.codigo,
            Producto.id != producto_id
        ).first()
        if codigo_existente:
            raise HTTPException(status_code=400, detail="Ya existe un producto con este código")
    
    # Actualizar solo los campos que se enviaron
    update_data = producto_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(producto, field, value)
    
    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """Eliminar (desactivar) un producto"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Desactivar el producto en lugar de eliminarlo
    producto.activo = 0
    db.commit()
    return {"message": "Producto desactivado correctamente"}

@router.post("/productos/{producto_id}/activar")
async def activar_producto(producto_id: int, db: Session = Depends(get_db)):
    """Activar un producto desactivado"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.activo = 1
    db.commit()
    return {"message": "Producto activado correctamente"}

@router.put("/productos/{producto_id}/stock")
async def actualizar_stock(
    producto_id: int, 
    nuevo_stock: int, 
    db: Session = Depends(get_db)
):
    """Actualizar el stock de un producto"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if nuevo_stock < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")
    
    producto.stock = nuevo_stock
    db.commit()
    return {"message": f"Stock actualizado a {nuevo_stock}"}
