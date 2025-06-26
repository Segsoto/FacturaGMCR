// JavaScript para Nueva Factura

let clientesCache = [];
let productosCache = [];
let selectedFile = null;

document.addEventListener('DOMContentLoaded', function() {
    cargarClientes();
    cargarProductos();
    inicializarEventos();
    configurarDropZone();
});

// Cargar lista de clientes
async function cargarClientes() {
    try {
        const clientes = await API.get('/clientes?limit=1000');
        clientesCache = clientes;
        
        const selectCliente = document.getElementById('cliente_id');
        selectCliente.innerHTML = '<option value="">Seleccionar cliente existente (opcional)</option>';
        
        clientes.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.id;
            option.textContent = `${cliente.nombre} ${cliente.apellidos} - ${cliente.cedula}`;
            option.dataset.email = cliente.email || '';
            option.dataset.nombre = `${cliente.nombre} ${cliente.apellidos}`;
            selectCliente.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error cargando clientes:', error);
    }
}

// Cargar lista de productos
async function cargarProductos() {
    try {
        const productos = await API.get('/productos?limit=1000');
        productosCache = productos;
        
        const selectProducto = document.getElementById('producto_id');
        selectProducto.innerHTML = '<option value="">Seleccionar producto...</option>';
        
        productos.forEach(producto => {
            if (producto.activo) { // Solo productos activos
                const option = document.createElement('option');
                option.value = producto.id;
                option.textContent = `${producto.nombre} - ₡${producto.precio_unitario.toLocaleString()} por m²`;
                option.dataset.precio = producto.precio_unitario;
                option.dataset.descripcion = producto.descripcion || '';
                option.dataset.categoria = producto.categoria || '';
                selectProducto.appendChild(option);
            }
        });
        
    } catch (error) {
        console.error('Error cargando productos:', error);
        Utils.showToast('Error cargando productos', 'error');
    }
}

// Inicializar eventos
function inicializarEventos() {
    // Evento de selección de cliente
    document.getElementById('cliente_id').addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        if (selectedOption.value) {
            document.getElementById('nombre_cliente').value = selectedOption.dataset.nombre || '';
            document.getElementById('email_cliente').value = selectedOption.dataset.email || '';
        }
    });
    
    // Evento de selección de producto
    document.getElementById('producto_id').addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const productoInfo = document.getElementById('producto-info');
        const productoDetalles = document.getElementById('producto-detalles');
        
        if (selectedOption.value) {
            // Mostrar información del producto
            const precio = parseFloat(selectedOption.dataset.precio);
            const descripcion = selectedOption.dataset.descripcion;
            const categoria = selectedOption.dataset.categoria;
            
            productoDetalles.innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <strong>Precio por m²:</strong><br>
                        ₡${precio.toLocaleString()}
                    </div>
                    <div class="col-md-4">
                        <strong>Categoría:</strong><br>
                        ${categoria || 'N/A'}
                    </div>
                    <div class="col-md-4">
                        <strong>Descripción:</strong><br>
                        ${descripcion || 'N/A'}
                    </div>
                </div>
            `;
            productoInfo.style.display = 'block';
            
            // Calcular totales automáticamente
            calcularTotales();
        } else {
            productoInfo.style.display = 'none';
        }
    });
    
    // Eventos de cálculo
    const metrosInput = document.getElementById('metros_cuadrados');
    
    metrosInput.addEventListener('input', calcularTotales);
    
    // Evento de envío del formulario
    document.getElementById('form-nueva-factura').addEventListener('submit', crearFactura);
    
    // Eventos de imagen
    document.getElementById('imagen_modelo').addEventListener('change', manejarSeleccionImagen);
    document.getElementById('remove-image').addEventListener('click', removerImagen);
}

// Configurar zona de arrastrar y soltar
function configurarDropZone() {
    const uploadArea = document.getElementById('upload-area');
    
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                selectedFile = file;
                mostrarPreviewImagen(file);
            } else {
                Utils.showToast('Por favor selecciona una imagen válida', 'warning');
            }
        }
    });
    
    uploadArea.addEventListener('click', function() {
        document.getElementById('imagen_modelo').click();
    });
}

// Manejar selección de imagen
function manejarSeleccionImagen(event) {
    const file = event.target.files[0];
    if (file) {
        if (file.type.startsWith('image/')) {
            selectedFile = file;
            mostrarPreviewImagen(file);
        } else {
            Utils.showToast('Por favor selecciona una imagen válida', 'warning');
            event.target.value = '';
        }
    }
}

// Mostrar preview de la imagen
function mostrarPreviewImagen(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const uploadContent = document.querySelector('.upload-content');
        const previewContainer = document.getElementById('preview-container');
        const previewImage = document.getElementById('preview-image');
        
        previewImage.src = e.target.result;
        uploadContent.classList.add('d-none');
        previewContainer.classList.remove('d-none');
    };
    reader.readAsDataURL(file);
}

// Remover imagen
function removerImagen() {
    selectedFile = null;
    document.getElementById('imagen_modelo').value = '';
    
    const uploadContent = document.querySelector('.upload-content');
    const previewContainer = document.getElementById('preview-container');
    
    uploadContent.classList.remove('d-none');
    previewContainer.classList.add('d-none');
}

// Calcular totales
function calcularTotales() {
    const metrosInput = document.getElementById('metros_cuadrados');
    const productoSelect = document.getElementById('producto_id');
    
    const metros = parseFloat(metrosInput.value) || 0;
    const selectedOption = productoSelect.options[productoSelect.selectedIndex];
    const precioMetro = selectedOption.value ? parseFloat(selectedOption.dataset.precio) : 0;
    
    if (metros > 0 && precioMetro > 0) {
        const subtotal = metros * precioMetro;
        const impuestos = subtotal * 0.13; // 13% de impuestos
        const total = subtotal + impuestos;
        
        // Mostrar cálculos en tiempo real
        mostrarCalculos(metros, precioMetro, subtotal, impuestos, total);
    } else {
        ocultarCalculos();
    }
}

// Mostrar cálculos en tiempo real
function mostrarCalculos(metros, precioMetro, subtotal, impuestos, total) {
    let calculosDiv = document.getElementById('calculos-preview');
    
    if (!calculosDiv) {
        calculosDiv = document.createElement('div');
        calculosDiv.id = 'calculos-preview';
        calculosDiv.className = 'col-12 mt-3';
        
        // Insertar después del campo de metros cuadrados
        const metrosContainer = document.getElementById('metros_cuadrados').closest('.col-md-6');
        metrosContainer.parentNode.appendChild(calculosDiv);
    }
    
    calculosDiv.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-calculator me-2"></i>Cálculo de la Factura</h6>
            <div class="row">
                <div class="col-md-3">
                    <strong>Metros²:</strong><br>
                    ${metros.toFixed(2)} m²
                </div>
                <div class="col-md-3">
                    <strong>Precio/m²:</strong><br>
                    ₡${precioMetro.toLocaleString()}
                </div>
                <div class="col-md-3">
                    <strong>Subtotal:</strong><br>
                    ₡${subtotal.toLocaleString()}
                </div>
                <div class="col-md-3">
                    <strong>Total + IVA:</strong><br>
                    <span class="fw-bold text-success">₡${total.toLocaleString()}</span>
                </div>
            </div>
            <small class="text-muted">Impuestos (13%): ₡${impuestos.toLocaleString()}</small>
        </div>
    `;
}

// Ocultar cálculos
function ocultarCalculos() {
    const calculosDiv = document.getElementById('calculos-preview');
    if (calculosDiv) {
        calculosDiv.remove();
    }
}

// Crear factura
async function crearFactura(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    // Validar formulario
    if (!Utils.validateForm(event.target)) {
        Utils.showToast('Por favor completa todos los campos obligatorios', 'warning');
        return;
    }
    
    try {
        // Obtener datos del producto seleccionado
        const productoSelect = document.getElementById('producto_id');
        const selectedOption = productoSelect.options[productoSelect.selectedIndex];
        
        if (!selectedOption.value) {
            Utils.showToast('Por favor selecciona un producto', 'warning');
            return;
        }
        
        const precioMetro = parseFloat(selectedOption.dataset.precio);
        const productoNombre = selectedOption.textContent.split(' - ')[0]; // Obtener solo el nombre
        
        // Crear objeto de factura
        const facturaData = {
            cliente_id: parseInt(formData.get('cliente_id')) || null,
            nombre_cliente: formData.get('nombre_cliente'),
            email_cliente: formData.get('email_cliente'),
            color_seleccionado: productoNombre, // Usar el nombre del producto en lugar de color
            metros_cuadrados: parseFloat(formData.get('metros_cuadrados')),
            precio_por_metro: precioMetro,
            descripcion_servicio: formData.get('descripcion_servicio') || null,
            observaciones: formData.get('observaciones') || null
        };
        
        // Crear factura
        const factura = await API.post('/facturas', facturaData);
        
        // Subir imagen si hay una seleccionada
        if (selectedFile) {
            const imageFormData = new FormData();
            imageFormData.append('file', selectedFile);
            
            await fetch(`/api/facturas/${factura.id}/upload-imagen`, {
                method: 'POST',
                body: imageFormData
            });
        }
        
        Utils.showToast('Factura creada exitosamente', 'success');
        
        // Preguntar si quiere enviar por email
        if (confirm('¿Deseas enviar la factura por email al cliente?')) {
            await enviarFacturaPorEmail(factura.id);
        }
        
        // Redirigir a la lista de facturas
        setTimeout(() => {
            window.location.href = '/facturas';
        }, 2000);
        
    } catch (error) {
        console.error('Error creando factura:', error);
        Utils.showToast('Error creando la factura', 'danger');
    }
}

// Enviar factura por email
async function enviarFacturaPorEmail(facturaId) {
    try {
        const emailData = {
            factura_id: facturaId,
            mensaje_personalizado: null
        };
        
        await API.post(`/facturas/${facturaId}/enviar-email`, emailData);
        Utils.showToast('Factura enviada por email correctamente', 'success');
        
    } catch (error) {
        console.error('Error enviando email:', error);
        Utils.showToast('Error enviando el email', 'warning');
    }
}

// Validaciones adicionales
document.getElementById('email_cliente').addEventListener('blur', function() {
    const email = this.value;
    if (email && !Utils.validateEmail(email)) {
        this.classList.add('is-invalid');
        Utils.showToast('Email inválido', 'warning');
    } else {
        this.classList.remove('is-invalid');
    }
});

document.getElementById('metros_cuadrados').addEventListener('blur', function() {
    const metros = parseFloat(this.value);
    if (metros <= 0) {
        this.classList.add('is-invalid');
        Utils.showToast('Los metros cuadrados deben ser mayor a 0', 'warning');
    } else {
        this.classList.remove('is-invalid');
    }
});

document.getElementById('precio_por_metro').addEventListener('blur', function() {
    const precio = parseFloat(this.value);
    if (precio <= 0) {
        this.classList.add('is-invalid');
        Utils.showToast('El precio por metro debe ser mayor a 0', 'warning');
    } else {
        this.classList.remove('is-invalid');
    }
});
