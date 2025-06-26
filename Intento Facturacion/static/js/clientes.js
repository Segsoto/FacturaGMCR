// JavaScript para gestión de clientes

let clientesData = [];

document.addEventListener('DOMContentLoaded', function() {
    cargarClientes();
});

// Cargar lista de clientes
async function cargarClientes() {
    try {
        const response = await fetch('/api/clientes');
        if (response.ok) {
            clientesData = await response.json();
            mostrarClientes();
        } else {
            console.error('Error cargando clientes');
            mostrarError('Error cargando la lista de clientes');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión al cargar clientes');
    }
}

// Mostrar clientes en la tabla
function mostrarClientes() {
    const tbody = document.querySelector('#tabla-clientes tbody');
    
    if (clientesData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No hay clientes registrados
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = clientesData.map(cliente => `
        <tr>
            <td>${cliente.nombre} ${cliente.apellidos}</td>
            <td>${cliente.cedula}</td>
            <td>${cliente.email || 'N/A'}</td>
            <td>${cliente.telefono || 'N/A'}</td>
            <td>
                <span class="badge ${cliente.activo ? 'bg-success' : 'bg-danger'}">
                    ${cliente.activo ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editarCliente(${cliente.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="eliminarCliente(${cliente.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Guardar nuevo cliente
async function guardarCliente() {
    const form = document.getElementById('form-nuevo-cliente');
    const formData = new FormData(form);
    
    const cliente = {
        nombre: formData.get('nombre'),
        apellidos: formData.get('apellidos'),
        cedula: formData.get('cedula'),
        telefono: formData.get('telefono'),
        email: formData.get('email'),
        direccion: formData.get('direccion')
    };
    
    try {
        const response = await fetch('/api/clientes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cliente)
        });
        
        if (response.ok) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoCliente'));
            modal.hide();
            
            // Limpiar formulario
            form.reset();
            
            // Recargar lista
            cargarClientes();
            
            mostrarExito('Cliente creado exitosamente');
        } else {
            const error = await response.json();
            mostrarError(error.detail || 'Error creando cliente');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión');
    }
}

// Editar cliente
function editarCliente(id) {
    // Por implementar
    alert('Función de edición por implementar');
}

// Eliminar cliente
function eliminarCliente(id) {
    if (confirm('¿Está seguro de eliminar este cliente?')) {
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
