/**
 * Shop Template - Application JavaScript
 * =====================================
 * Main application entry point that initializes all modules
 */

// ============================================
// Application Initializer
// ============================================
class ShopTemplateApp {
    constructor() {
        this.modules = {};
        this.init();
    }
    
    init() {
        console.log('Initializing Shop Template Application...');
        
        // Initialize core modules
        this.initCoreModules();
        
        // Initialize page-specific modules
        this.initPageModules();
        
        // Initialize third-party integrations
        this.initThirdParty();
        
        // Log initialization
        this.logInitializedModules();
    }
    
    initCoreModules() {
        // Theme system
        this.modules.theme = {
            initialized: true,
            instance: ShopTemplate
        };
        
        // Main functionality
        this.modules.main = {
            initialized: true,
            instance: window.ShopTemplate
        };
    }
    
    initPageModules() {
        const body = document.body;
        
        // Store pages
        if (body.classList.contains('page-store') || 
            body.classList.contains('page-product') ||
            body.classList.contains('page-products') ||
            body.classList.contains('page-cart') ||
            body.classList.contains('page-wishlist') ||
            body.classList.contains('page-compare')) {
            this.modules.store = {
                initialized: true,
                instance: window.Store
            };
        }
        
        // Blog pages
        if (body.classList.contains('page-blog') || 
            body.classList.contains('page-post')) {
            this.modules.blog = {
                initialized: true,
                instance: window.BlogModule
            };
        }
        
        // Checkout pages
        if (body.classList.contains('page-checkout')) {
            this.modules.checkout = {
                initialized: true,
                instance: window.CheckoutProcess
            };
        }
        
        // Auth pages
        if (body.classList.contains('page-login') ||
            body.classList.contains('page-register') ||
            body.classList.contains('page-forgot-password') ||
            body.classList.contains('page-reset-password') ||
            body.classList.contains('page-account')) {
            this.modules.auth = {
                initialized: true,
                instance: window.Auth
            };
        }
        
        // Admin pages
        if (body.classList.contains('page-admin')) {
            this.modules.admin = {
                initialized: true,
                instance: window.Admin
            };
        }
        
        // Contact page
        if (body.classList.contains('page-contact')) {
            this.modules.contact = {
                initialized: true
            };
        }
        
        // Profile pages
        if (body.classList.contains('page-profile') ||
            body.classList.contains('page-dashboard')) {
            this.modules.profile = {
                initialized: true
            };
        }
    }
    
    initThirdParty() {
        // Initialize any third-party libraries
        // In a real app, you might initialize:
        // - Payment gateways (Stripe, PayPal)
        // - Analytics (Google Analytics)
        // - Chat systems (Intercom, Drift)
        // - Social media widgets
        
        console.log('Initializing third-party integrations...');
    }
    
    logInitializedModules() {
        console.log('Shop Template Application Initialized');
        console.log('--------------------------------------');
        for (const [name, module] of Object.entries(this.modules)) {
            console.log(`- ${name.charAt(0).toUpperCase() + name.slice(1)}: ${module.initialized ? 'Initialized' : 'Not initialized'}`);
        }
        console.log('--------------------------------------');
    }
    
    // ============================================
    // Utility Methods
    // ============================================
    
    getModule(name) {
        return this.modules[name]?.instance;
    }
    
    isModuleInitialized(name) {
        return this.modules[name]?.initialized || false;
    }
    
    // ============================================
    // Event Bus
    // ============================================
    
    static eventBus = {
        events: {},
        
        on(event, callback) {
            if (!this.events[event]) {
                this.events[event] = [];
            }
            this.events[event].push(callback);
        },
        
        emit(event, ...args) {
            if (this.events[event]) {
                this.events[event].forEach(callback => {
                    callback(...args);
                });
            }
        },
        
        off(event, callback) {
            if (this.events[event]) {
                this.events[event] = this.events[event].filter(cb => cb !== callback);
            }
        }
    };
    
    // ============================================
    // State Management
    // ============================================
    
    static state = {
        cart: null,
        wishlist: null,
        compare: null,
        auth: null,
        theme: null,
        
        getCart() {
            return this.cart || (window.cart ? window.cart : null);
        },
        
        getWishlist() {
            return this.wishlist || (window.wishlist ? window.wishlist : null);
        },
        
        getCompare() {
            return this.compare || (window.compare ? window.compare : null);
        },
        
        getAuth() {
            return this.auth || (window.authManager ? window.authManager : null);
        },
        
        getTheme() {
            return this.theme || ShopTemplate.settings;
        }
    };
    
    // ============================================
    // API Client
    // ============================================
    
    static api = {
        baseUrl: '/api/v1/',
        
        async request(method, endpoint, data = null, headers = {}) {
            const url = this.baseUrl + endpoint;
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    ...headers
                }
            };
            
            // Add auth token if available
            const auth = ShopTemplateApp.state.getAuth();
            if (auth && auth.getToken()) {
                options.headers['Authorization'] = `Bearer ${auth.getToken()}`;
            }
            
            if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
                options.body = JSON.stringify(data);
            }
            
            try {
                const response = await fetch(url, options);
                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.message || 'Request failed');
                }
                
                return result;
            } catch (error) {
                console.error('API Error:', error);
                throw error;
            }
        },
        
        async get(endpoint, headers = {}) {
            return this.request('GET', endpoint, null, headers);
        },
        
        async post(endpoint, data = null, headers = {}) {
            return this.request('POST', endpoint, data, headers);
        },
        
        async put(endpoint, data = null, headers = {}) {
            return this.request('PUT', endpoint, data, headers);
        },
        
        async patch(endpoint, data = null, headers = {}) {
            return this.request('PATCH', endpoint, data, headers);
        },
        
        async delete(endpoint, headers = {}) {
            return this.request('DELETE', endpoint, null, headers);
        }
    };
    
    // ============================================
    // Storage Utilities
    // ============================================
    
    static storage = {
        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                return defaultValue;
            }
        },
        
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (e) {
                return false;
            }
        },
        
        remove(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (e) {
                return false;
            }
        },
        
        clear() {
            try {
                localStorage.clear();
                return true;
            } catch (e) {
                return false;
            }
        },
        
        session: {
            get(key, defaultValue = null) {
                try {
                    const item = sessionStorage.getItem(key);
                    return item ? JSON.parse(item) : defaultValue;
                } catch (e) {
                    return defaultValue;
                }
            },
            
            set(key, value) {
                try {
                    sessionStorage.setItem(key, JSON.stringify(value));
                    return true;
                } catch (e) {
                    return false;
                }
            },
            
            remove(key) {
                try {
                    sessionStorage.removeItem(key);
                    return true;
                } catch (e) {
                    return false;
                }
            },
            
            clear() {
                try {
                    sessionStorage.clear();
                    return true;
                } catch (e) {
                    return false;
                }
            }
        }
    };
}

// ============================================
// Initialize Application
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Create global app instance
    window.ShopTemplateApp = new ShopTemplateApp();
    
    // Make utilities available globally
    window.App = {
        eventBus: ShopTemplateApp.eventBus,
        state: ShopTemplateApp.state,
        api: ShopTemplateApp.api,
        storage: ShopTemplateApp.storage
    };
    
    // Dispatch ready event
    ShopTemplateApp.eventBus.emit('app:ready');
    
    // Log initialization
    console.log('%c Shop Template ', 'background: #3b82f6; color: white; font-size: 20px; padding: 10px;');
    console.log('%c Application initialized successfully! ', 'color: #22c55e; font-size: 14px;');
});

// ============================================
// Error Handling
// ============================================
window.addEventListener('error', (event) => {
    console.error('Unhandled error:', event.error);
    ShopTemplate.showToast('An error occurred. Please try again.', 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);
    ShopTemplate.showToast('An error occurred. Please try again.', 'error');
});

// ============================================
// Before Unload
// ============================================
window.addEventListener('beforeunload', (event) => {
    // Check if there are unsaved changes
    if (window.hasUnsavedChanges) {
        event.preventDefault();
        event.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return event.returnValue;
    }
});

// ============================================
// Online/Offline Detection
// ============================================
window.addEventListener('online', () => {
    ShopTemplate.showToast('You are now online', 'success');
    ShopTemplateApp.eventBus.emit('network:online');
});

window.addEventListener('offline', () => {
    ShopTemplate.showToast('You are offline. Some features may not work.', 'warning');
    ShopTemplateApp.eventBus.emit('network:offline');
});

// ============================================
// Export
// ============================================
window.ShopTemplateApp = window.ShopTemplateApp || {};
