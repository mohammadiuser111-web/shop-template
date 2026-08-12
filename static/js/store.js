/**
 * Shop Template - Store JavaScript
 * ================================
 * Store-specific JavaScript functionality
 */

// ============================================
// Cart Management
// ============================================
class Cart {
    constructor() {
        this.items = [];
        this.storageKey = 'shop-template-cart';
        this.load();
    }
    
    load() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                this.items = JSON.parse(saved);
            } catch (e) {
                this.items = [];
            }
        }
        this.updateUI();
        this.updateBadge();
    }
    
    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
        this.updateUI();
        this.updateBadge();
    }
    
    addItem(product, quantity = 1) {
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                salePrice: product.salePrice || null,
                image: product.image || null,
                quantity: quantity,
                variant: product.variant || null,
                maxQuantity: product.stock || Infinity
            });
        }
        
        this.save();
        ShopTemplate.showToast(`${product.name} added to cart`, 'success');
    }
    
    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.save();
        ShopTemplate.showToast('Item removed from cart', 'info');
    }
    
    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            item.quantity = Math.max(1, Math.min(quantity, item.maxQuantity));
            this.save();
        }
    }
    
    clear() {
        this.items = [];
        this.save();
        ShopTemplate.showToast('Cart cleared', 'info');
    }
    
    getItemCount() {
        return this.items.reduce((total, item) => total + item.quantity, 0);
    }
    
    getSubtotal() {
        return this.items.reduce((total, item) => {
            const price = item.salePrice || item.price;
            return total + (price * item.quantity);
        }, 0);
    }
    
    getTotal() {
        // In a real app, this would include shipping, tax, etc.
        return this.getSubtotal();
    }
    
    getItem(productId) {
        return this.items.find(item => item.id === productId);
    }
    
    hasItem(productId) {
        return this.items.some(item => item.id === productId);
    }
    
    updateUI() {
        // Update cart sidebar
        this.updateCartSidebar();
        
        // Update cart dropdown
        this.updateCartDropdown();
    }
    
    updateBadge() {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            badge.textContent = this.getItemCount();
            badge.style.display = this.getItemCount() > 0 ? 'flex' : 'none';
        }
    }
    
    updateCartSidebar() {
        const cartSidebar = document.querySelector('.cart-sidebar');
        if (!cartSidebar) return;
        
        const cartItems = cartSidebar.querySelector('.cart-sidebar-items');
        const cartSubtotal = cartSidebar.querySelector('.cart-sidebar-subtotal');
        const cartTotal = cartSidebar.querySelector('.cart-sidebar-total');
        const cartEmpty = cartSidebar.querySelector('.cart-sidebar-empty');
        
        if (!cartItems || !cartSubtotal || !cartTotal) return;
        
        if (this.items.length === 0) {
            cartItems.style.display = 'none';
            cartEmpty.style.display = 'block';
        } else {
            cartItems.style.display = 'block';
            cartEmpty.style.display = 'none';
            
            // Update items
            cartItems.innerHTML = this.items.map(item => `
                <div class="cart-sidebar-item" data-product-id="${item.id}">
                    <div class="cart-sidebar-item-image">
                        ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ''}
                    </div>
                    <div class="cart-sidebar-item-info">
                        <div class="cart-sidebar-item-name">${item.name}</div>
                        ${item.variant ? `<div class="cart-sidebar-item-variant">${item.variant}</div>` : ''}
                        <div class="cart-sidebar-item-price">
                            ${item.salePrice ? `<span class="cart-sidebar-item-sale-price">${ShopTemplate.formatPrice(item.salePrice)}</span>` : ''}
                            <span class="cart-sidebar-item-${item.salePrice ? 'original-' : ''}price">${ShopTemplate.formatPrice(item.price)}</span>
                        </div>
                    </div>
                    <div class="cart-sidebar-item-quantity">
                        <div class="quantity-input quantity-input-sm">
                            <button class="quantity-input-btn minus" type="button">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="5" y1="12" x2="19" y2="12"/>
                                </svg>
                            </button>
                            <input type="number" class="quantity-input-value" value="${item.quantity}" min="1" max="${item.maxQuantity}">
                            <button class="quantity-input-btn plus" type="button">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="12" y1="5" x2="12" y2="19"/>
                                    <line x1="5" y1="12" x2="19" y2="12"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <button class="cart-sidebar-item-remove" type="button" data-product-id="${item.id}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            `).join('');
            
            // Update subtotal and total
            cartSubtotal.querySelector('.amount').textContent = ShopTemplate.formatPrice(this.getSubtotal());
            cartTotal.querySelector('.amount').textContent = ShopTemplate.formatPrice(this.getTotal());
            
            // Initialize quantity inputs
            this.initCartQuantityInputs();
            
            // Initialize remove buttons
            this.initCartRemoveButtons();
        }
    }
    
    updateCartDropdown() {
        const cartDropdown = document.querySelector('.cart-dropdown');
        if (!cartDropdown) return;
        
        const cartItems = cartDropdown.querySelector('.cart-dropdown-items');
        const cartSubtotal = cartDropdown.querySelector('.cart-dropdown-subtotal');
        const cartEmpty = cartDropdown.querySelector('.cart-dropdown-empty');
        
        if (!cartItems || !cartSubtotal) return;
        
        if (this.items.length === 0) {
            cartItems.style.display = 'none';
            cartEmpty.style.display = 'block';
        } else {
            cartItems.style.display = 'block';
            cartEmpty.style.display = 'none';
            
            // Update items (show only first 3)
            const displayItems = this.items.slice(0, 3);
            cartItems.innerHTML = displayItems.map(item => `
                <div class="cart-dropdown-item" data-product-id="${item.id}">
                    <div class="cart-dropdown-item-image">
                        ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ''}
                    </div>
                    <div class="cart-dropdown-item-info">
                        <div class="cart-dropdown-item-name">${item.name}</div>
                        <div class="cart-dropdown-item-price">
                            ${item.quantity} x ${ShopTemplate.formatPrice(item.salePrice || item.price)}
                        </div>
                    </div>
                </div>
            `).join('');
            
            // Show more items count
            if (this.items.length > 3) {
                const moreCount = this.items.length - 3;
                cartItems.innerHTML += `
                    <div class="cart-dropdown-more">
                        +${moreCount} more items
                    </div>
                `;
            }
            
            // Update subtotal
            cartSubtotal.querySelector('.amount').textContent = ShopTemplate.formatPrice(this.getSubtotal());
        }
    }
    
    initCartQuantityInputs() {
        const quantityInputs = document.querySelectorAll('.cart-sidebar-item .quantity-input');
        quantityInputs.forEach(inputGroup => {
            const input = inputGroup.querySelector('.quantity-input-value');
            const minusBtn = inputGroup.querySelector('.quantity-input-btn.minus');
            const plusBtn = inputGroup.querySelector('.quantity-input-btn.plus');
            const productId = inputGroup.closest('.cart-sidebar-item').dataset.productId;
            
            if (!input || !minusBtn || !plusBtn || !productId) return;
            
            const item = this.getItem(productId);
            if (!item) return;
            
            minusBtn.addEventListener('click', () => {
                const value = Math.max(1, parseInt(input.value) - 1);
                input.value = value;
                this.updateQuantity(productId, value);
            });
            
            plusBtn.addEventListener('click', () => {
                const value = Math.min(item.maxQuantity, parseInt(input.value) + 1);
                input.value = value;
                this.updateQuantity(productId, value);
            });
            
            input.addEventListener('change', () => {
                let value = parseInt(input.value) || 1;
                value = Math.min(Math.max(1, value), item.maxQuantity);
                input.value = value;
                this.updateQuantity(productId, value);
            });
        });
    }
    
    initCartRemoveButtons() {
        const removeButtons = document.querySelectorAll('.cart-sidebar-item-remove');
        removeButtons.forEach(btn => {
            const productId = btn.dataset.productId;
            if (!productId) return;
            
            btn.addEventListener('click', () => {
                this.removeItem(productId);
            });
        });
    }
}

// ============================================
// Wishlist Management
// ============================================
class Wishlist {
    constructor() {
        this.items = [];
        this.storageKey = 'shop-template-wishlist';
        this.load();
    }
    
    load() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                this.items = JSON.parse(saved);
            } catch (e) {
                this.items = [];
            }
        }
        this.updateUI();
        this.updateBadge();
    }
    
    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
        this.updateUI();
        this.updateBadge();
    }
    
    addItem(product) {
        if (!this.hasItem(product.id)) {
            this.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                salePrice: product.salePrice || null,
                image: product.image || null
            });
            this.save();
            ShopTemplate.showToast(`${product.name} added to wishlist`, 'success');
        } else {
            ShopTemplate.showToast('Product already in wishlist', 'info');
        }
    }
    
    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.save();
        ShopTemplate.showToast('Item removed from wishlist', 'info');
    }
    
    clear() {
        this.items = [];
        this.save();
        ShopTemplate.showToast('Wishlist cleared', 'info');
    }
    
    getItemCount() {
        return this.items.length;
    }
    
    getItem(productId) {
        return this.items.find(item => item.id === productId);
    }
    
    hasItem(productId) {
        return this.items.some(item => item.id === productId);
    }
    
    updateUI() {
        this.updateWishlistSidebar();
        this.updateWishlistDropdown();
    }
    
    updateBadge() {
        const badge = document.querySelector('.wishlist-badge');
        if (badge) {
            badge.textContent = this.getItemCount();
            badge.style.display = this.getItemCount() > 0 ? 'flex' : 'none';
        }
    }
    
    updateWishlistSidebar() {
        const wishlistSidebar = document.querySelector('.wishlist-sidebar');
        if (!wishlistSidebar) return;
        
        const wishlistItems = wishlistSidebar.querySelector('.wishlist-sidebar-items');
        const wishlistEmpty = wishlistSidebar.querySelector('.wishlist-sidebar-empty');
        
        if (!wishlistItems) return;
        
        if (this.items.length === 0) {
            wishlistItems.style.display = 'none';
            wishlistEmpty.style.display = 'block';
        } else {
            wishlistItems.style.display = 'block';
            wishlistEmpty.style.display = 'none';
            
            wishlistItems.innerHTML = this.items.map(item => `
                <div class="wishlist-sidebar-item" data-product-id="${item.id}">
                    <div class="wishlist-sidebar-item-image">
                        ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ''}
                    </div>
                    <div class="wishlist-sidebar-item-info">
                        <div class="wishlist-sidebar-item-name">${item.name}</div>
                        <div class="wishlist-sidebar-item-price">
                            ${item.salePrice ? `<span class="wishlist-sidebar-item-sale-price">${ShopTemplate.formatPrice(item.salePrice)}</span>` : ''}
                            <span class="wishlist-sidebar-item-${item.salePrice ? 'original-' : ''}price">${ShopTemplate.formatPrice(item.price)}</span>
                        </div>
                    </div>
                    <button class="wishlist-sidebar-item-remove" type="button" data-product-id="${item.id}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            `).join('');
            
            // Initialize remove buttons
            this.initWishlistRemoveButtons();
        }
    }
    
    updateWishlistDropdown() {
        const wishlistDropdown = document.querySelector('.wishlist-dropdown');
        if (!wishlistDropdown) return;
        
        const wishlistItems = wishlistDropdown.querySelector('.wishlist-dropdown-items');
        const wishlistEmpty = wishlistDropdown.querySelector('.wishlist-dropdown-empty');
        
        if (!wishlistItems) return;
        
        if (this.items.length === 0) {
            wishlistItems.style.display = 'none';
            wishlistEmpty.style.display = 'block';
        } else {
            wishlistItems.style.display = 'block';
            wishlistEmpty.style.display = 'none';
            
            // Update items (show only first 3)
            const displayItems = this.items.slice(0, 3);
            wishlistItems.innerHTML = displayItems.map(item => `
                <div class="wishlist-dropdown-item" data-product-id="${item.id}">
                    <div class="wishlist-dropdown-item-image">
                        ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ''}
                    </div>
                    <div class="wishlist-dropdown-item-info">
                        <div class="wishlist-dropdown-item-name">${item.name}</div>
                        <div class="wishlist-dropdown-item-price">${ShopTemplate.formatPrice(item.salePrice || item.price)}</div>
                    </div>
                </div>
            `).join('');
            
            // Show more items count
            if (this.items.length > 3) {
                const moreCount = this.items.length - 3;
                wishlistItems.innerHTML += `
                    <div class="wishlist-dropdown-more">
                        +${moreCount} more items
                    </div>
                `;
            }
        }
    }
    
    initWishlistRemoveButtons() {
        const removeButtons = document.querySelectorAll('.wishlist-sidebar-item-remove');
        removeButtons.forEach(btn => {
            const productId = btn.dataset.productId;
            if (!productId) return;
            
            btn.addEventListener('click', () => {
                this.removeItem(productId);
            });
        });
    }
}

// ============================================
// Compare Management
// ============================================
class Compare {
    constructor() {
        this.items = [];
        this.storageKey = 'shop-template-compare';
        this.maxItems = 4;
        this.load();
    }
    
    load() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                this.items = JSON.parse(saved);
            } catch (e) {
                this.items = [];
            }
        }
        this.updateUI();
        this.updateBadge();
    }
    
    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
        this.updateUI();
        this.updateBadge();
    }
    
    addItem(product) {
        if (this.items.length >= this.maxItems) {
            ShopTemplate.showToast(`Maximum ${this.maxItems} items can be compared`, 'warning');
            return;
        }
        
        if (!this.hasItem(product.id)) {
            this.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                salePrice: product.salePrice || null,
                image: product.image || null,
                rating: product.rating || 0,
                features: product.features || []
            });
            this.save();
            ShopTemplate.showToast(`${product.name} added to compare`, 'success');
        } else {
            ShopTemplate.showToast('Product already in compare', 'info');
        }
    }
    
    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.save();
        ShopTemplate.showToast('Item removed from compare', 'info');
    }
    
    clear() {
        this.items = [];
        this.save();
        ShopTemplate.showToast('Compare list cleared', 'info');
    }
    
    getItemCount() {
        return this.items.length;
    }
    
    getItem(productId) {
        return this.items.find(item => item.id === productId);
    }
    
    hasItem(productId) {
        return this.items.some(item => item.id === productId);
    }
    
    updateUI() {
        this.updateCompareSidebar();
    }
    
    updateBadge() {
        const badge = document.querySelector('.compare-badge');
        if (badge) {
            badge.textContent = this.getItemCount();
            badge.style.display = this.getItemCount() > 0 ? 'flex' : 'none';
        }
    }
    
    updateCompareSidebar() {
        const compareSidebar = document.querySelector('.compare-sidebar');
        if (!compareSidebar) return;
        
        const compareItems = compareSidebar.querySelector('.compare-sidebar-items');
        const compareEmpty = compareSidebar.querySelector('.compare-sidebar-empty');
        const compareTable = compareSidebar.querySelector('.compare-sidebar-table');
        
        if (!compareItems || !compareTable) return;
        
        if (this.items.length === 0) {
            compareItems.style.display = 'none';
            compareTable.style.display = 'none';
            compareEmpty.style.display = 'block';
        } else {
            compareItems.style.display = 'block';
            compareTable.style.display = 'block';
            compareEmpty.style.display = 'none';
            
            // Update items list
            compareItems.innerHTML = this.items.map(item => `
                <div class="compare-sidebar-item" data-product-id="${item.id}">
                    <div class="compare-sidebar-item-image">
                        ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ''}
                    </div>
                    <div class="compare-sidebar-item-info">
                        <div class="compare-sidebar-item-name">${item.name}</div>
                        <div class="compare-sidebar-item-price">${ShopTemplate.formatPrice(item.salePrice || item.price)}</div>
                    </div>
                    <button class="compare-sidebar-item-remove" type="button" data-product-id="${item.id}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            `).join('');
            
            // Update compare table
            this.updateCompareTable();
            
            // Initialize remove buttons
            this.initCompareRemoveButtons();
        }
    }
    
    updateCompareTable() {
        const compareTable = document.querySelector('.compare-sidebar-table');
        if (!compareTable) return;
        
        const tableBody = compareTable.querySelector('tbody');
        if (!tableBody) return;
        
        // Get all unique features
        const allFeatures = new Set();
        this.items.forEach(item => {
            (item.features || []).forEach(feature => {
                allFeatures.add(feature.name);
            });
        });
        
        // Build table rows
        let tableHTML = '';
        
        // Price row
        tableHTML += `
            <tr>
                <th>Price</th>
                ${this.items.map(item => `
                    <td>${ShopTemplate.formatPrice(item.salePrice || item.price)}</td>
                `).join('')}
            </tr>
        `;
        
        // Rating row
        tableHTML += `
            <tr>
                <th>Rating</th>
                ${this.items.map(item => `
                    <td>
                        <div class="rating rating-sm">
                            ${[...Array(5)].map((_, i) => `
                                <svg class="rating-star ${i >= Math.round(item.rating) ? 'empty' : ''}" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                                </svg>
                            `).join('')}
                        </div>
                    </td>
                `).join('')}
            </tr>
        `;
        
        // Features rows
        allFeatures.forEach(featureName => {
            tableHTML += `
                <tr>
                    <th>${featureName}</th>
                    ${this.items.map(item => {
                        const feature = (item.features || []).find(f => f.name === featureName);
                        return `<td>${feature ? feature.value : '-'}</td>`;
                    }).join('')}
                </tr>
            `;
        });
        
        // Actions row
        tableHTML += `
            <tr>
                <th>Actions</th>
                ${this.items.map(item => `
                    <td>
                        <button class="btn btn-sm btn-outline-primary" type="button">
                            Add to Cart
                        </button>
                    </td>
                `).join('')}
            </tr>
        `;
        
        tableBody.innerHTML = tableHTML;
    }
    
    initCompareRemoveButtons() {
        const removeButtons = document.querySelectorAll('.compare-sidebar-item-remove');
        removeButtons.forEach(btn => {
            const productId = btn.dataset.productId;
            if (!productId) return;
            
            btn.addEventListener('click', () => {
                this.removeItem(productId);
            });
        });
    }
}

// ============================================
// Product Quick View
// ============================================
function initProductQuickView() {
    const quickViewBtns = document.querySelectorAll('.product-quick-view');
    quickViewBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            if (!productId) return;
            
            // In a real app, you would fetch the product details
            // For demo purposes, we'll show a loading state
            showProductQuickView(productId);
        });
    });
}

function showProductQuickView(productId) {
    // This would be implemented based on your backend API
    // For now, just show a toast
    ShopTemplate.showToast(`Quick view for product ${productId} would open here`, 'info');
}

// ============================================
// Product Filter
// ============================================
class ProductFilter {
    constructor() {
        this.filters = {
            categories: [],
            priceRange: [0, 1000],
            rating: 0,
            brands: [],
            inStock: true,
            onSale: false
        };
        this.init();
    }
    
    init() {
        this.initCategoryFilters();
        this.initPriceRange();
        this.initRatingFilter();
        this.initBrandFilters();
        this.initStockFilter();
        this.initSaleFilter();
        this.initFilterActions();
    }
    
    initCategoryFilters() {
        const checkboxes = document.querySelectorAll('.filter-category input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.filters.categories = Array.from(
                    document.querySelectorAll('.filter-category input[type="checkbox"]:checked')
                ).map(cb => cb.value);
                this.applyFilters();
            });
        });
    }
    
    initPriceRange() {
        const rangeInput = document.querySelector('.filter-price-range input[type="range"]');
        const minInput = document.querySelector('.filter-price-min input');
        const maxInput = document.querySelector('.filter-price-max input');
        
        if (rangeInput) {
            rangeInput.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                this.filters.priceRange = [value, this.filters.priceRange[1]];
                this.applyFilters();
            });
        }
        
        if (minInput) {
            minInput.addEventListener('change', (e) => {
                const value = parseInt(e.target.value) || 0;
                this.filters.priceRange = [value, this.filters.priceRange[1]];
                this.applyFilters();
            });
        }
        
        if (maxInput) {
            maxInput.addEventListener('change', (e) => {
                const value = parseInt(e.target.value) || 1000;
                this.filters.priceRange = [this.filters.priceRange[0], value];
                this.applyFilters();
            });
        }
    }
    
    initRatingFilter() {
        const stars = document.querySelectorAll('.filter-rating .rating-star');
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                this.filters.rating = 5 - index;
                stars.forEach((s, i) => {
                    s.classList.toggle('empty', i > index);
                });
                this.applyFilters();
            });
        });
    }
    
    initBrandFilters() {
        const checkboxes = document.querySelectorAll('.filter-brand input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.filters.brands = Array.from(
                    document.querySelectorAll('.filter-brand input[type="checkbox"]:checked')
                ).map(cb => cb.value);
                this.applyFilters();
            });
        });
    }
    
    initStockFilter() {
        const checkbox = document.querySelector('.filter-stock input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener('change', () => {
                this.filters.inStock = checkbox.checked;
                this.applyFilters();
            });
        }
    }
    
    initSaleFilter() {
        const checkbox = document.querySelector('.filter-sale input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener('change', () => {
                this.filters.onSale = checkbox.checked;
                this.applyFilters();
            });
        }
    }
    
    initFilterActions() {
        const applyBtn = document.querySelector('.filter-actions .btn-apply');
        const resetBtn = document.querySelector('.filter-actions .btn-reset');
        
        applyBtn?.addEventListener('click', () => {
            this.applyFilters();
            this.closeFilterSidebar();
        });
        
        resetBtn?.addEventListener('click', () => {
            this.resetFilters();
        });
    }
    
    applyFilters() {
        // In a real app, this would trigger an AJAX request or filter the products
        // For demo purposes, we'll just show a toast
        const filterCount = Object.values(this.filters).reduce((count, value) => {
            if (Array.isArray(value)) {
                return count + (value.length > 0 ? 1 : 0);
            }
            return count + (value ? 1 : 0);
        }, 0);
        
        ShopTemplate.showToast(`Applied ${filterCount} filters`, 'info');
    }
    
    resetFilters() {
        this.filters = {
            categories: [],
            priceRange: [0, 1000],
            rating: 0,
            brands: [],
            inStock: true,
            onSale: false
        };
        
        // Reset UI
        document.querySelectorAll('.filter-category input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        
        document.querySelectorAll('.filter-brand input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        
        document.querySelector('.filter-stock input[type="checkbox"]').checked = true;
        document.querySelector('.filter-sale input[type="checkbox"]').checked = false;
        
        document.querySelectorAll('.filter-rating .rating-star').forEach((star, index) => {
            star.classList.toggle('empty', index > 0);
        });
        
        ShopTemplate.showToast('Filters reset', 'info');
        this.applyFilters();
    }
    
    closeFilterSidebar() {
        const filterSidebar = document.querySelector('.filter-sidebar');
        const filterOverlay = document.querySelector('.filter-sidebar-overlay');
        
        filterSidebar?.classList.remove('open');
        filterOverlay?.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// ============================================
// Product Sort
// ============================================
function initProductSort() {
    const sortSelect = document.querySelector('.products-sort select');
    if (!sortSelect) return;
    
    sortSelect.addEventListener('change', (e) => {
        const sortBy = e.target.value;
        // In a real app, this would trigger sorting
        ShopTemplate.showToast(`Sorting by: ${sortBy}`, 'info');
    });
}

// ============================================
// Product View Toggle
// ============================================
function initProductViewToggle() {
    const viewToggle = document.querySelectorAll('.products-view-toggle a');
    const productsGrid = document.querySelector('.products-grid');
    
    if (!productsGrid) return;
    
    viewToggle.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active from all
            viewToggle.forEach(t => t.classList.remove('active'));
            
            // Add active to clicked
            toggle.classList.add('active');
            
            // Toggle view
            const view = toggle.dataset.view;
            productsGrid.classList.remove('grid-view', 'list-view');
            productsGrid.classList.add(`${view}-view`);
            
            // Save preference
            localStorage.setItem('products-view', view);
        });
    });
    
    // Load saved preference
    const savedView = localStorage.getItem('products-view') || 'grid';
    const activeToggle = document.querySelector(`.products-view-toggle a[data-view="${savedView}"]`);
    if (activeToggle) {
        activeToggle.classList.add('active');
        productsGrid.classList.add(`${savedView}-view`);
    }
}

// ============================================
// Recently Viewed Products
// ============================================
class RecentlyViewed {
    constructor() {
        this.items = [];
        this.storageKey = 'shop-template-recently-viewed';
        this.maxItems = 12;
        this.load();
    }
    
    load() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                this.items = JSON.parse(saved);
            } catch (e) {
                this.items = [];
            }
        }
    }
    
    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
    }
    
    addItem(product) {
        // Remove if already exists
        this.items = this.items.filter(item => item.id !== product.id);
        
        // Add to beginning
        this.items.unshift({
            id: product.id,
            name: product.name,
            price: product.price,
            salePrice: product.salePrice || null,
            image: product.image || null,
            url: product.url || window.location.href
        });
        
        // Limit to max items
        this.items = this.items.slice(0, this.maxItems);
        
        this.save();
    }
    
    getItems() {
        return this.items;
    }
}

// ============================================
// Newsletter Subscription
// ============================================
function initNewsletter() {
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = form.querySelector('input[type="email"]').value;
            
            if (email) {
                // In a real app, this would submit to your backend
                ShopTemplate.showToast('Thank you for subscribing!', 'success');
                form.reset();
            } else {
                ShopTemplate.showToast('Please enter a valid email address', 'error');
            }
        });
    });
}

// ============================================
// Initialize Everything
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize cart, wishlist, compare
    window.cart = new Cart();
    window.wishlist = new Wishlist();
    window.compare = new Compare();
    
    // Initialize product filter
    window.productFilter = new ProductFilter();
    
    // Initialize recently viewed
    window.recentlyViewed = new RecentlyViewed();
    
    // Initialize other features
    initProductQuickView();
    initProductSort();
    initProductViewToggle();
    initNewsletter();
    
    // Add to cart buttons
    const addToCartBtns = document.querySelectorAll('.btn-add-to-cart');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            if (!productId) return;
            
            // In a real app, you would fetch the product details
            // For demo purposes, we'll use placeholder data
            const product = {
                id: productId,
                name: btn.dataset.productName || 'Product',
                price: parseFloat(btn.dataset.productPrice) || 0,
                salePrice: btn.dataset.productSalePrice ? parseFloat(btn.dataset.productSalePrice) : null,
                image: btn.dataset.productImage || null,
                stock: parseInt(btn.dataset.productStock) || Infinity
            };
            
            cart.addItem(product);
        });
    });
    
    // Add to wishlist buttons
    const addToWishlistBtns = document.querySelectorAll('.btn-add-to-wishlist');
    addToWishlistBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            if (!productId) return;
            
            const product = {
                id: productId,
                name: btn.dataset.productName || 'Product',
                price: parseFloat(btn.dataset.productPrice) || 0,
                salePrice: btn.dataset.productSalePrice ? parseFloat(btn.dataset.productSalePrice) : null,
                image: btn.dataset.productImage || null
            };
            
            wishlist.addItem(product);
            
            // Toggle button state
            btn.classList.toggle('active');
            btn.querySelector('svg')?.classList.toggle('active');
        });
    });
    
    // Add to compare buttons
    const addToCompareBtns = document.querySelectorAll('.btn-add-to-compare');
    addToCompareBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            if (!productId) return;
            
            const product = {
                id: productId,
                name: btn.dataset.productName || 'Product',
                price: parseFloat(btn.dataset.productPrice) || 0,
                salePrice: btn.dataset.productSalePrice ? parseFloat(btn.dataset.productSalePrice) : null,
                image: btn.dataset.productImage || null,
                rating: parseFloat(btn.dataset.productRating) || 0,
                features: btn.dataset.productFeatures ? JSON.parse(btn.dataset.productFeatures) : []
            };
            
            compare.addItem(product);
        });
    });
    
    // Track product views
    const productDetail = document.querySelector('.product-detail');
    if (productDetail) {
        const productId = productDetail.dataset.productId;
        if (productId) {
            const product = {
                id: productId,
                name: productDetail.dataset.productName || 'Product',
                price: parseFloat(productDetail.dataset.productPrice) || 0,
                salePrice: productDetail.dataset.productSalePrice ? parseFloat(productDetail.dataset.productSalePrice) : null,
                image: productDetail.dataset.productImage || null,
                url: window.location.href
            };
            recentlyViewed.addItem(product);
        }
    }
});

// ============================================
// Export for use in other modules
// ============================================
window.Store = {
    Cart,
    Wishlist,
    Compare,
    ProductFilter,
    RecentlyViewed,
    initProductQuickView,
    initNewsletter
};
