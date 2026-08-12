/**
 * Shop Template - Main JavaScript
 * ==============================
 * Main application JavaScript file
 */

// ============================================
// Configuration
// ============================================
const ShopTemplate = {
    // Breakpoints
    breakpoints: {
        xs: 576,
        sm: 768,
        md: 992,
        lg: 1200,
        xl: 1400
    },
    
    // Storage keys
    storage: {
        theme: 'shop-template-theme',
        themeColor: 'shop-template-theme-color',
        sidebarCollapsed: 'shop-template-sidebar-collapsed'
    },
    
    // Default settings
    settings: {
        theme: 'light',
        themeColor: 'light-blue',
        sidebarCollapsed: false
    }
};

// ============================================
// DOM Ready
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initThemeColor();
    initSidebar();
    initMobileMenu();
    initDropdowns();
    initModals();
    initToasts();
    initTabs();
    initAccordion();
    initQuantityInput();
    initStarRating();
    initFileInput();
    initPasswordStrength();
    initFormValidation();
    initLazyLoading();
    initScrollToTop();
    initTooltip();
    initCopyToClipboard();
    initNotificationBadge();
    initCartSidebar();
    initWishlistSidebar();
    initCompareSidebar();
    initSearch();
    initProductTabs();
    initProductGallery();
    initCheckoutSteps();
    initThemeSwitcher();
    initColorThemeSwitcher();
    initRTLSupport();
});

// ============================================
// Theme Management
// ============================================
function initTheme() {
    const savedTheme = localStorage.getItem(ShopTemplate.storage.theme);
    if (savedTheme) {
        ShopTemplate.settings.theme = savedTheme;
    }
    
    // Check for system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (!savedTheme && prefersDark) {
        ShopTemplate.settings.theme = 'dark';
    }
    
    applyTheme();
    
    // Watch for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem(ShopTemplate.storage.theme)) {
            ShopTemplate.settings.theme = e.matches ? 'dark' : 'light';
            applyTheme();
        }
    });
}

function applyTheme() {
    const html = document.documentElement;
    
    // Remove existing theme classes
    html.classList.remove('light', 'dark');
    
    // Apply theme
    html.classList.add(ShopTemplate.settings.theme);
    html.setAttribute('data-theme', ShopTemplate.settings.theme);
    
    // Update theme switcher buttons
    updateThemeSwitcher();
    
    // Save to storage
    localStorage.setItem(ShopTemplate.storage.theme, ShopTemplate.settings.theme);
}

function toggleTheme() {
    ShopTemplate.settings.theme = ShopTemplate.settings.theme === 'light' ? 'dark' : 'light';
    applyTheme();
}

function initThemeSwitcher() {
    const themeSwitcher = document.querySelector('.theme-switcher');
    if (!themeSwitcher) return;
    
    const lightBtn = themeSwitcher.querySelector('.theme-switcher-btn.light');
    const darkBtn = themeSwitcher.querySelector('.theme-switcher-btn.dark');
    
    lightBtn?.addEventListener('click', () => {
        ShopTemplate.settings.theme = 'light';
        applyTheme();
    });
    
    darkBtn?.addEventListener('click', () => {
        ShopTemplate.settings.theme = 'dark';
        applyTheme();
    });
}

function updateThemeSwitcher() {
    const themeSwitcher = document.querySelector('.theme-switcher');
    if (!themeSwitcher) return;
    
    const lightBtn = themeSwitcher.querySelector('.theme-switcher-btn.light');
    const darkBtn = themeSwitcher.querySelector('.theme-switcher-btn.dark');
    
    lightBtn?.classList.toggle('active', ShopTemplate.settings.theme === 'light');
    darkBtn?.classList.toggle('active', ShopTemplate.settings.theme === 'dark');
}

// ============================================
// Theme Color Management
// ============================================
function initThemeColor() {
    const savedThemeColor = localStorage.getItem(ShopTemplate.storage.themeColor);
    if (savedThemeColor) {
        ShopTemplate.settings.themeColor = savedThemeColor;
    }
    
    applyThemeColor();
}

function applyThemeColor() {
    const html = document.documentElement;
    
    // Remove existing theme color classes
    html.classList.remove('light-blue', 'dark-blue', 'green', 'purple', 'orange', 'red');
    
    // Apply theme color
    html.classList.add(ShopTemplate.settings.themeColor);
    html.setAttribute('data-theme-color', ShopTemplate.settings.themeColor);
    
    // Update color theme switcher
    updateColorThemeSwitcher();
    
    // Save to storage
    localStorage.setItem(ShopTemplate.storage.themeColor, ShopTemplate.settings.themeColor);
}

function setThemeColor(color) {
    ShopTemplate.settings.themeColor = color;
    applyThemeColor();
}

function initColorThemeSwitcher() {
    const colorOptions = document.querySelectorAll('.theme-color-option');
    colorOptions.forEach(option => {
        option.addEventListener('click', () => {
            const color = option.classList.contains('light-blue') ? 'light-blue' :
                          option.classList.contains('dark-blue') ? 'dark-blue' :
                          option.classList.contains('green') ? 'green' :
                          option.classList.contains('purple') ? 'purple' :
                          option.classList.contains('orange') ? 'orange' : 'red';
            setThemeColor(color);
        });
    });
}

function updateColorThemeSwitcher() {
    const colorOptions = document.querySelectorAll('.theme-color-option');
    colorOptions.forEach(option => {
        const color = option.classList.contains('light-blue') ? 'light-blue' :
                      option.classList.contains('dark-blue') ? 'dark-blue' :
                      option.classList.contains('green') ? 'green' :
                      option.classList.contains('purple') ? 'purple' :
                      option.classList.contains('orange') ? 'orange' : 'red';
        option.classList.toggle('active', color === ShopTemplate.settings.themeColor);
    });
}

// ============================================
// Sidebar Management
// ============================================
function initSidebar() {
    const savedState = localStorage.getItem(ShopTemplate.storage.sidebarCollapsed);
    if (savedState) {
        ShopTemplate.settings.sidebarCollapsed = savedState === 'true';
    }
    
    applySidebarState();
    
    // Toggle button
    const toggleBtn = document.querySelector('.admin-sidebar-close');
    toggleBtn?.addEventListener('click', toggleSidebar);
    
    // Mobile menu toggle
    const mobileToggle = document.querySelector('.admin-header-menu-toggle');
    mobileToggle?.addEventListener('click', toggleSidebar);
    
    // Navigation items with dropdowns
    const navItems = document.querySelectorAll('.admin-nav-item.has-dropdown');
    navItems.forEach(item => {
        const header = item.querySelector('.admin-nav-item a');
        header?.addEventListener('click', (e) => {
            if (window.innerWidth >= ShopTemplate.breakpoints.md) {
                e.preventDefault();
                toggleNavDropdown(item);
            }
        });
    });
}

function applySidebarState() {
    const sidebar = document.querySelector('.admin-sidebar');
    if (!sidebar) return;
    
    sidebar.classList.toggle('collapsed', ShopTemplate.settings.sidebarCollapsed);
    
    // Save to storage
    localStorage.setItem(ShopTemplate.storage.sidebarCollapsed, ShopTemplate.settings.sidebarCollapsed);
}

function toggleSidebar() {
    ShopTemplate.settings.sidebarCollapsed = !ShopTemplate.settings.sidebarCollapsed;
    applySidebarState();
}

function toggleNavDropdown(item) {
    item.classList.toggle('open');
}

// ============================================
// Mobile Menu
// ============================================
function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
    
    if (!mobileMenuToggle || !mobileMenu) return;
    
    mobileMenuToggle.addEventListener('click', () => {
        mobileMenu.classList.add('open');
        mobileMenuOverlay?.classList.add('show');
        document.body.style.overflow = 'hidden';
    });
    
    mobileMenuClose?.addEventListener('click', closeMobileMenu);
    mobileMenuOverlay?.addEventListener('click', closeMobileMenu);
}

function closeMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
    
    mobileMenu?.classList.remove('open');
    mobileMenuOverlay?.classList.remove('show');
    document.body.style.overflow = '';
}

// ============================================
// Dropdowns
// ============================================
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!toggle || !menu) return;
        
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            
            // Close other dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(otherMenu => {
                if (otherMenu !== menu) {
                    otherMenu.classList.remove('show');
                    otherMenu.parentElement.querySelector('.dropdown-toggle')?.classList.remove('open');
                }
            });
            
            // Toggle current dropdown
            toggle.classList.toggle('open');
            menu.classList.toggle('show');
        });
        
        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                menu.classList.remove('show');
                toggle.classList.remove('open');
            }
        });
    });
}

// ============================================
// Modals
// ============================================
let activeModal = null;

function initModals() {
    const modals = document.querySelectorAll('.modal');
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const modalCloses = document.querySelectorAll('.modal-close, [data-modal-close]');
    
    // Open modal
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const target = trigger.getAttribute('data-modal-target');
            const modal = document.querySelector(target);
            if (modal) openModal(modal);
        });
    });
    
    // Close modal
    modalCloses.forEach(close => {
        close.addEventListener('click', (e) => {
            e.preventDefault();
            const modal = close.closest('.modal');
            if (modal) closeModal(modal);
        });
    });
    
    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                const modal = overlay.querySelector('.modal');
                if (modal) closeModal(modal);
            }
        });
    });
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && activeModal) {
            closeModal(activeModal);
        }
    });
}

function openModal(modal) {
    const overlay = modal.closest('.modal-overlay') || modal.parentElement;
    
    if (activeModal) {
        closeModal(activeModal);
    }
    
    activeModal = modal;
    overlay.classList.add('show');
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Focus first focusable element
    const focusable = modal.querySelector('[autofocus], input, select, textarea, button');
    if (focusable) focusable.focus();
}

function closeModal(modal) {
    const overlay = modal.closest('.modal-overlay') || modal.parentElement;
    
    overlay.classList.remove('show');
    modal.classList.remove('show');
    document.body.style.overflow = '';
    
    if (activeModal === modal) {
        activeModal = null;
    }
}

// ============================================
// Toast Notifications
// ============================================
function initToasts() {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    // Auto-hide toasts
    setInterval(() => {
        const toasts = toastContainer.querySelectorAll('.toast');
        toasts.forEach(toast => {
            if (toast.classList.contains('show')) {
                const duration = parseInt(toast.getAttribute('data-duration')) || 5000;
                setTimeout(() => {
                    hideToast(toast);
                }, duration);
            }
        });
    }, 1000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('data-duration', duration);
    
    const icons = {
        success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 2 2h16.76a2 2 0 0 0 2-2L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn?.addEventListener('click', () => hideToast(toast));
    
    // Auto-hide
    setTimeout(() => {
        hideToast(toast);
    }, duration);
    
    return toast;
}

function hideToast(toast) {
    toast.classList.remove('show');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

// ============================================
// Tabs
// ============================================
function initTabs() {
    const tabs = document.querySelectorAll('.tabs');
    tabs.forEach(tabContainer => {
        const tabItems = tabContainer.querySelectorAll('.tab-item');
        const tabContents = document.querySelectorAll(`[data-tab-group="${tabContainer.getAttribute('data-tab-group') || ''}"] .tab-content`);
        
        tabItems.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.getAttribute('data-tab-target');
                
                // Remove active from all
                tabItems.forEach(item => item.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active to clicked
                tab.classList.add('active');
                
                // Add active to target content
                const targetContent = document.querySelector(target);
                targetContent?.classList.add('active');
            });
        });
    });
}

// ============================================
// Accordion
// ============================================
function initAccordion() {
    const accordions = document.querySelectorAll('.accordion');
    accordions.forEach(accordion => {
        const items = accordion.querySelectorAll('.accordion-item');
        
        items.forEach(item => {
            const header = item.querySelector('.accordion-header');
            header?.addEventListener('click', () => {
                const isOpen = item.classList.contains('open');
                
                // Close all items if not allowing multiple
                if (!accordion.classList.contains('allow-multiple')) {
                    items.forEach(otherItem => {
                        if (otherItem !== item) {
                            otherItem.classList.remove('open');
                        }
                    });
                }
                
                // Toggle current item
                item.classList.toggle('open');
            });
        });
    });
}

// ============================================
// Quantity Input
// ============================================
function initQuantityInput() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(inputGroup => {
        const input = inputGroup.querySelector('.quantity-input-value');
        const minusBtn = inputGroup.querySelector('.quantity-input-btn.minus');
        const plusBtn = inputGroup.querySelector('.quantity-input-btn.plus');
        
        if (!input || !minusBtn || !plusBtn) return;
        
        const min = parseInt(input.getAttribute('min')) || 1;
        const max = parseInt(input.getAttribute('max')) || Infinity;
        
        minusBtn.addEventListener('click', () => {
            let value = parseInt(input.value) || min;
            value = Math.max(min, value - 1);
            input.value = value;
            updateQuantityButtonState(input, minusBtn, plusBtn, min, max);
            input.dispatchEvent(new Event('change'));
        });
        
        plusBtn.addEventListener('click', () => {
            let value = parseInt(input.value) || min;
            value = Math.min(max, value + 1);
            input.value = value;
            updateQuantityButtonState(input, minusBtn, plusBtn, min, max);
            input.dispatchEvent(new Event('change'));
        });
        
        input.addEventListener('change', () => {
            updateQuantityButtonState(input, minusBtn, plusBtn, min, max);
        });
        
        input.addEventListener('blur', () => {
            let value = parseInt(input.value) || min;
            value = Math.min(Math.max(min, value), max);
            input.value = value;
            updateQuantityButtonState(input, minusBtn, plusBtn, min, max);
        });
        
        // Initialize button state
        updateQuantityButtonState(input, minusBtn, plusBtn, min, max);
    });
}

function updateQuantityButtonState(input, minusBtn, plusBtn, min, max) {
    const value = parseInt(input.value) || min;
    
    minusBtn.disabled = value <= min;
    plusBtn.disabled = value >= max;
}

// ============================================
// Star Rating
// ============================================
function initStarRating() {
    const ratings = document.querySelectorAll('.rating');
    ratings.forEach(rating => {
        const stars = rating.querySelectorAll('.rating-star');
        const input = rating.querySelector('input[type="hidden"]');
        
        if (stars.length === 0) return;
        
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                if (rating.classList.contains('readonly')) return;
                
                const value = index + 1;
                
                // Update stars
                stars.forEach((s, i) => {
                    s.classList.toggle('empty', i >= value);
                });
                
                // Update input
                if (input) {
                    input.value = value;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            star.addEventListener('mouseenter', () => {
                if (rating.classList.contains('readonly')) return;
                
                stars.forEach((s, i) => {
                    s.classList.toggle('hover', i <= index);
                });
            });
            
            star.addEventListener('mouseleave', () => {
                if (rating.classList.contains('readonly')) return;
                
                stars.forEach(s => s.classList.remove('hover'));
            });
        });
    });
}

// ============================================
// File Input
// ============================================
function initFileInput() {
    const fileInputs = document.querySelectorAll('.file-input-label');
    fileInputs.forEach(label => {
        const input = label.previousElementSibling;
        const preview = label.parentElement.querySelector('.file-input-preview');
        const removeBtn = label.parentElement.querySelector('.file-input-remove');
        const helpText = label.parentElement.querySelector('.file-input-help');
        
        if (!input || input.type !== 'file') return;
        
        label.addEventListener('click', (e) => {
            e.preventDefault();
            input.click();
        });
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                updateFilePreview(file, preview, helpText);
            }
        });
        
        removeBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            input.value = '';
            if (preview) {
                preview.innerHTML = '';
                preview.style.display = 'none';
            }
            if (helpText) {
                helpText.style.display = 'block';
            }
        });
        
        // Initialize
        if (input.value && preview) {
            const file = input.files[0];
            if (file) {
                updateFilePreview(file, preview, helpText);
            }
        }
    });
}

function updateFilePreview(file, preview, helpText) {
    if (!preview) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        if (file.type.startsWith('image/')) {
            preview.innerHTML = `<img src="${e.target.result}" alt="${file.name}">`;
            preview.style.display = 'flex';
        } else {
            preview.innerHTML = `<span class="file-input-filename">${file.name}</span>`;
            preview.style.display = 'flex';
        }
    };
    reader.readAsDataURL(file);
    
    if (helpText) {
        helpText.style.display = 'none';
    }
}

// ============================================
// Password Strength
// ============================================
function initPasswordStrength() {
    const passwordInputs = document.querySelectorAll('.password-strength-input');
    passwordInputs.forEach(input => {
        const bar = input.parentElement.querySelector('.password-strength-bar');
        const text = input.parentElement.querySelector('.password-strength-text');
        
        if (!bar || !text) return;
        
        input.addEventListener('input', () => {
            const strength = checkPasswordStrength(input.value);
            updatePasswordStrength(bar, text, strength);
        });
    });
}

function checkPasswordStrength(password) {
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength += 1;
    if (password.length >= 12) strength += 1;
    
    // Character variety
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 1;
    if (/\d/.test(password)) strength += 1;
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
    
    return Math.min(strength, 3);
}

function updatePasswordStrength(bar, text, strength) {
    const levels = ['weak', 'medium', 'strong'];
    const level = levels[strength - 1] || 'weak';
    
    bar.className = `password-strength-bar ${level}`;
    text.className = `password-strength-text ${level}`;
    
    const messages = {
        weak: 'Weak',
        medium: 'Medium',
        strong: 'Strong'
    };
    
    text.textContent = messages[level] || '';
}

// ============================================
// Form Validation
// ============================================
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }, false);
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// ============================================
// Lazy Loading
// ============================================
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// ============================================
// Scroll to Top
// ============================================
function initScrollToTop() {
    const scrollToTopBtn = document.querySelector('.scroll-to-top');
    if (!scrollToTopBtn) return;
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.classList.add('show');
        } else {
            scrollToTopBtn.classList.remove('show');
        }
    });
    
    scrollToTopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ============================================
// Tooltip
// ============================================
function initTooltip() {
    const tooltips = document.querySelectorAll('.tooltip-container');
    tooltips.forEach(tooltip => {
        const tooltipText = tooltip.querySelector('.tooltip-text');
        if (!tooltipText) return;
        
        tooltip.addEventListener('mouseenter', () => {
            const rect = tooltip.getBoundingClientRect();
            tooltipText.style.left = `${rect.width / 2}px`;
        });
    });
}

// ============================================
// Copy to Clipboard
// ============================================
function initCopyToClipboard() {
    const copyBtns = document.querySelectorAll('.copy-to-clipboard');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const text = btn.getAttribute('data-text') || '';
            const target = btn.getAttribute('data-target');
            
            let content = text;
            if (target) {
                const element = document.querySelector(target);
                if (element) {
                    content = element.value || element.textContent || '';
                }
            }
            
            try {
                await navigator.clipboard.writeText(content);
                btn.classList.add('copied');
                btn.querySelector('svg')?.setAttribute('data-copied', 'true');
                
                setTimeout(() => {
                    btn.classList.remove('copied');
                    btn.querySelector('svg')?.removeAttribute('data-copied');
                }, 2000);
            } catch (err) {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = content;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.classList.remove('copied');
                }, 2000);
            }
        });
    });
}

// ============================================
// Notification Badge
// ============================================
function initNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    if (!badge) return;
    
    // Example: Update badge count
    // In a real app, this would be connected to your notification system
    // updateNotificationBadge(5);
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (!badge) return;
    
    badge.textContent = count > 99 ? '99+' : count;
    badge.style.display = count > 0 ? 'flex' : 'none';
}

// ============================================
// Cart Sidebar
// ============================================
function initCartSidebar() {
    const cartToggle = document.querySelector('.cart-toggle');
    const cartSidebar = document.querySelector('.cart-sidebar');
    const cartClose = document.querySelector('.cart-sidebar-close');
    const cartOverlay = document.querySelector('.cart-sidebar-overlay');
    
    if (!cartToggle || !cartSidebar) return;
    
    cartToggle.addEventListener('click', () => {
        cartSidebar.classList.add('open');
        cartOverlay?.classList.add('show');
        document.body.style.overflow = 'hidden';
    });
    
    cartClose?.addEventListener('click', closeCartSidebar);
    cartOverlay?.addEventListener('click', closeCartSidebar);
}

function closeCartSidebar() {
    const cartSidebar = document.querySelector('.cart-sidebar');
    const cartOverlay = document.querySelector('.cart-sidebar-overlay');
    
    cartSidebar?.classList.remove('open');
    cartOverlay?.classList.remove('show');
    document.body.style.overflow = '';
}

// ============================================
// Wishlist Sidebar
// ============================================
function initWishlistSidebar() {
    const wishlistToggle = document.querySelector('.wishlist-toggle');
    const wishlistSidebar = document.querySelector('.wishlist-sidebar');
    const wishlistClose = document.querySelector('.wishlist-sidebar-close');
    const wishlistOverlay = document.querySelector('.wishlist-sidebar-overlay');
    
    if (!wishlistToggle || !wishlistSidebar) return;
    
    wishlistToggle.addEventListener('click', () => {
        wishlistSidebar.classList.add('open');
        wishlistOverlay?.classList.add('show');
        document.body.style.overflow = 'hidden';
    });
    
    wishlistClose?.addEventListener('click', closeWishlistSidebar);
    wishlistOverlay?.addEventListener('click', closeWishlistSidebar);
}

function closeWishlistSidebar() {
    const wishlistSidebar = document.querySelector('.wishlist-sidebar');
    const wishlistOverlay = document.querySelector('.wishlist-sidebar-overlay');
    
    wishlistSidebar?.classList.remove('open');
    wishlistOverlay?.classList.remove('show');
    document.body.style.overflow = '';
}

// ============================================
// Compare Sidebar
// ============================================
function initCompareSidebar() {
    const compareToggle = document.querySelector('.compare-toggle');
    const compareSidebar = document.querySelector('.compare-sidebar');
    const compareClose = document.querySelector('.compare-sidebar-close');
    const compareOverlay = document.querySelector('.compare-sidebar-overlay');
    
    if (!compareToggle || !compareSidebar) return;
    
    compareToggle.addEventListener('click', () => {
        compareSidebar.classList.add('open');
        compareOverlay?.classList.add('show');
        document.body.style.overflow = 'hidden';
    });
    
    compareClose?.addEventListener('click', closeCompareSidebar);
    compareOverlay?.addEventListener('click', closeCompareSidebar);
}

function closeCompareSidebar() {
    const compareSidebar = document.querySelector('.compare-sidebar');
    const compareOverlay = document.querySelector('.compare-sidebar-overlay');
    
    compareSidebar?.classList.remove('open');
    compareOverlay?.classList.remove('show');
    document.body.style.overflow = '';
}

// ============================================
// Search
// ============================================
function initSearch() {
    const searchToggle = document.querySelector('.search-toggle');
    const searchForm = document.querySelector('.search-form');
    const searchClose = document.querySelector('.search-close');
    const searchOverlay = document.querySelector('.search-overlay');
    
    if (!searchToggle || !searchForm) return;
    
    searchToggle.addEventListener('click', () => {
        searchForm.classList.add('open');
        searchOverlay?.classList.add('show');
        const input = searchForm.querySelector('input');
        if (input) input.focus();
    });
    
    searchClose?.addEventListener('click', closeSearch);
    searchOverlay?.addEventListener('click', closeSearch);
    
    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchForm.classList.contains('open')) {
            closeSearch();
        }
    });
}

function closeSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchOverlay = document.querySelector('.search-overlay');
    
    searchForm?.classList.remove('open');
    searchOverlay?.classList.remove('show');
}

// ============================================
// Product Tabs
// ============================================
function initProductTabs() {
    const productTabs = document.querySelectorAll('.product-tabs');
    productTabs.forEach(tabs => {
        const tabItems = tabs.querySelectorAll('.product-tab-item');
        const tabContents = tabs.parentElement.querySelectorAll('.product-tab-content');
        
        tabItems.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.getAttribute('data-tab-target');
                
                // Remove active from all
                tabItems.forEach(item => item.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active to clicked
                tab.classList.add('active');
                
                // Add active to target content
                const targetContent = tabs.parentElement.querySelector(target);
                targetContent?.classList.add('active');
            });
        });
    });
}

// ============================================
// Product Gallery
// ============================================
function initProductGallery() {
    const galleries = document.querySelectorAll('.product-gallery');
    galleries.forEach(gallery => {
        const thumbnails = gallery.querySelectorAll('.product-gallery-thumbnail');
        const mainImage = gallery.querySelector('.product-gallery-main img');
        
        if (!mainImage) return;
        
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', () => {
                const src = thumbnail.querySelector('img').src;
                mainImage.src = src;
                
                // Remove active from all thumbnails
                thumbnails.forEach(t => t.classList.remove('active'));
                
                // Add active to clicked thumbnail
                thumbnail.classList.add('active');
            });
        });
        
        // Initialize first thumbnail as active
        if (thumbnails.length > 0) {
            thumbnails[0].classList.add('active');
        }
    });
}

// ============================================
// Checkout Steps
// ============================================
function initCheckoutSteps() {
    const checkoutSteps = document.querySelector('.checkout-steps');
    if (!checkoutSteps) return;
    
    const steps = checkoutSteps.querySelectorAll('.checkout-step');
    const currentStep = parseInt(checkoutSteps.getAttribute('data-current-step')) || 0;
    
    steps.forEach((step, index) => {
        step.classList.remove('active', 'completed');
        
        if (index < currentStep) {
            step.classList.add('completed');
        } else if (index === currentStep) {
            step.classList.add('active');
        }
    });
}

// ============================================
// RTL Support
// ============================================
function initRTLSupport() {
    const html = document.documentElement;
    const direction = html.getAttribute('dir') || 'ltr';
    
    // Apply direction class
    html.classList.add(direction);
    
    // Update dropdown positioning for RTL
    if (direction === 'rtl') {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.right = '0';
            menu.style.left = 'auto';
        });
    }
}

// ============================================
// Utility Functions
// ============================================

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format price
function formatPrice(price, currency = '$') {
    return `${currency}${formatNumber(price)}`;
}

// Generate unique ID
function generateId(prefix = 'id') {
    return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
}

// Check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Scroll to element
function scrollToElement(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

// ============================================
// Export for use in other modules
// ============================================
window.ShopTemplate = {
    ...ShopTemplate,
    // Theme functions
    toggleTheme,
    setThemeColor,
    applyTheme,
    applyThemeColor,
    
    // Toast
    showToast,
    hideToast,
    
    // Modal
    openModal,
    closeModal,
    
    // Utility functions
    formatNumber,
    formatPrice,
    generateId,
    isInViewport,
    scrollToElement,
    debounce,
    throttle
};
