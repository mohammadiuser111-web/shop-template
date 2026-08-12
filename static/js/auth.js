/**
 * Shop Template - Authentication JavaScript
 * =======================================
 * Authentication-specific JavaScript functionality
 */

// ============================================
// Authentication Manager
// ============================================
class AuthManager {
    constructor() {
        this.token = null;
        this.user = null;
        this.storageKey = 'shop-template-auth';
        this.init();
    }
    
    init() {
        this.loadAuthState();
        this.initAuthForms();
        this.initSocialLogin();
        this.initPasswordToggle();
        this.initRememberMe();
    }
    
    loadAuthState() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                const authState = JSON.parse(saved);
                this.token = authState.token;
                this.user = authState.user;
                this.updateAuthUI();
            } catch (e) {
                this.clearAuth();
            }
        }
    }
    
    saveAuthState(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem(this.storageKey, JSON.stringify({ token, user }));
        this.updateAuthUI();
    }
    
    clearAuth() {
        this.token = null;
        this.user = null;
        localStorage.removeItem(this.storageKey);
        this.updateAuthUI();
    }
    
    isAuthenticated() {
        return !!this.token;
    }
    
    getUser() {
        return this.user;
    }
    
    getToken() {
        return this.token;
    }
    
    updateAuthUI() {
        const authLinks = document.querySelectorAll('[data-auth-link]');
        const guestLinks = document.querySelectorAll('[data-guest-link]');
        const userMenu = document.querySelector('.user-menu');
        
        authLinks.forEach(link => {
            link.style.display = this.isAuthenticated() ? 'block' : 'none';
        });
        
        guestLinks.forEach(link => {
            link.style.display = !this.isAuthenticated() ? 'block' : 'none';
        });
        
        if (userMenu) {
            if (this.isAuthenticated()) {
                userMenu.innerHTML = `
                    <div class="user-menu-avatar">
                        ${this.user?.avatar ? `<img src="${this.user.avatar}" alt="${this.user.name}">` : `<span>${this.user?.name?.charAt(0) || 'U'}</span>`}
                    </div>
                    <div class="user-menu-info">
                        <div class="user-menu-name">${this.user?.name || 'User'}</div>
                        <div class="user-menu-email">${this.user?.email || ''}</div>
                    </div>
                `;
                userMenu.style.display = 'flex';
            } else {
                userMenu.style.display = 'none';
            }
        }
    }
    
    initAuthForms() {
        // Login form
        const loginForm = document.querySelector('.auth-form.login');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin(loginForm);
            });
        }
        
        // Register form
        const registerForm = document.querySelector('.auth-form.register');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRegister(registerForm);
            });
        }
        
        // Forgot password form
        const forgotForm = document.querySelector('.auth-form.forgot-password');
        if (forgotForm) {
            forgotForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleForgotPassword(forgotForm);
            });
        }
        
        // Reset password form
        const resetForm = document.querySelector('.auth-form.reset-password');
        if (resetForm) {
            resetForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleResetPassword(resetForm);
            });
        }
    }
    
    handleLogin(form) {
        const email = form.querySelector('input[name="email"]').value;
        const password = form.querySelector('input[name="password"]').value;
        const rememberMe = form.querySelector('input[name="remember"]')?.checked || false;
        
        if (!email || !password) {
            ShopTemplate.showToast('Please fill in all fields', 'error');
            return;
        }
        
        // In a real app, this would make an API call
        // For demo purposes, we'll simulate a successful login
        this.simulateLogin(email, password, rememberMe);
    }
    
    handleRegister(form) {
        const name = form.querySelector('input[name="name"]').value;
        const email = form.querySelector('input[name="email"]').value;
        const password = form.querySelector('input[name="password"]').value;
        const confirmPassword = form.querySelector('input[name="confirm_password"]').value;
        const terms = form.querySelector('input[name="terms"]')?.checked || false;
        
        if (!name || !email || !password || !confirmPassword) {
            ShopTemplate.showToast('Please fill in all fields', 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            ShopTemplate.showToast('Passwords do not match', 'error');
            return;
        }
        
        if (!terms) {
            ShopTemplate.showToast('Please accept the terms and conditions', 'error');
            return;
        }
        
        // In a real app, this would make an API call
        // For demo purposes, we'll simulate a successful registration
        this.simulateRegister(name, email, password);
    }
    
    handleForgotPassword(form) {
        const email = form.querySelector('input[name="email"]').value;
        
        if (!email) {
            ShopTemplate.showToast('Please enter your email address', 'error');
            return;
        }
        
        // In a real app, this would make an API call
        // For demo purposes, we'll simulate a successful request
        this.simulateForgotPassword(email);
    }
    
    handleResetPassword(form) {
        const password = form.querySelector('input[name="password"]').value;
        const confirmPassword = form.querySelector('input[name="confirm_password"]').value;
        const token = new URLSearchParams(window.location.search).get('token');
        
        if (!password || !confirmPassword) {
            ShopTemplate.showToast('Please fill in all fields', 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            ShopTemplate.showToast('Passwords do not match', 'error');
            return;
        }
        
        if (!token) {
            ShopTemplate.showToast('Invalid reset token', 'error');
            return;
        }
        
        // In a real app, this would make an API call
        // For demo purposes, we'll simulate a successful password reset
        this.simulateResetPassword(password, token);
    }
    
    simulateLogin(email, password, rememberMe) {
        // Simulate API call delay
        setTimeout(() => {
            const user = {
                id: 1,
                name: 'John Doe',
                email: email,
                avatar: '/static/images/avatars/avatar-1.jpg',
                role: 'customer'
            };
            
            const token = 'simulated-jwt-token-' + Date.now();
            
            if (rememberMe) {
                localStorage.setItem(this.storageKey, JSON.stringify({ token, user }));
            } else {
                sessionStorage.setItem(this.storageKey, JSON.stringify({ token, user }));
            }
            
            this.saveAuthState(token, user);
            
            // Redirect to dashboard or home
            const redirectUrl = form.querySelector('input[name="next"]')?.value || '/account/';
            window.location.href = redirectUrl;
            
            ShopTemplate.showToast('Login successful!', 'success');
        }, 1000);
    }
    
    simulateRegister(name, email, password) {
        // Simulate API call delay
        setTimeout(() => {
            const user = {
                id: 1,
                name: name,
                email: email,
                avatar: null,
                role: 'customer'
            };
            
            const token = 'simulated-jwt-token-' + Date.now();
            
            this.saveAuthState(token, user);
            
            // Redirect to account page
            window.location.href = '/account/';
            
            ShopTemplate.showToast('Registration successful!', 'success');
        }, 1000);
    }
    
    simulateForgotPassword(email) {
        // Simulate API call delay
        setTimeout(() => {
            // In a real app, you would show a success message
            // and possibly redirect to a confirmation page
            const forgotSuccess = document.querySelector('.forgot-password-success');
            if (forgotSuccess) {
                forgotSuccess.style.display = 'block';
                document.querySelector('.forgot-password-form').style.display = 'none';
            } else {
                ShopTemplate.showToast('Password reset link sent to your email', 'success');
            }
        }, 1000);
    }
    
    simulateResetPassword(password, token) {
        // Simulate API call delay
        setTimeout(() => {
            const resetSuccess = document.querySelector('.reset-password-success');
            if (resetSuccess) {
                resetSuccess.style.display = 'block';
                document.querySelector('.reset-password-form').style.display = 'none';
            } else {
                ShopTemplate.showToast('Password reset successful!', 'success');
                window.location.href = '/account/login/';
            }
        }, 1000);
    }
    
    initSocialLogin() {
        const socialButtons = document.querySelectorAll('.btn-social');
        socialButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const provider = btn.dataset.provider;
                this.handleSocialLogin(provider);
            });
        });
    }
    
    handleSocialLogin(provider) {
        // In a real app, this would redirect to the OAuth provider
        // For demo purposes, we'll show a message
        ShopTemplate.showToast(`Connecting with ${provider.toUpperCase()}...`, 'info');
        
        // Simulate social login
        setTimeout(() => {
            const user = {
                id: 1,
                name: `${provider.charAt(0).toUpperCase()}${provider.slice(1)} User`,
                email: `${provider}@example.com`,
                avatar: `/static/images/avatars/avatar-${Math.floor(Math.random() * 5) + 1}.jpg`,
                role: 'customer'
            };
            
            const token = 'simulated-jwt-token-' + Date.now();
            
            this.saveAuthState(token, user);
            window.location.href = '/account/';
            
            ShopTemplate.showToast(`Logged in with ${provider.toUpperCase()}`, 'success');
        }, 1500);
    }
    
    initPasswordToggle() {
        const passwordToggles = document.querySelectorAll('.password-toggle');
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const input = toggle.parentElement.querySelector('input');
                if (input) {
                    const type = input.type === 'password' ? 'text' : 'password';
                    input.type = type;
                    toggle.querySelector('svg').innerHTML = type === 'password' ?
                        '<path d="M17 8l4 4m0 0l-4 4m4-4H3"/><path d="M3 8l4 4m0 0l4-4"/>' :
                        '<line x1="3" y1="6" x2="21" y2="6"/><path d="M16.5 12a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0z"/><line x1="3" y1="18" x2="21" y2="18"/>';
                }
            });
        });
    }
    
    initRememberMe() {
        const rememberCheckbox = document.querySelector('input[name="remember"]');
        if (rememberCheckbox) {
            // Check if there's a saved auth state
            const saved = localStorage.getItem(this.storageKey);
            rememberCheckbox.checked = !!saved;
        }
    }
    
    logout() {
        this.clearAuth();
        window.location.href = '/account/login/';
        ShopTemplate.showToast('You have been logged out', 'info');
    }
}

// ============================================
// Password Strength Meter
// ============================================
class PasswordStrengthMeter {
    constructor(inputElement) {
        this.input = inputElement;
        this.bar = document.querySelector('.password-strength-bar');
        this.text = document.querySelector('.password-strength-text');
        this.init();
    }
    
    init() {
        this.input.addEventListener('input', () => {
            this.updateStrength();
        });
    }
    
    updateStrength() {
        const password = this.input.value;
        const strength = this.calculateStrength(password);
        this.updateUI(strength);
    }
    
    calculateStrength(password) {
        let strength = 0;
        
        // Length
        if (password.length >= 8) strength += 1;
        if (password.length >= 12) strength += 1;
        
        // Contains uppercase and lowercase
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 1;
        
        // Contains numbers
        if (/\d/.test(password)) strength += 1;
        
        // Contains special characters
        if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
        
        return Math.min(strength, 3);
    }
    
    updateUI(strength) {
        if (!this.bar || !this.text) return;
        
        const levels = ['weak', 'medium', 'strong'];
        const level = levels[strength - 1] || 'weak';
        
        this.bar.className = `password-strength-bar ${level}`;
        this.text.className = `password-strength-text ${level}`;
        
        const messages = {
            weak: 'Weak',
            medium: 'Medium',
            strong: 'Strong'
        };
        
        this.text.textContent = messages[level] || '';
    }
}

// ============================================
// Form Validation
// ============================================
class AuthFormValidator {
    constructor(form) {
        this.form = form;
        this.init();
    }
    
    init() {
        const inputs = this.form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateInput(input);
            });
        });
        
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
            }
        });
    }
    
    validateInput(input) {
        const value = input.value.trim();
        const type = input.type;
        const name = input.name;
        
        let isValid = true;
        let errorMessage = '';
        
        // Required validation
        if (input.required && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Email validation
        if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
        
        // Password validation
        if (name === 'password' && value && value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters';
        }
        
        // Confirm password validation
        if (name === 'confirm_password') {
            const password = this.form.querySelector('input[name="password"]').value;
            if (value !== password) {
                isValid = false;
                errorMessage = 'Passwords do not match';
            }
        }
        
        // Update UI
        input.classList.toggle('is-invalid', !isValid);
        
        const existingError = input.parentElement.querySelector('.form-error');
        if (existingError) existingError.remove();
        
        if (!isValid && !existingError) {
            const error = document.createElement('div');
            error.className = 'form-error';
            error.textContent = errorMessage;
            input.parentElement.appendChild(error);
        }
        
        return isValid;
    }
    
    validateForm() {
        const inputs = this.form.querySelectorAll('input');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// ============================================
// Two Factor Authentication
// ============================================
class TwoFactorAuth {
    constructor() {
        this.init();
    }
    
    init() {
        const twoFactorForm = document.querySelector('.two-factor-form');
        if (twoFactorForm) {
            this.initTwoFactorForm(twoFactorForm);
        }
        
        const setupTwoFactorForm = document.querySelector('.setup-two-factor-form');
        if (setupTwoFactorForm) {
            this.initSetupTwoFactorForm(setupTwoFactorForm);
        }
    }
    
    initTwoFactorForm(form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const code = form.querySelector('input[name="code"]').value;
            this.verifyTwoFactorCode(code);
        });
    }
    
    verifyTwoFactorCode(code) {
        // In a real app, this would make an API call
        // For demo purposes, we'll simulate verification
        setTimeout(() => {
            if (code === '123456') {
                // Success
                window.location.href = '/account/';
                ShopTemplate.showToast('Two-factor authentication successful!', 'success');
            } else {
                // Error
                ShopTemplate.showToast('Invalid verification code', 'error');
            }
        }, 1000);
    }
    
    initSetupTwoFactorForm(form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.setupTwoFactorAuth();
        });
    }
    
    setupTwoFactorAuth() {
        // In a real app, this would make an API call to enable 2FA
        // For demo purposes, we'll simulate the process
        setTimeout(() => {
            // Show QR code
            const qrCodeContainer = document.querySelector('.two-factor-qr-code');
            if (qrCodeContainer) {
                qrCodeContainer.innerHTML = `
                    <div class="qr-code-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                            <rect x="3" y="3" width="7" height="7"/>
                            <rect x="14" y="3" width="7" height="7"/>
                            <rect x="3" y="14" width="7" height="7"/>
                            <rect x="14" y="14" width="7" height="7"/>
                        </svg>
                        <div>QR Code for Authenticator App</div>
                    </div>
                `;
            }
            
            ShopTemplate.showToast('Two-factor authentication enabled! Scan the QR code with your authenticator app.', 'success');
        }, 1000);
    }
}

// ============================================
// Session Management
// ============================================
class SessionManager {
    constructor() {
        this.sessionTimeout = 30 * 60 * 1000; // 30 minutes
        this.warningTime = 5 * 60 * 1000; // 5 minutes before timeout
        this.init();
    }
    
    init() {
        this.startSessionTimer();
        this.initSessionWarning();
    }
    
    startSessionTimer() {
        // Reset timer on user activity
        const activities = ['mousemove', 'keydown', 'scroll', 'click'];
        activities.forEach(activity => {
            document.addEventListener(activity, () => {
                this.resetSessionTimer();
            });
        });
        
        // Start timeout
        this.timeoutId = setTimeout(() => {
            this.handleSessionTimeout();
        }, this.sessionTimeout);
        
        // Start warning
        this.warningId = setTimeout(() => {
            this.showSessionWarning();
        }, this.sessionTimeout - this.warningTime);
    }
    
    resetSessionTimer() {
        clearTimeout(this.timeoutId);
        clearTimeout(this.warningId);
        this.startSessionTimer();
    }
    
    showSessionWarning() {
        // Show a warning modal
        const warningModal = document.createElement('div');
        warningModal.className = 'session-warning-modal';
        warningModal.innerHTML = `
            <div class="session-warning-content">
                <div class="session-warning-message">
                    Your session will expire in 5 minutes due to inactivity.
                </div>
                <div class="session-warning-actions">
                    <button class="btn btn-outline-secondary session-continue">Continue Session</button>
                    <button class="btn btn-primary session-logout">Logout</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(warningModal);
        
        // Add event listeners
        const continueBtn = warningModal.querySelector('.session-continue');
        const logoutBtn = warningModal.querySelector('.session-logout');
        
        continueBtn?.addEventListener('click', () => {
            this.resetSessionTimer();
            warningModal.remove();
        });
        
        logoutBtn?.addEventListener('click', () => {
            if (window.authManager) {
                window.authManager.logout();
            }
            warningModal.remove();
        });
    }
    
    handleSessionTimeout() {
        if (window.authManager) {
            window.authManager.logout();
        }
    }
}

// ============================================
// Initialize Everything
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize auth manager
    window.authManager = new AuthManager();
    
    // Initialize password strength meters
    const passwordInputs = document.querySelectorAll('.password-strength-input');
    passwordInputs.forEach(input => {
        new PasswordStrengthMeter(input);
    });
    
    // Initialize form validators
    const authForms = document.querySelectorAll('.auth-form');
    authForms.forEach(form => {
        new AuthFormValidator(form);
    });
    
    // Initialize 2FA
    window.twoFactorAuth = new TwoFactorAuth();
    
    // Initialize session manager
    if (window.authManager.isAuthenticated()) {
        window.sessionManager = new SessionManager();
    }
    
    // Logout button
    const logoutBtn = document.querySelector('.btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (window.authManager) {
                window.authManager.logout();
            }
        });
    }
});

// ============================================
// Export for use in other modules
// ============================================
window.Auth = {
    AuthManager,
    PasswordStrengthMeter,
    AuthFormValidator,
    TwoFactorAuth,
    SessionManager
};
