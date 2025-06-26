# 🧾 Sistema de Facturación Granimar CR

Sistema de facturación completo desarrollado en Python con FastAPI para la empresa Granimar CR. Incluye una interfaz web moderna y una API REST completa para la gestión de clientes, productos y facturas.

## ✨ Características

- **🏢 Gestión de Clientes**: Registro, edición y consulta de clientes con validación de cédula costarricense
- **📦 Catálogo de Productos**: Administración completa de productos con control de inventario
- **🧾 Facturación**: Creación y gestión de facturas con cálculo automático de impuestos (13%)
- **📊 Dashboard**: Estadísticas de ventas, productos más vendidos y mejores clientes
- **🗄️ Base de Datos**: Integración con SQL Server usando SQLAlchemy
- **🌐 API REST**: Endpoints completos para todas las operaciones
- **📱 Interfaz Responsive**: Frontend moderno con Bootstrap 5

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.13 + FastAPI
- **Base de Datos**: SQL Server con SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Migraciones**: Alembic
- **Validación**: Pydantic
- **Driver DB**: PyODBC

## 📋 Requisitos

- Python 3.11 o superior
- SQL Server (LocalDB, Express o completo)
- Driver ODBC para SQL Server
- Visual Studio Code (recomendado)

## 🚀 Instalación

### 1. Clonar o descargar el proyecto
```bash
# Si tienes git
git clone <url-del-repositorio>

# O descargar el ZIP y extraer
```

### 2. Instalar dependencias
```bash
cd "c:\Users\brand\OneDrive - Universidad Fidélitas\Documentos\Intento Facturacion"
pip install -r requirements.txt
```

### 3. Configurar la base de datos

Crear un archivo `.env` en la raíz del proyecto con la configuración de tu base de datos:

```env
# Variables de entorno para la base de datos
DB_SERVER=localhost
DB_DATABASE=granimar_facturacion
DB_USERNAME=sa
DB_PASSWORD=TuContraseña123
DB_PORT=1433

# Configuración de la aplicación
SECRET_KEY=tu_clave_secreta_muy_segura
DEBUG=True
```

### 4. Crear la base de datos
```sql
-- Ejecutar en SQL Server Management Studio o Azure Data Studio
CREATE DATABASE granimar_facturacion;
```

### 5. Ejecutar migraciones (cuando estén configuradas)
```bash
alembic upgrade head
```

### 6. Iniciar el servidor
```bash
# Opción 1: Archivo principal
python main.py

# Opción 2: Con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción 3: Versión de prueba (actual)
python main_simple.py
```

## 🌐 Acceso a la Aplicación

Una vez iniciado el servidor:

- **Aplicación Web**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

## 📁 Estructura del Proyecto

```
├── main.py                  # Aplicación principal FastAPI
├── main_simple.py          # Versión de prueba simplificada
├── requirements.txt        # Dependencias Python
├── schemas.py             # Esquemas Pydantic para validación
├── alembic.ini            # Configuración de migraciones
├── .env                   # Variables de entorno (no incluir en git)
├── .env.example          # Ejemplo de variables de entorno
├── database/
│   ├── __init__.py
│   └── connection.py     # Configuración de base de datos
├── models/
│   ├── __init__.py       # Modelos SQLAlchemy
├── routes/
│   ├── __init__.py
│   ├── clientes.py       # Endpoints de clientes
│   ├── productos.py      # Endpoints de productos
│   ├── facturas.py       # Endpoints de facturas
│   └── dashboard.py      # Endpoints de estadísticas
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   └── js/
│       ├── utils.js      # Utilidades JavaScript
│       └── dashboard.js  # Funciones del dashboard
├── templates/
│   ├── base.html         # Plantilla base
│   └── index.html        # Página principal
└── alembic/
    ├── env.py            # Configuración de Alembic
    ├── script.py.mako    # Plantilla de migraciones
    └── versions/         # Archivos de migración
```

## 🔗 API Endpoints

### Clientes
- `GET /api/clientes` - Listar clientes
- `POST /api/clientes` - Crear cliente
- `GET /api/clientes/{id}` - Obtener cliente
- `PUT /api/clientes/{id}` - Actualizar cliente
- `DELETE /api/clientes/{id}` - Desactivar cliente

### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `GET /api/productos/{id}` - Obtener producto
- `PUT /api/productos/{id}` - Actualizar producto
- `DELETE /api/productos/{id}` - Desactivar producto

### Facturas
- `GET /api/facturas` - Listar facturas
- `POST /api/facturas` - Crear factura
- `GET /api/facturas/{id}` - Obtener factura
- `PUT /api/facturas/{id}` - Actualizar factura
- `POST /api/facturas/{id}/anular` - Anular factura

### Dashboard
- `GET /api/dashboard/estadisticas` - Estadísticas generales
- `GET /api/dashboard/ventas-por-mes` - Ventas por mes
- `GET /api/dashboard/productos-mas-vendidos` - Top productos
- `GET /api/dashboard/clientes-top` - Mejores clientes

## 🗄️ Modelos de Base de Datos

### Cliente
- ID, nombre, apellidos, cédula
- Teléfono, email, dirección
- Fecha de creación, estado activo

### Producto
- ID, código, nombre, descripción
- Precio unitario, stock, categoría
- Fecha de creación, estado activo

### Factura
- ID, número de factura, cliente
- Fecha de emisión, subtotal, impuestos, total
- Estado (PENDIENTE, PAGADA, ANULADA)

### Detalle de Factura
- ID, factura, producto
- Cantidad, precio unitario, subtotal

## 🎨 Características de la Interfaz

- **Diseño Moderno**: Interface limpia con Bootstrap 5
- **Responsive**: Se adapta a dispositivos móviles
- **Dashboard Interactivo**: Gráficos con Chart.js
- **Validación en Tiempo Real**: Formularios con validación
- **Notificaciones**: Sistema de toasts para feedback
- **Búsqueda y Filtros**: Búsqueda avanzada en todas las secciones

## 🔧 Desarrollo

### Estructura de Desarrollo
- **Arquitectura MVC**: Separación clara de responsabilidades
- **Validación**: Esquemas Pydantic para validación de datos
- **ORM**: SQLAlchemy para operaciones de base de datos
- **Migraciones**: Alembic para versionado de esquema

### Tareas de VS Code
- **Iniciar Servidor**: Configurado para ejecutar con F5
- **Debug**: Configuración de debugging incluida

## 🚨 Estado Actual

✅ **Completado**:
- Estructura base del proyecto
- Modelos de base de datos
- API REST completa
- Esquemas de validación
- Configuración de Alembic
- Plantillas HTML base
- Estilos CSS
- JavaScript utilidades
- Dashboard básico

⏳ **Pendiente**:
- Completar todas las plantillas HTML
- Implementar autenticación
- Agregar más validaciones
- Optimizar consultas de base de datos
- Agregar tests unitarios
- Configurar logging
- Agregar exportación de reportes

## 📝 Notas de Configuración

### SQL Server
Asegúrate de que SQL Server esté configurado para:
- Permitir conexiones TCP/IP
- Autenticación mixta (si usas usuario/contraseña)
- Puerto 1433 abierto (o el que configures)

### Driver ODBC
Instalar el driver ODBC más reciente:
- [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## 📞 Soporte

Para soporte técnico o preguntas sobre el sistema, contactar al equipo de desarrollo.

---

**© 2024 Granimar CR - Sistema de Facturación**  
Desarrollado con ❤️ usando Python + FastAPI
