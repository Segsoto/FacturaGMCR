// JavaScript para gestión de productos

let productosData = [];

document.addEventListener('DOMContentLoaded', function() {
    cargarProductos();
});

// Cargar lista de productos
async function cargarProductos() {
    try {
        const response = await fetch('/api/productos');
        if (response.ok) {
            productosData = await response.json();
            mostrarProductos();
        } else {
            console.error('Error cargando productos');
            mostrarError('Error cargando la lista de productos');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión al cargar productos');
    }
}

// Mostrar productos en la tabla
function mostrarProductos() {
    const tbody = document.querySelector('#tabla-productos tbody');
    
    if (productosData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    No hay productos registrados
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = productosData.map(producto => `
        <tr>
            <td>${producto.codigo}</td>
            <td>${producto.nombre}</td>
            <td>${producto.categoria || 'N/A'}</td>
            <td>₡${producto.precio_unitario.toLocaleString()}</td>
            <td>${producto.stock}</td>
            <td>
                <span class="badge ${producto.activo ? 'bg-success' : 'bg-danger'}">
                    ${producto.activo ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editarProducto(${producto.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="eliminarProducto(${producto.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Guardar nuevo producto
async function guardarProducto() {
    const form = document.getElementById('form-nuevo-producto');
    const formData = new FormData(form);
    
    const producto = {
        codigo: formData.get('codigo'),
        nombre: formData.get('nombre'),
        descripcion: formData.get('descripcion'),
        precio_unitario: parseFloat(formData.get('precio_unitario')),
        stock: parseInt(formData.get('stock')) || 0,
        categoria: formData.get('categoria')
    };
    
    try {
        const response = await fetch('/api/productos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(producto)
        });
        
        if (response.ok) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoProducto'));
            modal.hide();
            
            // Limpiar formulario
            form.reset();
            
            // Recargar lista
            cargarProductos();
            
            mostrarExito('Producto creado exitosamente');
        } else {
            const error = await response.json();
            mostrarError(error.detail || 'Error creando producto');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión');
    }
}

// Editar producto
function editarProducto(id) {
    // Por implementar
    alert('Función de edición por implementar');
}

// Eliminar producto
function eliminarProducto(id) {
    if (confirm('¿Está seguro de eliminar este producto?')) {
        // Por implementar
        alert('Función de eliminación por implementar');
    }
}

// Funciones de utilidad
function mostrarExito(mensaje) {
    // Usar la función de utils.js si existe, o mostrar alerta simple
    if (typeof Utils !== 'undefined' && Utils.showToast) {
        Utils.showToast(mensaje, 'success');
    } else {
        alert(mensaje);
    }
}

function mostrarError(mensaje) {
    // Usar la función de utils.js si existe, o mostrar alerta simple
    if (typeof Utils !== 'undefined' && Utils.showToast) {
        Utils.showToast(mensaje, 'error');
    } else {
        alert('Error: ' + mensaje);
    }
}
