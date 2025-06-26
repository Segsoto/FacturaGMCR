from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from models import Cliente
from schemas import ClienteCreate, ClienteUpdate, ClienteResponse

router = APIRouter()

@router.get("/clientes", response_model=List[ClienteResponse])
async def obtener_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[int] = Query(None),
    buscar: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de clientes con filtros opcionales"""
    query = db.query(Cliente)
    
    if activo is not None:
        query = query.filter(Cliente.activo == activo)
    
    if buscar:
        buscar_term = f"%{buscar}%"
        query = query.filter(
            (Cliente.nombre.like(buscar_term)) |
            (Cliente.apellidos.like(buscar_term)) |
            (Cliente.cedula.like(buscar_term)) |
            (Cliente.email.like(buscar_term))
        )
    
    clientes = query.offset(skip).limit(limit).all()
    return clientes

@router.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente específico por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.post("/clientes", response_model=ClienteResponse)
async def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    # Verificar si ya existe un cliente con la misma cédula
    cliente_existente = db.query(Cliente).filter(Cliente.cedula == cliente.cedula).first()
    if cliente_existente:
        raise HTTPException(status_code=400, detail="Ya existe un cliente con esta cédula")
    
    # Crear nuevo cliente
    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.put("/clientes/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(
    cliente_id: int, 
    cliente_update: ClienteUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar un cliente existente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar solo los campos que se enviaron
    update_data = cliente_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)
    
    db.commit()
    db.refresh(cliente)
    return cliente

@router.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Eliminar (desactivar) un cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Desactivar el cliente en lugar de eliminarlo
    cliente.activo = 0
    db.commit()
    return {"message": "Cliente desactivado correctamente"}

@router.post("/clientes/{cliente_id}/activar")
async def activar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Activar un cliente desactivado"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente.activo = 1
    db.commit()
    return {"message": "Cliente activado correctamente"}
