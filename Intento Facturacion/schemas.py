from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date

# Esquemas para Cliente
class ClienteBase(BaseModel):
    """Esquema base para cliente"""
    nombre: str
    apellidos: str
    cedula: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    
    @validator('cedula')
    def validar_cedula(cls, v):
        if not v or len(v) < 9:
            raise ValueError('La cédula debe tener al menos 9 caracteres')
        return v
    
    @validator('nombre', 'apellidos')
    def validar_nombres(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nombre y apellidos deben tener al menos 2 caracteres')
        return v.strip().title()

class ClienteCreate(ClienteBase):
    """Esquema para crear cliente"""
    pass

class ClienteUpdate(BaseModel):
    """Esquema para actualizar cliente"""
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[int] = None

class ClienteResponse(ClienteBase):
    """Esquema de respuesta para cliente"""
    id: int
    fecha_creacion: datetime
    activo: int
    
    class Config:
        from_attributes = True

# Esquemas para Producto
class ProductoBase(BaseModel):
    """Esquema base para producto"""
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_unitario: float
    stock: Optional[int] = 0
    categoria: Optional[str] = None
    
    @validator('precio_unitario')
    def validar_precio(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v
    
    @validator('stock')
    def validar_stock(cls, v):
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v

class ProductoCreate(ProductoBase):
    """Esquema para crear producto"""
    pass

class ProductoUpdate(BaseModel):
    """Esquema para actualizar producto"""
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_unitario: Optional[float] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None
    activo: Optional[int] = None

class ProductoResponse(ProductoBase):
    """Esquema de respuesta para producto"""
    id: int
    fecha_creacion: datetime
    activo: int
    
    class Config:
        from_attributes = True

# Esquemas para Detalle de Factura
class DetalleFacturaBase(BaseModel):
    """Esquema base para detalle de factura"""
    producto_id: int
    cantidad: int
    precio_unitario: float
    
    @validator('cantidad')
    def validar_cantidad(cls, v):
        if v <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')
        return v

class DetalleFacturaCreate(DetalleFacturaBase):
    """Esquema para crear detalle de factura"""
    pass

class DetalleFacturaResponse(DetalleFacturaBase):
    """Esquema de respuesta para detalle de factura"""
    id: int
    factura_id: int
    subtotal: float
    producto: ProductoResponse
    
    class Config:
        from_attributes = True

# Esquemas para Factura
class FacturaBase(BaseModel):
    """Esquema base para factura"""
    cliente_id: int
    nombre_cliente: str
    email_cliente: str
    color_seleccionado: Optional[str] = None
    metros_cuadrados: float
    precio_por_metro: float
    descripcion_servicio: Optional[str] = None
    observaciones: Optional[str] = None
    
    @validator('metros_cuadrados')
    def validar_metros(cls, v):
        if v <= 0:
            raise ValueError('Los metros cuadrados deben ser mayor a 0')
        return v
    
    @validator('precio_por_metro')
    def validar_precio_metro(cls, v):
        if v <= 0:
            raise ValueError('El precio por metro debe ser mayor a 0')
        return v
    
    @validator('email_cliente')
    def validar_email_cliente(cls, v):
        if not v or '@' not in v:
            raise ValueError('Email del cliente inválido')
        return v.lower().strip()

class FacturaCreate(FacturaBase):
    """Esquema para crear factura"""
    pass

class FacturaUpdate(BaseModel):
    """Esquema para actualizar factura"""
    estado: Optional[str] = None
    observaciones: Optional[str] = None
    color_seleccionado: Optional[str] = None
    imagen_modelo: Optional[str] = None

class FacturaResponse(FacturaBase):
    """Esquema de respuesta para factura"""
    id: int
    numero_factura: str
    fecha_emision: datetime
    subtotal: float
    impuestos: float
    total: float
    estado: str
    imagen_modelo: Optional[str] = None
    email_enviado: int
    fecha_envio_email: Optional[datetime] = None
    cliente: ClienteResponse
    
    class Config:
        from_attributes = True

# Esquema para envío de email
class EmailFactura(BaseModel):
    """Esquema para envío de factura por email"""
    factura_id: int
    email_adicional: Optional[str] = None
    mensaje_personalizado: Optional[str] = None

# Esquema para filtros de búsqueda
class FiltroFacturas(BaseModel):
    """Esquema para filtros de búsqueda de facturas"""
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    estado: Optional[str] = None
    nombre_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    color: Optional[str] = None
    metros_min: Optional[float] = None
    metros_max: Optional[float] = None

# Esquemas para Dashboard
class EstadisticasVentas(BaseModel):
    """Esquema para estadísticas de ventas"""
    total_ventas_mes: float
    total_facturas_mes: int
    total_clientes: int
    total_productos: int
    facturas_pendientes: int
