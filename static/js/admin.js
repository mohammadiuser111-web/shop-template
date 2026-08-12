/**
 * Shop Template - Admin JavaScript
 * ================================
 * Admin panel specific JavaScript functionality
 */

// ============================================
// Admin Dashboard
// ============================================
class AdminDashboard {
    constructor() {
        this.init();
    }
    
    init() {
        this.initStats();
        this.initCharts();
        this.initRecentActivity();
        this.initQuickActions();
    }
    
    initStats() {
        // In a real app, these would be fetched from the API
        // For demo purposes, we'll use placeholder data
        const stats = [
            { label: 'Total Sales', value: 12450, change: 12.5, icon: 'dollar-sign' },
            { label: 'Total Orders', value: 342, change: 8.3, icon: 'shopping-bag' },
            { label: 'Total Customers', value: 1856, change: -2.1, icon: 'users' },
            { label: 'Total Products', value: 245, change: 5.7, icon: 'package' }
        ];
        
        this.updateStats(stats);
    }
    
    updateStats(stats) {
        const statsContainer = document.querySelector('.admin-stats');
        if (!statsContainer) return;
        
        statsContainer.innerHTML = stats.map(stat => `
            <div class="admin-stat-card">
                <div class="admin-stat-icon ${stat.change >= 0 ? 'success' : 'error'}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${this.getIcon(stat.icon)}
                    </svg>
                </div>
                <div class="admin-stat-content">
                    <div class="admin-stat-value">${ShopTemplate.formatNumber(stat.value)}</div>
                    <div class="admin-stat-label">${stat.label}</div>
                    <div class="admin-stat-change ${stat.change >= 0 ? 'positive' : 'negative'}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            ${stat.change >= 0 ? '<polyline points="22 6 18 10 15 10 9 14 5 11 1 8"/>' : '<polyline points="22 18 18 14 15 14 9 10 5 11 1 14"/>'}
                        </svg>
                        <span>${Math.abs(stat.change)}%</span>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    getIcon(name) {
        const icons = {
            'dollar-sign': '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
            'shopping-bag': '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>',
            'users': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
            'package': '<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>'
        };
        return icons[name] || '<line x1="0" y1="0" x2="24" y2="24"/>';
    }
    
    initCharts() {
        // In a real app, these would be rendered using a charting library
        // For demo purposes, we'll just show placeholder elements
        this.initSalesChart();
        this.initOrdersChart();
    }
    
    initSalesChart() {
        const chartContainer = document.querySelector('.chart-sales');
        if (!chartContainer) return;
        
        // Placeholder for chart
        chartContainer.innerHTML = `
            <div class="chart-placeholder">
                <div class="chart-placeholder-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                        <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
                    </svg>
                </div>
                <div class="chart-placeholder-text">Sales Chart</div>
                <div class="chart-placeholder-hint">Chart would be rendered here</div>
            </div>
        `;
    }
    
    initOrdersChart() {
        const chartContainer = document.querySelector('.chart-orders');
        if (!chartContainer) return;
        
        chartContainer.innerHTML = `
            <div class="chart-placeholder">
                <div class="chart-placeholder-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 6v6l4 2"/>
                    </svg>
                </div>
                <div class="chart-placeholder-text">Orders Chart</div>
                <div class="chart-placeholder-hint">Chart would be rendered here</div>
            </div>
        `;
    }
    
    initRecentActivity() {
        const activityContainer = document.querySelector('.admin-recent-activity');
        if (!activityContainer) return;
        
        // Placeholder data
        const activities = [
            { type: 'order', message: 'New order #12345 from John Doe', time: '2 min ago', status: 'success' },
            { type: 'product', message: 'Product "Wireless Headphones" updated', time: '10 min ago', status: 'info' },
            { type: 'customer', message: 'New customer registered: Jane Smith', time: '1 hour ago', status: 'success' },
            { type: 'review', message: 'New review for "Smart Watch"', time: '2 hours ago', status: 'warning' },
            { type: 'stock', message: 'Low stock alert: Only 5 "USB Cable" left', time: '3 hours ago', status: 'error' }
        ];
        
        activityContainer.innerHTML = activities.map(activity => `
            <div class="admin-activity-item">
                <div class="admin-activity-icon ${activity.status}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${this.getActivityIcon(activity.type)}
                    </svg>
                </div>
                <div class="admin-activity-content">
                    <div class="admin-activity-message">${activity.message}</div>
                    <div class="admin-activity-time">${activity.time}</div>
                </div>
            </div>
        `).join('');
    }
    
    getActivityIcon(type) {
        const icons = {
            'order': '<path d="M21 15a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="21"/>',
            'product': '<path d="M21.2 15c.7-1.2 1-2.5.7-3.9-.6-2.4-2.4-4.2-4.8-4.8-.9-.3-1.8-.5-2.7-.5-3.3 0-6 2.7-6 6s2.7 6 6 6c.9 0 1.8-.2 2.7-.5"/><path d="M12 3v18"/><path d="M19 7.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/><path d="M5 7.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/><path d="M12 18a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/>',
            'customer': '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
            'review': '<path d="M18 6 6 18"/><path d="M6 6l12 12"/>',
            'stock': '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>'
        };
        return icons[type] || '<line x1="0" y1="0" x2="24" y2="24"/>';
    }
    
    initQuickActions() {
        const quickActions = document.querySelector('.admin-quick-actions');
        if (!quickActions) return;
        
        const actions = [
            { icon: 'plus-circle', label: 'Add Product', url: '/admin/products/add/' },
            { icon: 'user-plus', label: 'Add Customer', url: '/admin/customers/add/' },
            { icon: 'file-text', label: 'Create Order', url: '/admin/orders/add/' },
            { icon: 'message-circle', label: 'Send Newsletter', url: '/admin/newsletter/' }
        ];
        
        quickActions.innerHTML = actions.map(action => `
            <a href="${action.url}" class="admin-quick-action">
                <div class="admin-quick-action-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${this.getQuickActionIcon(action.icon)}
                    </svg>
                </div>
                <div class="admin-quick-action-label">${action.label}</div>
            </a>
        `).join('');
    }
    
    getQuickActionIcon(name) {
        const icons = {
            'plus-circle': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
            'user-plus': '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/><line x1="20" y1="6" x2="24" y2="2"/>',
            'file-text': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
            'message-circle': '<path d="M3 20l1.3 -3.9A9 8 0 1 1 7.7 19l-4.7 1"/><path d="M12 12v.01"/>'
        };
        return icons[name] || '<line x1="0" y1="0" x2="24" y2="24"/>';
    }
}

// ============================================
// Admin Table
// ============================================
class AdminTable {
    constructor(tableElement) {
        this.table = tableElement;
        this.init();
    }
    
    init() {
        this.initCheckboxes();
        this.initRowSelection();
        this.initBulkActions();
        this.initPagination();
        this.initSearch();
    }
    
    initCheckboxes() {
        const selectAll = this.table.querySelector('.select-all');
        const checkboxes = this.table.querySelectorAll('tbody input[type="checkbox"]');
        
        if (selectAll) {
            selectAll.addEventListener('change', () => {
                checkboxes.forEach(cb => {
                    cb.checked = selectAll.checked;
                    this.toggleRowSelected(cb.closest('tr'), cb.checked);
                });
                this.updateBulkActions();
            });
        }
        
        checkboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                this.toggleRowSelected(cb.closest('tr'), cb.checked);
                this.updateSelectAll(selectAll, checkboxes);
                this.updateBulkActions();
            });
        });
    }
    
    toggleRowSelected(row, selected) {
        row.classList.toggle('selected', selected);
    }
    
    updateSelectAll(selectAll, checkboxes) {
        if (!selectAll) return;
        
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        selectAll.checked = allChecked;
        
        // Indeterminate state
        const someChecked = Array.from(checkboxes).some(cb => cb.checked);
        selectAll.indeterminate = !allChecked && someChecked;
    }
    
    updateBulkActions() {
        const bulkActions = document.querySelector('.admin-table-bulk-actions');
        if (!bulkActions) return;
        
        const selectedCount = this.table.querySelectorAll('tbody tr.selected').length;
        const bulkCount = bulkActions.querySelector('.bulk-count');
        
        if (bulkCount) {
            bulkCount.textContent = selectedCount > 0 ? ` (${selectedCount} selected)` : '';
        }
        
        bulkActions.style.display = selectedCount > 0 ? 'flex' : 'none';
    }
    
    initRowSelection() {
        const rows = this.table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', (e) => {
                // Skip if clicking on a checkbox or action button
                if (e.target.type === 'checkbox' || e.target.closest('button, a')) return;
                
                const checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    this.toggleRowSelected(row, checkbox.checked);
                    this.updateSelectAll(
                        this.table.querySelector('.select-all'),
                        this.table.querySelectorAll('tbody input[type="checkbox"]')
                    );
                    this.updateBulkActions();
                }
            });
        });
    }
    
    initBulkActions() {
        const bulkActions = document.querySelector('.admin-table-bulk-actions');
        if (!bulkActions) return;
        
        const selectAll = bulkActions.querySelector('.bulk-select-all');
        const selectNone = bulkActions.querySelector('.bulk-select-none');
        const deleteSelected = bulkActions.querySelector('.bulk-delete');
        
        selectAll?.addEventListener('click', () => {
            const checkboxes = this.table.querySelectorAll('tbody input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.checked = true;
                this.toggleRowSelected(cb.closest('tr'), true);
            });
            this.updateSelectAll(
                this.table.querySelector('.select-all'),
                checkboxes
            );
            this.updateBulkActions();
        });
        
        selectNone?.addEventListener('click', () => {
            const checkboxes = this.table.querySelectorAll('tbody input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.checked = false;
                this.toggleRowSelected(cb.closest('tr'), false);
            });
            this.updateSelectAll(
                this.table.querySelector('.select-all'),
                checkboxes
            );
            this.updateBulkActions();
        });
        
        deleteSelected?.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete the selected items?')) {
                const selectedRows = this.table.querySelectorAll('tbody tr.selected');
                selectedRows.forEach(row => {
                    row.remove();
                });
                this.updateBulkActions();
                ShopTemplate.showToast('Selected items deleted', 'success');
            }
        });
    }
    
    initPagination() {
        const pagination = document.querySelector('.admin-pagination');
        if (!pagination) return;
        
        const pageSizeSelect = pagination.querySelector('.admin-pagination-size select');
        pageSizeSelect?.addEventListener('change', (e) => {
            const pageSize = parseInt(e.target.value);
            // In a real app, this would trigger a page reload or AJAX request
            ShopTemplate.showToast(`Page size changed to ${pageSize}`, 'info');
        });
    }
    
    initSearch() {
        const searchInput = document.querySelector('.admin-filter-search input');
        if (!searchInput) return;
        
        searchInput.addEventListener('input', ShopTemplate.debounce(() => {
            const searchTerm = searchInput.value.toLowerCase();
            const rows = this.table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }
}

// ============================================
// Admin Form
// ============================================
class AdminForm {
    constructor(formElement) {
        this.form = formElement;
        this.init();
    }
    
    init() {
        this.initValidation();
        this.initFileUpload();
        this.initRichTextEditor();
        this.initDatePicker();
        this.initColorPicker();
        this.initSubmit();
    }
    
    initValidation() {
        const inputs = this.form.querySelectorAll('[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateInput(input);
            });
        });
    }
    
    validateInput(input) {
        const value = input.value.trim();
        const isValid = value.length > 0;
        
        input.classList.toggle('is-invalid', !isValid);
        
        // Remove error message if exists
        const existingError = input.parentElement.querySelector('.form-error');
        if (existingError) existingError.remove();
        
        // Add error message if invalid
        if (!isValid && !existingError) {
            const error = document.createElement('div');
            error.className = 'form-error';
            error.textContent = 'This field is required';
            input.parentElement.appendChild(error);
        }
        
        return isValid;
    }
    
    initFileUpload() {
        const fileInputs = this.form.querySelectorAll('.file-upload');
        fileInputs.forEach(container => {
            const input = container.querySelector('input[type="file"]');
            const preview = container.querySelector('.file-upload-preview');
            const removeBtn = container.querySelector('.file-upload-remove');
            
            if (!input || !preview) return;
            
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.updateFilePreview(file, preview);
                }
            });
            
            removeBtn?.addEventListener('click', (e) => {
                e.preventDefault();
                input.value = '';
                preview.innerHTML = '';
                preview.style.display = 'none';
            });
        });
    }
    
    updateFilePreview(file, preview) {
        const reader = new FileReader();
        reader.onload = (e) => {
            if (file.type.startsWith('image/')) {
                preview.innerHTML = `<img src="${e.target.result}" alt="${file.name}">`;
                preview.style.display = 'block';
            } else {
                preview.innerHTML = `<span class="file-upload-filename">${file.name}</span>`;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }
    
    initRichTextEditor() {
        const textareas = this.form.querySelectorAll('.rich-text-editor');
        textareas.forEach(textarea => {
            // In a real app, you would initialize a rich text editor here
            // For demo purposes, we'll just add a placeholder
            const placeholder = document.createElement('div');
            placeholder.className = 'rich-text-placeholder';
            placeholder.textContent = 'Rich text editor would be initialized here';
            textarea.parentElement.appendChild(placeholder);
        });
    }
    
    initDatePicker() {
        const dateInputs = this.form.querySelectorAll('.datepicker');
        dateInputs.forEach(input => {
            // In a real app, you would initialize a date picker here
            // For demo purposes, we'll just add a placeholder
            input.addEventListener('focus', () => {
                ShopTemplate.showToast('Date picker would open here', 'info');
            });
        });
    }
    
    initColorPicker() {
        const colorInputs = this.form.querySelectorAll('.color-picker-input');
        colorInputs.forEach(input => {
            // In a real app, you would initialize a color picker here
            // For demo purposes, we'll just add a placeholder
            input.addEventListener('focus', () => {
                ShopTemplate.showToast('Color picker would open here', 'info');
            });
        });
    }
    
    initSubmit() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (!submitBtn) return;
        
        this.form.addEventListener('submit', (e) => {
            let isValid = true;
            const inputs = this.form.querySelectorAll('[required]');
            
            inputs.forEach(input => {
                if (!this.validateInput(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                ShopTemplate.showToast('Please fill in all required fields', 'error');
            }
        });
    }
}

// ============================================
// Admin Notification
// ============================================
class AdminNotification {
    constructor() {
        this.notifications = [];
        this.storageKey = 'admin-notifications';
        this.init();
    }
    
    init() {
        this.loadNotifications();
        this.initNotificationList();
        this.initNotificationBadge();
    }
    
    loadNotifications() {
        // In a real app, these would be fetched from the API
        // For demo purposes, we'll use placeholder data
        this.notifications = [
            { id: 1, type: 'order', message: 'New order #12345 received', time: '2 min ago', read: false },
            { id: 2, type: 'review', message: 'New product review from John Doe', time: '10 min ago', read: false },
            { id: 3, type: 'stock', message: 'Low stock alert for Wireless Headphones', time: '1 hour ago', read: true },
            { id: 4, type: 'customer', message: 'New customer registered', time: '2 hours ago', read: true },
            { id: 5, type: 'system', message: 'System update available', time: '3 hours ago', read: false }
        ];
        
        this.saveNotifications();
    }
    
    saveNotifications() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.notifications));
    }
    
    getUnreadCount() {
        return this.notifications.filter(n => !n.read).length;
    }
    
    markAsRead(id) {
        const notification = this.notifications.find(n => n.id === id);
        if (notification) {
            notification.read = true;
            this.saveNotifications();
            this.updateNotificationList();
            this.updateNotificationBadge();
        }
    }
    
    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.saveNotifications();
        this.updateNotificationList();
        this.updateNotificationBadge();
    }
    
    initNotificationList() {
        const notificationList = document.querySelector('.admin-notification-list');
        if (!notificationList) return;
        
        this.updateNotificationList();
        
        // Mark as read on click
        notificationList.addEventListener('click', (e) => {
            const notificationItem = e.target.closest('.admin-notification-item');
            if (!notificationItem) return;
            
            const id = parseInt(notificationItem.dataset.id);
            if (!isNaN(id)) {
                this.markAsRead(id);
            }
        });
    }
    
    updateNotificationList() {
        const notificationList = document.querySelector('.admin-notification-list');
        if (!notificationList) return;
        
        notificationList.innerHTML = this.notifications.map(notification => `
            <div class="admin-notification-item ${notification.read ? 'read' : 'unread'}" data-id="${notification.id}">
                <div class="admin-notification-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${this.getNotificationIcon(notification.type)}
                    </svg>
                </div>
                <div class="admin-notification-content">
                    <div class="admin-notification-message">${notification.message}</div>
                    <div class="admin-notification-time">${notification.time}</div>
                </div>
            </div>
        `).join('');
    }
    
    getNotificationIcon(type) {
        const icons = {
            'order': '<path d="M21 15a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="21"/>',
            'review': '<path d="M18 6 6 18"/><path d="M6 6l12 12"/>',
            'stock': '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
            'customer': '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
            'system': '<path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>'
        };
        return icons[type] || '<line x1="0" y1="0" x2="24" y2="24"/>';
    }
    
    initNotificationBadge() {
        const badge = document.querySelector('.admin-header-notifications-badge');
        if (!badge) return;
        
        this.updateNotificationBadge();
    }
    
    updateNotificationBadge() {
        const badge = document.querySelector('.admin-header-notifications-badge');
        if (!badge) return;
        
        const count = this.getUnreadCount();
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// ============================================
// Admin Settings
// ============================================
class AdminSettings {
    constructor() {
        this.init();
    }
    
    init() {
        this.initThemeSettings();
        this.initProfileSettings();
    }
    
    initThemeSettings() {
        const themeForm = document.querySelector('.admin-theme-settings');
        if (!themeForm) return;
        
        const themeSelect = themeForm.querySelector('select[name="theme"]');
        const colorSelect = themeForm.querySelector('select[name="theme_color"]');
        
        if (themeSelect) {
            themeSelect.value = ShopTemplate.settings.theme;
            themeSelect.addEventListener('change', (e) => {
                ShopTemplate.settings.theme = e.target.value;
                ShopTemplate.applyTheme();
            });
        }
        
        if (colorSelect) {
            colorSelect.value = ShopTemplate.settings.themeColor;
            colorSelect.addEventListener('change', (e) => {
                ShopTemplate.settings.themeColor = e.target.value;
                ShopTemplate.applyThemeColor();
            });
        }
    }
    
    initProfileSettings() {
        const profileForm = document.querySelector('.admin-profile-settings');
        if (!profileForm) return;
        
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
            ShopTemplate.showToast('Profile settings saved', 'success');
        });
    }
}

// ============================================
// Initialize Everything
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize admin dashboard
    if (document.querySelector('.admin-dashboard')) {
        window.adminDashboard = new AdminDashboard();
    }
    
    // Initialize admin tables
    const tables = document.querySelectorAll('.admin-table');
    tables.forEach(table => {
        new AdminTable(table);
    });
    
    // Initialize admin forms
    const forms = document.querySelectorAll('.admin-form');
    forms.forEach(form => {
        new AdminForm(form);
    });
    
    // Initialize admin notifications
    window.adminNotification = new AdminNotification();
    
    // Initialize admin settings
    if (document.querySelector('.admin-settings')) {
        window.adminSettings = new AdminSettings();
    }
    
    // Initialize profile dropdown
    const profileBtn = document.querySelector('.admin-header-profile');
    if (profileBtn) {
        profileBtn.addEventListener('click', () => {
            const dropdown = document.querySelector('.admin-header-profile-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('show');
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!profileBtn.contains(e.target)) {
                const dropdown = document.querySelector('.admin-header-profile-dropdown');
                if (dropdown) {
                    dropdown.classList.remove('show');
                }
            }
        });
    }
    
    // Initialize notification dropdown
    const notificationBtn = document.querySelector('.admin-header-notifications');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            const dropdown = document.querySelector('.admin-notification-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('show');
                
                // Mark all as read when opening
                if (dropdown.classList.contains('show')) {
                    window.adminNotification.markAllAsRead();
                }
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!notificationBtn.contains(e.target)) {
                const dropdown = document.querySelector('.admin-notification-dropdown');
                if (dropdown) {
                    dropdown.classList.remove('show');
                }
            }
        });
    }
});

// ============================================
// Export for use in other modules
// ============================================
window.Admin = {
    AdminDashboard,
    AdminTable,
    AdminForm,
    AdminNotification,
    AdminSettings
};
