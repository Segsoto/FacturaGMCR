from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from database.connection import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Cliente(Base):
    """Modelo para la tabla de clientes"""
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    
    # Relación con facturas
    facturas = relationship("Factura", back_populates="cliente")

class Producto(Base):
    """Modelo para la tabla de productos"""
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    precio_unitario = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    categoria = Column(String(50))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    
    # Relación con detalles de factura
    detalles_factura = relationship("DetalleFactura", back_populates="producto")

class Factura(Base):
    """Modelo para la tabla de facturas"""
    __tablename__ = "facturas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_factura = Column(String(20), unique=True, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    
    # Campos específicos del servicio
    nombre_cliente = Column(String(200), nullable=False)  # Nombre completo del cliente
    email_cliente = Column(String(100), nullable=False)   # Email para envío
    color_seleccionado = Column(String(100))              # Color del servicio
    metros_cuadrados = Column(Float, nullable=False)      # Área a trabajar
    precio_por_metro = Column(Float, nullable=False)      # Precio por m²
    imagen_modelo = Column(String(500))                   # Ruta de la imagen del modelo
    descripcion_servicio = Column(Text)                   # Descripción del trabajo
    
    # Campos de cálculo
    subtotal = Column(Float, default=0.0)
    impuestos = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    estado = Column(String(20), default="PENDIENTE")      # PENDIENTE, PAGADA, ANULADA, ENVIADA
    observaciones = Column(Text)
    
    # Campos de control de envío
    email_enviado = Column(Integer, default=0)            # 0=No enviado, 1=Enviado
    fecha_envio_email = Column(DateTime)                   # Cuándo se envió
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="facturas")
    detalles = relationship("DetalleFactura", back_populates="factura", cascade="all, delete-orphan")

class DetalleFactura(Base):
    """Modelo para la tabla de detalles de factura"""
    __tablename__ = "detalles_factura"
    
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # Relaciones
    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_factura")
