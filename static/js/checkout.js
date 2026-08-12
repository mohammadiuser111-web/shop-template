/**
 * Shop Template - Checkout JavaScript
 * ==================================
 * Checkout process specific JavaScript functionality
 */

// ============================================
// Checkout Process
// ============================================
class Checkout {
    constructor() {
        this.steps = [
            { id: 'shipping', name: 'Shipping', completed: false },
            { id: 'payment', name: 'Payment', completed: false },
            { id: 'review', name: 'Review', completed: false },
            { id: 'confirmation', name: 'Confirmation', completed: false }
        ];
        this.currentStep = 0;
        this.formData = {
            shipping: {},
            payment: {},
            review: {}
        };
        this.init();
    }
    
    init() {
        this.loadStep();
        this.initSteps();
        this.initShippingForm();
        this.initPaymentForm();
        this.initReviewStep();
        this.initConfirmationStep();
        this.initNavigation();
    }
    
    loadStep() {
        const stepParam = new URLSearchParams(window.location.search).get('step');
        const stepIndex = this.steps.findIndex(s => s.id === stepParam);
        
        if (stepIndex >= 0) {
            this.currentStep = stepIndex;
        }
        
        this.updateStepsUI();
    }
    
    initSteps() {
        const checkoutSteps = document.querySelector('.checkout-steps');
        if (!checkoutSteps) return;
        
        checkoutSteps.setAttribute('data-current-step', this.currentStep);
        
        // Initialize step navigation
        const stepItems = checkoutSteps.querySelectorAll('.checkout-step');
        stepItems.forEach((step, index) => {
            step.addEventListener('click', () => {
                if (index <= this.currentStep) {
                    this.goToStep(index);
                }
            });
        });
    }
    
    updateStepsUI() {
        const checkoutSteps = document.querySelector('.checkout-steps');
        if (!checkoutSteps) return;
        
        checkoutSteps.setAttribute('data-current-step', this.currentStep);
        
        const stepItems = checkoutSteps.querySelectorAll('.checkout-step');
        stepItems.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            
            if (index < this.currentStep) {
                step.classList.add('completed');
            } else if (index === this.currentStep) {
                step.classList.add('active');
            }
        });
    }
    
    goToStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) return;
        
        // Validate current step before proceeding
        if (stepIndex > this.currentStep && !this.validateCurrentStep()) {
            return;
        }
        
        this.currentStep = stepIndex;
        this.updateStepsUI();
        this.updateStepContent();
        
        // Update URL
        const url = new URL(window.location);
        url.searchParams.set('step', this.steps[stepIndex].id);
        window.history.pushState({}, '', url);
    }
    
    updateStepContent() {
        const stepContents = document.querySelectorAll('.checkout-step-content');
        stepContents.forEach((content, index) => {
            content.style.display = index === this.currentStep ? 'block' : 'none';
        });
    }
    
    validateCurrentStep() {
        switch (this.currentStep) {
            case 0: // Shipping
                return this.validateShippingForm();
            case 1: // Payment
                return this.validatePaymentForm();
            case 2: // Review
                return true; // Review step is always valid
            default:
                return true;
        }
    }
    
    // ============================================
    // Shipping Form
    // ============================================
    initShippingForm() {
        const shippingForm = document.querySelector('.shipping-form');
        if (!shippingForm) return;
        
        // Load saved data
        this.loadFormData('shipping', shippingForm);
        
        // Form validation
        shippingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (this.validateShippingForm()) {
                this.saveFormData('shipping', shippingForm);
                this.goToStep(1);
            }
        });
        
        // Country change updates states
        const countrySelect = shippingForm.querySelector('select[name="country"]');
        const stateSelect = shippingForm.querySelector('select[name="state"]');
        
        if (countrySelect && stateSelect) {
            countrySelect.addEventListener('change', () => {
                this.updateStates(countrySelect.value, stateSelect);
            });
        }
        
        // Shipping method selection
        const shippingMethods = shippingForm.querySelectorAll('.shipping-method-option');
        shippingMethods.forEach(method => {
            method.addEventListener('click', () => {
                shippingMethods.forEach(m => m.classList.remove('selected'));
                method.classList.add('selected');
                const input = method.querySelector('input[type="radio"]');
                if (input) input.checked = true;
            });
        });
    }
    
    validateShippingForm() {
        const shippingForm = document.querySelector('.shipping-form');
        if (!shippingForm) return false;
        
        let isValid = true;
        const requiredFields = shippingForm.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        // Validate shipping method selected
        const shippingMethodSelected = shippingForm.querySelector('.shipping-method-option.selected');
        if (!shippingMethodSelected) {
            ShopTemplate.showToast('Please select a shipping method', 'error');
            isValid = false;
        }
        
        if (!isValid) {
            ShopTemplate.showToast('Please fill in all required fields', 'error');
        }
        
        return isValid;
    }
    
    updateStates(country, stateSelect) {
        // In a real app, this would fetch states based on the selected country
        // For demo purposes, we'll use placeholder data
        const states = {
            'US': ['California', 'Texas', 'New York', 'Florida', 'Illinois'],
            'CA': ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Manitoba'],
            'UK': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
            'AU': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia'],
            'DE': ['Bavaria', 'Berlin', 'Brandenburg', 'Hamburg', 'Hesse']
        };
        
        stateSelect.innerHTML = '';
        
        if (country && states[country]) {
            states[country].forEach(state => {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                stateSelect.appendChild(option);
            });
            stateSelect.disabled = false;
        } else {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Select state/province';
            stateSelect.appendChild(option);
            stateSelect.disabled = true;
        }
    }
    
    // ============================================
    // Payment Form
    // ============================================
    initPaymentForm() {
        const paymentForm = document.querySelector('.payment-form');
        if (!paymentForm) return;
        
        // Load saved data
        this.loadFormData('payment', paymentForm);
        
        // Form validation
        paymentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (this.validatePaymentForm()) {
                this.saveFormData('payment', paymentForm);
                this.updateReviewStep();
                this.goToStep(2);
            }
        });
        
        // Payment method selection
        const paymentMethods = paymentForm.querySelectorAll('.payment-method-option');
        paymentMethods.forEach(method => {
            method.addEventListener('click', () => {
                paymentMethods.forEach(m => m.classList.remove('selected'));
                method.classList.add('selected');
                const input = method.querySelector('input[type="radio"]');
                if (input) input.checked = true;
                
                // Show/hide payment details based on method
                this.togglePaymentDetails(method.dataset.method);
            });
        });
        
        // Gift card toggle
        const giftCardToggle = paymentForm.querySelector('.gift-card-toggle');
        const giftCardContainer = paymentForm.querySelector('.gift-card-container');
        
        if (giftCardToggle && giftCardContainer) {
            giftCardToggle.addEventListener('click', () => {
                giftCardContainer.classList.toggle('open');
            });
        }
        
        // Gift card form
        const giftCardForm = paymentForm.querySelector('.gift-card-form');
        if (giftCardForm) {
            giftCardForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const code = giftCardForm.querySelector('input').value;
                if (code) {
                    // In a real app, this would validate the gift card
                    const result = giftCardForm.querySelector('.gift-card-result');
                    result.textContent = `Gift card "${code}" applied successfully`;
                    result.className = 'gift-card-result success';
                    giftCardForm.reset();
                }
            });
        }
    }
    
    validatePaymentForm() {
        const paymentForm = document.querySelector('.payment-form');
        if (!paymentForm) return false;
        
        let isValid = true;
        
        // Validate payment method selected
        const paymentMethodSelected = paymentForm.querySelector('.payment-method-option.selected');
        if (!paymentMethodSelected) {
            ShopTemplate.showToast('Please select a payment method', 'error');
            isValid = false;
        }
        
        // Validate credit card if selected
        const creditCardMethod = paymentForm.querySelector('.payment-method-option[data-method="credit-card"]');
        if (creditCardMethod?.classList.contains('selected')) {
            const cardNumber = paymentForm.querySelector('input[name="card_number"]');
            const cardName = paymentForm.querySelector('input[name="card_name"]');
            const cardExpiry = paymentForm.querySelector('input[name="card_expiry"]');
            const cardCvv = paymentForm.querySelector('input[name="card_cvv"]');
            
            if (!cardNumber?.value.trim() || !cardName?.value.trim() || 
                !cardExpiry?.value.trim() || !cardCvv?.value.trim()) {
                ShopTemplate.showToast('Please fill in all credit card details', 'error');
                isValid = false;
            }
        }
        
        if (!isValid) {
            ShopTemplate.showToast('Please fill in all required fields', 'error');
        }
        
        return isValid;
    }
    
    togglePaymentDetails(method) {
        const paymentForm = document.querySelector('.payment-form');
        if (!paymentForm) return;
        
        // Hide all payment details
        const allDetails = paymentForm.querySelectorAll('.payment-method-details');
        allDetails.forEach(detail => {
            detail.style.display = 'none';
        });
        
        // Show selected method details
        const selectedDetails = paymentForm.querySelector(`.payment-method-details[data-method="${method}"]`);
        if (selectedDetails) {
            selectedDetails.style.display = 'block';
        }
    }
    
    // ============================================
    // Review Step
    // ============================================
    initReviewStep() {
        this.updateReviewStep();
        
        const reviewForm = document.querySelector('.review-form');
        if (!reviewForm) return;
        
        reviewForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.goToStep(3);
        });
    }
    
    updateReviewStep() {
        const reviewOrder = document.querySelector('.review-order');
        if (!reviewOrder) return;
        
        // Update shipping info
        this.updateReviewShipping();
        
        // Update payment info
        this.updateReviewPayment();
        
        // Update order summary
        this.updateReviewOrderSummary();
    }
    
    updateReviewShipping() {
        const shippingInfo = document.querySelector('.review-shipping-info');
        if (!shippingInfo) return;
        
        const shippingData = this.formData.shipping;
        
        shippingInfo.innerHTML = `
            <div class="review-order-info">
                <div class="review-order-info-item">
                    <div class="review-order-info-label">Shipping Address</div>
                    <div class="review-order-info-value">
                        ${shippingData.first_name || ''} ${shippingData.last_name || ''}<br>
                        ${shippingData.address || ''}<br>
                        ${shippingData.city || ''}, ${shippingData.state || ''} ${shippingData.postal_code || ''}<br>
                        ${shippingData.country || ''}
                    </div>
                </div>
                <div class="review-order-info-item">
                    <div class="review-order-info-label">Contact</div>
                    <div class="review-order-info-value">
                        ${shippingData.email || ''}<br>
                        ${shippingData.phone || ''}
                    </div>
                </div>
                <div class="review-order-info-item">
                    <div class="review-order-info-label">Shipping Method</div>
                    <div class="review-order-info-value">
                        ${shippingData.shipping_method || 'Standard Shipping'}
                    </div>
                </div>
            </div>
        `;
    }
    
    updateReviewPayment() {
        const paymentInfo = document.querySelector('.review-payment-info');
        if (!paymentInfo) return;
        
        const paymentData = this.formData.payment;
        const paymentMethod = document.querySelector('.payment-method-option.selected');
        
        paymentInfo.innerHTML = `
            <div class="review-order-info">
                <div class="review-order-info-item">
                    <div class="review-order-info-label">Payment Method</div>
                    <div class="review-order-info-value">
                        ${paymentMethod?.querySelector('.payment-method-name')?.textContent || 'Not selected'}
                    </div>
                </div>
                ${paymentMethod?.dataset.method === 'credit-card' ? `
                    <div class="review-order-info-item">
                        <div class="review-order-info-label">Card Details</div>
                        <div class="review-order-info-value">
                            **** **** **** ${paymentData.card_number?.slice(-4) || ''}<br>
                            ${paymentData.card_name || ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    updateReviewOrderSummary() {
        const orderSummary = document.querySelector('.review-order-summary');
        if (!orderSummary) return;
        
        // In a real app, this would be loaded from the cart
        // For demo purposes, we'll use placeholder data
        const cart = window.cart || { items: [], getSubtotal: () => 0, getTotal: () => 0 };
        
        orderSummary.innerHTML = `
            <div class="review-order-products">
                ${cart.items.map(item => `
                    <div class="review-order-product">
                        <div class="review-order-product-image">
                            ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ''}
                        </div>
                        <div class="review-order-product-info">
                            <div class="review-order-product-name">${item.name}</div>
                            ${item.variant ? `<div class="review-order-product-variant">${item.variant}</div>` : ''}
                            <div class="review-order-product-price">${ShopTemplate.formatPrice(item.salePrice || item.price)}</div>
                        </div>
                        <div class="review-order-product-quantity">x${item.quantity}</div>
                    </div>
                `).join('')}
            </div>
            <div class="review-order-totals">
                <div class="review-order-total-row">
                    <span>Subtotal</span>
                    <span>${ShopTemplate.formatPrice(cart.getSubtotal())}</span>
                </div>
                <div class="review-order-total-row">
                    <span>Shipping</span>
                    <span>Free</span>
                </div>
                <div class="review-order-total-row">
                    <span>Tax</span>
                    <span>$0.00</span>
                </div>
                <div class="review-order-total-row total">
                    <span>Total</span>
                    <span>${ShopTemplate.formatPrice(cart.getTotal())}</span>
                </div>
            </div>
        `;
    }
    
    // ============================================
    // Confirmation Step
    // ============================================
    initConfirmationStep() {
        const confirmationForm = document.querySelector('.confirmation-form');
        if (!confirmationForm) return;
        
        confirmationForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.completeOrder();
        });
    }
    
    completeOrder() {
        // In a real app, this would submit the order to the server
        // For demo purposes, we'll redirect to the success page
        window.location.href = '/checkout/success/';
    }
    
    // ============================================
    // Navigation
    // ============================================
    initNavigation() {
        const prevBtn = document.querySelector('.checkout-navigation .btn-prev');
        const nextBtn = document.querySelector('.checkout-navigation .btn-next');
        const submitBtn = document.querySelector('.checkout-navigation .btn-submit');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                this.goToStep(this.currentStep - 1);
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                this.goToStep(this.currentStep + 1);
            });
        }
        
        if (submitBtn) {
            submitBtn.addEventListener('click', () => {
                this.completeOrder();
            });
        }
    }
    
    // ============================================
    // Form Data Management
    // ============================================
    saveFormData(step, form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (value) {
                data[key] = value;
            }
        }
        
        this.formData[step] = data;
        localStorage.setItem(`checkout-${step}-data`, JSON.stringify(data));
    }
    
    loadFormData(step, form) {
        const savedData = localStorage.getItem(`checkout-${step}-data`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                this.formData[step] = data;
                
                // Populate form fields
                for (const [key, value] of Object.entries(data)) {
                    const field = form.querySelector(`[name="${key}"], [name="${key}[]"]`);
                    if (field) {
                        if (field.type === 'checkbox' || field.type === 'radio') {
                            field.checked = field.value == value;
                        } else {
                            field.value = value;
                        }
                    }
                }
                
                // Update UI based on loaded data
                this.updateFormUI(step, form);
            } catch (e) {
                console.error('Error loading form data:', e);
            }
        }
    }
    
    updateFormUI(step, form) {
        switch (step) {
            case 'shipping':
                this.updateShippingFormUI(form);
                break;
            case 'payment':
                this.updatePaymentFormUI(form);
                break;
        }
    }
    
    updateShippingFormUI(form) {
        const countrySelect = form.querySelector('select[name="country"]');
        const stateSelect = form.querySelector('select[name="state"]');
        
        if (countrySelect && stateSelect && this.formData.shipping.country) {
            this.updateStates(this.formData.shipping.country, stateSelect);
            if (this.formData.shipping.state) {
                stateSelect.value = this.formData.shipping.state;
            }
        }
        
        // Update selected shipping method
        if (this.formData.shipping.shipping_method) {
            const shippingMethods = form.querySelectorAll('.shipping-method-option');
            shippingMethods.forEach(method => {
                const input = method.querySelector('input[type="radio"]');
                if (input && input.value === this.formData.shipping.shipping_method) {
                    method.classList.add('selected');
                    input.checked = true;
                }
            });
        }
    }
    
    updatePaymentFormUI(form) {
        // Update selected payment method
        if (this.formData.payment.payment_method) {
            const paymentMethods = form.querySelectorAll('.payment-method-option');
            paymentMethods.forEach(method => {
                const input = method.querySelector('input[type="radio"]');
                if (input && input.value === this.formData.payment.payment_method) {
                    method.classList.add('selected');
                    input.checked = true;
                    this.togglePaymentDetails(input.value);
                }
            });
        }
    }
}

// ============================================
// Gift Card Management
// ============================================
class GiftCard {
    constructor() {
        this.codes = [];
        this.storageKey = 'shop-template-gift-cards';
        this.load();
    }
    
    load() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                this.codes = JSON.parse(saved);
            } catch (e) {
                this.codes = [];
            }
        }
    }
    
    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.codes));
    }
    
    addCode(code, amount) {
        this.codes.push({
            code: code.toUpperCase(),
            amount: parseFloat(amount),
            used: false,
            dateAdded: new Date().toISOString()
        });
        this.save();
        return true;
    }
    
    validateCode(code) {
        const giftCard = this.codes.find(
            gc => gc.code === code.toUpperCase() && !gc.used
        );
        
        if (giftCard) {
            giftCard.used = true;
            this.save();
            return { valid: true, amount: giftCard.amount };
        }
        
        return { valid: false, amount: 0 };
    }
    
    getBalance() {
        return this.codes.reduce((total, gc) => {
            if (!gc.used) {
                return total + gc.amount;
            }
            return total;
        }, 0);
    }
}

// ============================================
// Order Summary
// ============================================
class OrderSummary {
    constructor() {
        this.cart = window.cart || null;
        this.init();
    }
    
    init() {
        this.updateSummary();
        
        // Listen for cart changes
        if (this.cart) {
            // In a real app, you would listen for cart update events
            // For demo purposes, we'll just update on page load
        }
    }
    
    updateSummary() {
        if (!this.cart) return;
        
        const summaryElements = document.querySelectorAll('.order-summary');
        summaryElements.forEach(summary => {
            const subtotal = summary.querySelector('.order-summary-row:not(.total) .amount');
            const total = summary.querySelector('.order-summary-row.total .amount');
            
            if (subtotal) {
                subtotal.textContent = ShopTemplate.formatPrice(this.cart.getSubtotal());
            }
            
            if (total) {
                total.textContent = ShopTemplate.formatPrice(this.cart.getTotal());
            }
        });
    }
}

// ============================================
// Initialize Everything
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize checkout
    window.checkout = new Checkout();
    
    // Initialize gift card
    window.giftCard = new GiftCard();
    
    // Initialize order summary
    window.orderSummary = new OrderSummary();
    
    // Apply gift card from URL if present
    const urlParams = new URLSearchParams(window.location.search);
    const giftCardCode = urlParams.get('gift_card');
    if (giftCardCode) {
        const result = window.giftCard.validateCode(giftCardCode);
        if (result.valid) {
            ShopTemplate.showToast(`Gift card applied: ${ShopTemplate.formatPrice(result.amount)}`, 'success');
        } else {
            ShopTemplate.showToast('Invalid gift card code', 'error');
        }
    }
});

// ============================================
// Export for use in other modules
// ============================================
window.CheckoutProcess = {
    Checkout,
    GiftCard,
    OrderSummary
};
