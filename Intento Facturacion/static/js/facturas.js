// JavaScript para Gestión de Facturas

let facturasCache = [];
let paginaActual = 1;
let facturaActual = null;
const facturasPorPagina = 20;

document.addEventListener('DOMContentLoaded', function() {
    cargarFacturas();
    cargarEstadisticas();
    inicializarEventos();
});

// Inicializar eventos
function inicializarEventos() {
    // Eventos de filtros
    document.getElementById('btn-buscar').addEventListener('click', aplicarFiltros);
    document.getElementById('btn-limpiar').addEventListener('click', limpiarFiltros);
    
    // Evento para buscar cuando se presiona Enter en los campos de filtro
    const filtros = document.querySelectorAll('#form-filtros input, #form-filtros select');
    filtros.forEach(filtro => {
        filtro.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                aplicarFiltros();
            }
        });
    });
    
    // Eventos de modales
    document.getElementById('btn-enviar-email').addEventListener('click', mostrarModalEnviarEmail);
    document.getElementById('btn-confirmar-envio').addEventListener('click', confirmarEnvioEmail);
    document.getElementById('btn-imprimir').addEventListener('click', imprimirFactura);
}

// Cargar facturas
async function cargarFacturas(filtros = {}) {
    try {
        Utils.showLoading();
        
        // Construir parámetros de consulta
        const params = new URLSearchParams({
            skip: (paginaActual - 1) * facturasPorPagina,
            limit: facturasPorPagina,
            ...filtros
        });
        
        const facturas = await API.get(`/facturas?${params}`);
        facturasCache = facturas;
        
        mostrarFacturas(facturas);
        
    } catch (error) {
        console.error('Error cargando facturas:', error);
        Utils.showToast('Error cargando facturas', 'danger');
    } finally {
        Utils.hideLoading();
    }
}

// Mostrar facturas en la tabla
function mostrarFacturas(facturas) {
    const tbody = document.querySelector('#tabla-facturas tbody');
    
    if (facturas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted">
                    No se encontraron facturas
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = facturas.map(factura => `
        <tr>
            <td>
                <strong class="text-primary">${factura.numero_factura}</strong>
            </td>
            <td>
                <div class="fw-bold">${factura.nombre_cliente}</div>
            </td>
            <td>
                <small class="text-muted">${factura.email_cliente}</small>
            </td>
            <td>
                <small>${Utils.formatDate(factura.fecha_emision)}</small>
            </td>
            <td>
                <span class="badge bg-info">${factura.metros_cuadrados} m²</span>
            </td>
            <td>
                ${factura.color_seleccionado ? 
                    `<span class="badge bg-secondary">${factura.color_seleccionado}</span>` : 
                    '<span class="text-muted">-</span>'
                }
            </td>
            <td>
                <strong class="text-success">${Utils.formatCurrency(factura.total)}</strong>
            </td>
            <td>
                <span class="badge badge-estado-${factura.estado.toLowerCase()}">${factura.estado}</span>
            </td>
            <td>
                ${factura.email_enviado ? 
                    `<i class="fas fa-check-circle email-enviado" title="Enviado ${factura.fecha_envio_email ? Utils.formatDateTime(factura.fecha_envio_email) : ''}"></i>` :
                    '<i class="fas fa-times-circle email-no-enviado" title="No enviado"></i>'
                }
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="verFactura(${factura.id})" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="enviarEmailDirecto(${factura.id})" title="Enviar email">
                        <i class="fas fa-envelope"></i>
                    </button>
                    ${factura.estado !== 'ANULADA' ? 
                        `<button class="btn btn-outline-danger" onclick="anularFactura(${factura.id})" title="Anular">
                            <i class="fas fa-ban"></i>
                        </button>` : ''
                    }
                </div>
            </td>
        </tr>
    `).join('');
}

// Ver detalle de factura
async function verFactura(facturaId) {
    try {
        const factura = await API.get(`/facturas/${facturaId}`);
        facturaActual = factura;
        mostrarDetalleFactura(factura);
        
        const modal = new bootstrap.Modal(document.getElementById('modal-ver-factura'));
        modal.show();
        
    } catch (error) {
        console.error('Error cargando factura:', error);
        Utils.showToast('Error cargando los detalles de la factura', 'danger');
    }
}

// Mostrar detalle de factura en el modal
function mostrarDetalleFactura(factura) {
    const contenido = document.getElementById('contenido-factura');
    
    const imagenHtml = factura.imagen_modelo ? 
        `<div class="text-center mb-3">
            <img src="/${factura.imagen_modelo}" alt="Modelo" class="factura-imagen">
        </div>` : '';
    
    contenido.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-primary">Información de la Factura</h6>
                <table class="table table-sm">
                    <tr>
                        <th>Número:</th>
                        <td>${factura.numero_factura}</td>
                    </tr>
                    <tr>
                        <th>Fecha:</th>
                        <td>${Utils.formatDateTime(factura.fecha_emision)}</td>
                    </tr>
                    <tr>
                        <th>Estado:</th>
                        <td><span class="badge badge-estado-${factura.estado.toLowerCase()}">${factura.estado}</span></td>
                    </tr>
                    <tr>
                        <th>Email enviado:</th>
                        <td>
                            ${factura.email_enviado ? 
                                `<i class="fas fa-check text-success"></i> Sí (${factura.fecha_envio_email ? Utils.formatDateTime(factura.fecha_envio_email) : ''})` :
                                '<i class="fas fa-times text-danger"></i> No'
                            }
                        </td>
                    </tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-primary">Información del Cliente</h6>
                <table class="table table-sm">
                    <tr>
                        <th>Nombre:</th>
                        <td>${factura.nombre_cliente}</td>
                    </tr>
                    <tr>
                        <th>Email:</th>
                        <td>${factura.email_cliente}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        ${imagenHtml}
        
        <div class="row">
            <div class="col-12">
                <h6 class="text-primary">Detalles del Servicio</h6>
                <table class="table table-sm">
                    <tr>
                        <th>Descripción:</th>
                        <td>${factura.descripcion_servicio || 'No especificada'}</td>
                    </tr>
                    <tr>
                        <th>Color:</th>
                        <td>${factura.color_seleccionado || 'No especificado'}</td>
                    </tr>
                    <tr>
                        <th>Metros cuadrados:</th>
                        <td><strong>${factura.metros_cuadrados} m²</strong></td>
                    </tr>
                    <tr>
                        <th>Precio por m²:</th>
                        <td>${Utils.formatCurrency(factura.precio_por_metro)}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <h6 class="text-primary">Totales</h6>
                <table class="table table-sm">
                    <tr>
                        <th>Subtotal:</th>
                        <td>${Utils.formatCurrency(factura.subtotal)}</td>
                    </tr>
                    <tr>
                        <th>Impuestos (13%):</th>
                        <td>${Utils.formatCurrency(factura.impuestos)}</td>
                    </tr>
                    <tr class="table-primary">
                        <th><strong>Total:</strong></th>
                        <td><strong>${Utils.formatCurrency(factura.total)}</strong></td>
                    </tr>
                </table>
            </div>
        </div>
        
        ${factura.observaciones ? 
            `<div class="row">
                <div class="col-12">
                    <h6 class="text-primary">Observaciones</h6>
                    <div class="alert alert-info">${factura.observaciones}</div>
                </div>
            </div>` : ''
        }
    `;
}

// Aplicar filtros
function aplicarFiltros() {
    paginaActual = 1; // Resetear a primera página
    
    const filtros = {};
    
    const nombre = document.getElementById('filtro-nombre').value.trim();
    if (nombre) filtros.nombre_cliente = nombre;
    
    const email = document.getElementById('filtro-email').value.trim();
    if (email) filtros.email_cliente = email;
    
    const estado = document.getElementById('filtro-estado').value;
    if (estado) filtros.estado = estado;
    
    const fechaDesde = document.getElementById('filtro-fecha-desde').value;
    if (fechaDesde) filtros.fecha_desde = fechaDesde;
    
    const fechaHasta = document.getElementById('filtro-fecha-hasta').value;
    if (fechaHasta) filtros.fecha_hasta = fechaHasta;
    
    const color = document.getElementById('filtro-color').value.trim();
    if (color) filtros.color = color;
    
    const metrosMin = document.getElementById('filtro-metros-min').value;
    if (metrosMin) filtros.metros_min = metrosMin;
    
    const metrosMax = document.getElementById('filtro-metros-max').value;
    if (metrosMax) filtros.metros_max = metrosMax;
    
    cargarFacturas(filtros);
}

// Limpiar filtros
function limpiarFiltros() {
    document.getElementById('form-filtros').reset();
    paginaActual = 1;
    cargarFacturas();
}

// Cargar estadísticas
async function cargarEstadisticas() {
    try {
        const stats = await API.get('/facturas/estadisticas/resumen');
        
        document.getElementById('stat-total-facturas').textContent = stats.total_facturas;
        document.getElementById('stat-total-ventas').textContent = Utils.formatCurrency(stats.total_ventas);
        document.getElementById('stat-promedio-metros').textContent = stats.promedio_metros_cuadrados + ' m²';
        
        // Buscar facturas pendientes
        const pendientes = stats.estadisticas_por_estado.find(e => e.estado === 'PENDIENTE');
        document.getElementById('stat-pendientes').textContent = pendientes ? pendientes.cantidad : 0;
        
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

// Mostrar modal para enviar email
function mostrarModalEnviarEmail() {
    const modal = new bootstrap.Modal(document.getElementById('modal-enviar-email'));
    modal.show();
}

// Enviar email directo
async function enviarEmailDirecto(facturaId) {
    try {
        const emailData = {
            factura_id: facturaId,
            mensaje_personalizado: null
        };
        
        await API.post(`/facturas/${facturaId}/enviar-email`, emailData);
        Utils.showToast('Factura enviada por email correctamente', 'success');
        
        // Recargar facturas para actualizar estado
        cargarFacturas();
        
    } catch (error) {
        console.error('Error enviando email:', error);
        Utils.showToast('Error enviando el email', 'danger');
    }
}

// Confirmar envío de email
async function confirmarEnvioEmail() {
    if (!facturaActual) return;
    
    try {
        const emailAdicional = document.getElementById('email-adicional').value.trim();
        const mensajePersonalizado = document.getElementById('mensaje-personalizado').value.trim();
        
        const emailData = {
            factura_id: facturaActual.id,
            email_adicional: emailAdicional || null,
            mensaje_personalizado: mensajePersonalizado || null
        };
        
        await API.post(`/facturas/${facturaActual.id}/enviar-email`, emailData);
        Utils.showToast('Factura enviada por email correctamente', 'success');
        
        // Cerrar modal y recargar datos
        bootstrap.Modal.getInstance(document.getElementById('modal-enviar-email')).hide();
        bootstrap.Modal.getInstance(document.getElementById('modal-ver-factura')).hide();
        cargarFacturas();
        
    } catch (error) {
        console.error('Error enviando email:', error);
        Utils.showToast('Error enviando el email', 'danger');
    }
}

// Anular factura
async function anularFactura(facturaId) {
    if (!confirm('¿Estás seguro de que deseas anular esta factura?')) {
        return;
    }
    
    try {
        await API.post(`/facturas/${facturaId}/anular`);
        Utils.showToast('Factura anulada correctamente', 'success');
        cargarFacturas();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error anulando factura:', error);
        Utils.showToast('Error anulando la factura', 'danger');
    }
}

// Imprimir factura
function imprimirFactura() {
    if (!facturaActual) return;
    
    const contenido = document.getElementById('contenido-factura').innerHTML;
    const ventanaImpresion = window.open('', '_blank');
    
    ventanaImpresion.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Factura ${facturaActual.numero_factura}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .table th { background-color: #f8f9fa; }
                .text-primary { color: #007bff; }
                .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
                .alert { padding: 15px; border-radius: 4px; background-color: #d1ecf1; }
                .factura-imagen { max-width: 300px; }
                @media print {
                    body { margin: 0; }
                    .no-print { display: none; }
                }
            </style>
        </head>
        <body>
            <h1>Granimar CR - Factura ${facturaActual.numero_factura}</h1>
            ${contenido}
        </body>
        </html>
    `);
    
    ventanaImpresion.document.close();
    ventanaImpresion.focus();
    ventanaImpresion.print();
}

// Auto-refrescar cada 5 minutos
setInterval(() => {
    cargarEstadisticas();
}, 300000);
