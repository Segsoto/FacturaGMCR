// Utilidades JavaScript para el sistema de facturación Granimar CR

// Configuración de Axios
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Utilidades generales
const Utils = {
    // Formatear números como moneda
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('es-CR', {
            style: 'currency',
            currency: 'CRC'
        }).format(amount);
    },

    // Formatear fechas
    formatDate: (dateString) => {
        return new Date(dateString).toLocaleDateString('es-CR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Formatear fecha y hora
    formatDateTime: (dateString) => {
        return new Date(dateString).toLocaleString('es-CR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Mostrar mensaje toast
    showToast: (message, type = 'info') => {
        const toastContainer = document.getElementById('toast-container');
        const toastId = 'toast-' + Date.now();
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        
        toast.show();
        
        // Eliminar el toast del DOM después de que se oculte
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },

    // Mostrar loading overlay
    showLoading: () => {
        const loadingHtml = `
            <div id="loading-overlay" class="loading-overlay">
                <div class="spinner-border spinner-border-lg text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    },

    // Ocultar loading overlay
    hideLoading: () => {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    },

    // Confirmar acción
    confirm: (message, callback) => {
        if (confirm(message)) {
            callback();
        }
    },

    // Validar formulario
    validateForm: (formElement) => {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },

    // Limpiar formulario
    clearForm: (formElement) => {
        formElement.reset();
        const inputs = formElement.querySelectorAll('.is-invalid');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
    },

    // Debounce para búsquedas
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Validar cédula costarricense
    validateCedula: (cedula) => {
        cedula = cedula.replace(/[^0-9]/g, '');
        
        if (cedula.length !== 9) {
            return false;
        }
        
        // Algoritmo para validar cédula costarricense
        const weights = [3, 4, 5, 6, 7, 8, 9, 2];
        let sum = 0;
        
        for (let i = 0; i < 8; i++) {
            sum += parseInt(cedula[i]) * weights[i];
        }
        
        const remainder = sum % 11;
        const checkDigit = remainder < 2 ? remainder : 11 - remainder;
        
        return checkDigit === parseInt(cedula[8]);
    },

    // Formatear cédula
    formatCedula: (cedula) => {
        cedula = cedula.replace(/[^0-9]/g, '');
        if (cedula.length === 9) {
            return cedula.replace(/(\d{1})(\d{4})(\d{4})/, '$1-$2-$3');
        }
        return cedula;
    },

    // Validar email
    validateEmail: (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Generar código de producto
    generateProductCode: (name) => {
        const words = name.toUpperCase().split(' ');
        let code = '';
        
        words.forEach(word => {
            if (word.length > 0) {
                code += word[0];
            }
        });
        
        // Agregar timestamp para unicidad
        const timestamp = Date.now().toString().slice(-4);
        return code + timestamp;
    },

    // Calcular subtotal
    calculateSubtotal: (quantity, unitPrice) => {
        return parseFloat((quantity * unitPrice).toFixed(2));
    },

    // Calcular impuestos (13% en Costa Rica)
    calculateTax: (subtotal) => {
        return parseFloat((subtotal * 0.13).toFixed(2));
    },

    // Calcular total
    calculateTotal: (subtotal, tax) => {
        return parseFloat((subtotal + tax).toFixed(2));
    }
};

// API Helper
const API = {
    // Configuración base
    baseURL: '/api',

    // Métodos genéricos
    get: async (url) => {
        try {
            Utils.showLoading();
            const response = await axios.get(`${API.baseURL}${url}`);
            return response.data;
        } catch (error) {
            Utils.showToast(`Error: ${error.response?.data?.detail || error.message}`, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    },

    post: async (url, data) => {
        try {
            Utils.showLoading();
            const response = await axios.post(`${API.baseURL}${url}`, data);
            return response.data;
        } catch (error) {
            Utils.showToast(`Error: ${error.response?.data?.detail || error.message}`, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    },

    put: async (url, data) => {
        try {
            Utils.showLoading();
            const response = await axios.put(`${API.baseURL}${url}`, data);
            return response.data;
        } catch (error) {
            Utils.showToast(`Error: ${error.response?.data?.detail || error.message}`, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    },

    delete: async (url) => {
        try {
            Utils.showLoading();
            const response = await axios.delete(`${API.baseURL}${url}`);
            return response.data;
        } catch (error) {
            Utils.showToast(`Error: ${error.response?.data?.detail || error.message}`, 'danger');
            throw error;
        } finally {
            Utils.hideLoading();
        }
    }
};

// Event Listeners globales
document.addEventListener('DOMContentLoaded', function() {
    // Activar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Activar popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Marcar elemento de navegación activo
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// Exportar utilidades para uso global
window.Utils = Utils;
window.API = API;
