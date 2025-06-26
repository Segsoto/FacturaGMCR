// JavaScript para el Dashboard

let ventasChart;

// Cargar datos del dashboard al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarEstadisticas();
    cargarVentasPorMes();
    cargarProductosMasVendidos();
    cargarClientesTop();
});

// Cargar estadísticas principales
async function cargarEstadisticas() {
    try {
        const estadisticas = await API.get('/dashboard/estadisticas');
        
        // Actualizar las tarjetas de estadísticas
        document.getElementById('ventas-mes').textContent = Utils.formatCurrency(estadisticas.total_ventas_mes);
        document.getElementById('facturas-mes').textContent = estadisticas.total_facturas_mes;
        document.getElementById('total-clientes').textContent = estadisticas.total_clientes;
        document.getElementById('facturas-pendientes').textContent = estadisticas.facturas_pendientes;
        
        // Agregar animación a los números
        animateNumbers();
        
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

// Cargar datos de ventas por mes para el gráfico
async function cargarVentasPorMes() {
    try {
        const ventasPorMes = await API.get('/dashboard/ventas-por-mes');
        
        // Crear el gráfico de ventas
        crearGraficoVentas(ventasPorMes);
        
    } catch (error) {
        console.error('Error al cargar ventas por mes:', error);
    }
}

// Crear gráfico de ventas con Chart.js
function crearGraficoVentas(datos) {
    const ctx = document.getElementById('ventasChart').getContext('2d');
    
    // Preparar datos para el gráfico
    const labels = datos.map(item => item.mes);
    const ventasData = datos.map(item => item.total_ventas);
    const facturasData = datos.map(item => item.total_facturas);
    
    // Destruir gráfico anterior si existe
    if (ventasChart) {
        ventasChart.destroy();
    }
    
    ventasChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas (₡)',
                data: ventasData,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
                yAxisID: 'y'
            }, {
                label: 'Facturas',
                data: facturasData,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Mes'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Ventas (₡)'
                    },
                    ticks: {
                        callback: function(value) {
                            return Utils.formatCurrency(value);
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Cantidad de Facturas'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 0) {
                                label += Utils.formatCurrency(context.parsed.y);
                            } else {
                                label += context.parsed.y;
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// Cargar productos más vendidos
async function cargarProductosMasVendidos() {
    try {
        const productos = await API.get('/dashboard/productos-mas-vendidos');
        const container = document.getElementById('productos-vendidos');
        
        if (productos.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay datos disponibles</p>';
            return;
        }
        
        let html = '';
        productos.forEach((producto, index) => {
            const porcentaje = index === 0 ? 100 : (producto.total_vendido / productos[0].total_vendido) * 100;
            
            html += `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="fw-bold">${producto.nombre}</span>
                        <span class="text-muted">${producto.total_vendido}</span>
                    </div>
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar bg-primary" role="progressbar" 
                             style="width: ${porcentaje}%" 
                             aria-valuenow="${porcentaje}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                        </div>
                    </div>
                    <small class="text-muted">
                        Código: ${producto.codigo} | 
                        Ingresos: ${Utils.formatCurrency(producto.total_ingresos)}
                    </small>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error al cargar productos más vendidos:', error);
        document.getElementById('productos-vendidos').innerHTML = 
            '<p class="text-danger">Error al cargar datos</p>';
    }
}

// Cargar mejores clientes
async function cargarClientesTop() {
    try {
        const clientes = await API.get('/dashboard/clientes-top');
        const tbody = document.querySelector('#tabla-clientes-top tbody');
        
        if (clientes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted">No hay datos disponibles</td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        clientes.forEach(cliente => {
            html += `
                <tr>
                    <td>
                        <div class="fw-bold">${cliente.nombre_completo}</div>
                    </td>
                    <td>${cliente.cedula}</td>
                    <td>
                        <span class="badge bg-primary">${cliente.total_facturas}</span>
                    </td>
                    <td class="fw-bold text-success">
                        ${Utils.formatCurrency(cliente.total_compras)}
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        
    } catch (error) {
        console.error('Error al cargar clientes top:', error);
        document.querySelector('#tabla-clientes-top tbody').innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">Error al cargar datos</td>
            </tr>
        `;
    }
}

// Animar números en las tarjetas de estadísticas
function animateNumbers() {
    const elements = [
        { id: 'ventas-mes', isCurrency: true },
        { id: 'facturas-mes', isCurrency: false },
        { id: 'total-clientes', isCurrency: false },
        { id: 'facturas-pendientes', isCurrency: false }
    ];
    
    elements.forEach(element => {
        const el = document.getElementById(element.id);
        const finalValue = parseFloat(el.textContent.replace(/[^\d.-]/g, ''));
        
        if (isNaN(finalValue)) return;
        
        let currentValue = 0;
        const increment = finalValue / 50; // 50 steps
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(timer);
            }
            
            if (element.isCurrency) {
                el.textContent = Utils.formatCurrency(currentValue);
            } else {
                el.textContent = Math.floor(currentValue);
            }
        }, 20);
    });
}

// Función para refrescar datos
function refrescarDatos() {
    cargarEstadisticas();
    cargarVentasPorMes();
    cargarProductosMasVendidos();
    cargarClientesTop();
    Utils.showToast('Datos actualizados correctamente', 'success');
}

// Auto-refresh cada 5 minutos
setInterval(() => {
    cargarEstadisticas();
}, 300000); // 5 minutos
