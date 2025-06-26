"""
Script para crear productos de ejemplo para Granimar CR
Ejecutar una sola vez para poblar la base de datos con productos
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import SessionLocal
from models import Producto

def crear_productos_ejemplo():
    """Crear productos de ejemplo para el sistema"""
    
    db = SessionLocal()
    
    productos_ejemplo = [
        {
            "codigo": "PISO-CER-001",
            "nombre": "Piso Cerámico Premium",
            "descripcion": "Instalación de piso cerámico de alta calidad, incluye material y mano de obra",
            "precio_unitario": 25000.00,
            "categoria": "Pisos",
            "stock": 1000
        },
        {
            "codigo": "PISO-POR-002", 
            "nombre": "Piso Porcelanato",
            "descripcion": "Instalación de porcelanato premium, incluye pegamento y acabados",
            "precio_unitario": 35000.00,
            "categoria": "Pisos",
            "stock": 800
        },
        {
            "codigo": "PINT-INT-003",
            "nombre": "Pintura Interior",
            "descripcion": "Pintura interior con pintura premium, incluye preparación de superficie",
            "precio_unitario": 8000.00,
            "categoria": "Pintura",
            "stock": 2000
        },
        {
            "codigo": "PINT-EXT-004",
            "nombre": "Pintura Exterior",
            "descripcion": "Pintura exterior resistente al clima, incluye sellador y acabado",
            "precio_unitario": 12000.00,
            "categoria": "Pintura", 
            "stock": 1500
        },
        {
            "codigo": "TECH-MET-005",
            "nombre": "Techo Metálico",
            "descripcion": "Instalación de techo metálico con estructura y materiales incluidos",
            "precio_unitario": 18000.00,
            "categoria": "Techos",
            "stock": 500
        },
        {
            "codigo": "TECH-TEJ-006",
            "nombre": "Techo de Tejas",
            "descripcion": "Instalación de techo con tejas de barro, incluye estructura",
            "precio_unitario": 22000.00,
            "categoria": "Techos",
            "stock": 300
        },
        {
            "codigo": "PARED-DRY-007",
            "nombre": "Pared Drywall",
            "descripcion": "Instalación de paredes en drywall con acabado listo para pintar",
            "precio_unitario": 15000.00,
            "categoria": "Paredes",
            "stock": 1200
        },
        {
            "codigo": "ELEC-BAS-008",
            "nombre": "Instalación Eléctrica Básica",
            "descripcion": "Instalación eléctrica básica por metro cuadrado, incluye materiales",
            "precio_unitario": 9000.00,
            "categoria": "Electricidad",
            "stock": 2000
        }
    ]
    
    try:
        productos_creados = 0
        
        for producto_data in productos_ejemplo:
            # Verificar si el producto ya existe
            producto_existente = db.query(Producto).filter(
                Producto.codigo == producto_data["codigo"]
            ).first()
            
            if not producto_existente:
                nuevo_producto = Producto(**producto_data)
                db.add(nuevo_producto)
                productos_creados += 1
                print(f"✅ Creado: {producto_data['nombre']}")
            else:
                print(f"⚠️  Ya existe: {producto_data['nombre']}")
        
        db.commit()
        print(f"\n🎉 Proceso completado. {productos_creados} productos nuevos creados.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creando productos de ejemplo para Granimar CR...")
    crear_productos_ejemplo()
