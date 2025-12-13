// GenuVoice Control Panel - JavaScript

// API Base URL (adjust if needed)
const API_BASE_URL = window.location.origin;

// Bootstrap Modal Instance
let callModal;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('GenuVoice Control Panel Initialized');
    
    // Initialize Bootstrap Modal
    const callModalElement = document.getElementById('callModal');
    callModal = new bootstrap.Modal(callModalElement);
    
    // Load customers on page load
    loadCustomers();
    
    // Auto-refresh every 30 seconds
    setInterval(loadCustomers, 30000);
});

/**
 * Load all customers from API
 */
async function loadCustomers() {
    console.log('Loading customers...');
    
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorAlert = document.getElementById('error-alert');
    const tableContainer = document.getElementById('customers-table-container');
    
    // Show loading
    loadingIndicator.classList.remove('d-none');
    errorAlert.classList.add('d-none');
    tableContainer.classList.add('d-none');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/customers`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const customers = await response.json();
        console.log(`Loaded ${customers.length} customers`);
        
        // Update stats
        updateStats(customers);
        
        // Populate table
        populateCustomersTable(customers);
        
        // Hide loading, show table
        loadingIndicator.classList.add('d-none');
        tableContainer.classList.remove('d-none');
        
    } catch (error) {
        console.error('Error loading customers:', error);
        
        // Show error
        document.getElementById('error-message').textContent = 
            `Failed to load customers: ${error.message}`;
        loadingIndicator.classList.add('d-none');
        errorAlert.classList.remove('d-none');
    }
}

/**
 * Update dashboard statistics
 */
function updateStats(customers) {
    const totalCustomers = customers.length;
    const activeCustomers = customers.filter(c => c.status === 'active').length;
    const promisedCustomers = customers.filter(c => c.status === 'promised_to_pay').length;
    const totalDebt = customers.reduce((sum, c) => sum + c.debt_amount, 0);
    
    document.getElementById('total-customers').textContent = totalCustomers;
    document.getElementById('active-customers').textContent = activeCustomers;
    document.getElementById('promised-customers').textContent = promisedCustomers;
    document.getElementById('total-debt').textContent = 
        `$${totalDebt.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;
}

/**
 * Populate customers table
 */
function populateCustomersTable(customers) {
    const tbody = document.getElementById('customers-tbody');
    tbody.innerHTML = '';
    
    if (customers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mt-2">No customers found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    customers.forEach(customer => {
        const row = createCustomerRow(customer);
        tbody.appendChild(row);
    });
}

/**
 * Create a table row for a customer
 */
function createCustomerRow(customer) {
    const row = document.createElement('tr');
    row.classList.add('fade-in');
    
    // Name
    const nameCell = document.createElement('td');
    nameCell.innerHTML = `<strong>${escapeHtml(customer.name)}</strong>`;
    row.appendChild(nameCell);
    
    // Phone
    const phoneCell = document.createElement('td');
    phoneCell.innerHTML = `<code>${escapeHtml(customer.phone)}</code>`;
    row.appendChild(phoneCell);
    
    // Debt Amount
    const debtCell = document.createElement('td');
    debtCell.innerHTML = `<span class="debt-amount">$${customer.debt_amount.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>`;
    row.appendChild(debtCell);
    
    // Days Overdue
    const overdueCell = document.createElement('td');
    const overdueClass = customer.days_overdue > 30 ? 'days-overdue-high' : 
                        customer.days_overdue > 7 ? 'days-overdue-medium' : 'days-overdue-low';
    overdueCell.innerHTML = `<span class="${overdueClass}">${customer.days_overdue} days</span>`;
    row.appendChild(overdueCell);
    
    // Status
    const statusCell = document.createElement('td');
    statusCell.appendChild(createStatusBadge(customer.status));
    row.appendChild(statusCell);
    
    // Risk Level
    const riskCell = document.createElement('td');
    riskCell.appendChild(createRiskBadge(customer.risk_level));
    row.appendChild(riskCell);
    
    // Last Call
    const lastCallCell = document.createElement('td');
    lastCallCell.innerHTML = customer.last_call_date ? 
        `<small>${formatDate(customer.last_call_date)}</small>` : 
        `<span class="text-muted">Never</span>`;
    row.appendChild(lastCallCell);
    
    // Action Button
    const actionCell = document.createElement('td');
    const callButton = document.createElement('button');
    callButton.className = 'btn btn-sm btn-call';
    callButton.innerHTML = '<i class="bi bi-telephone-fill"></i> Call';
    callButton.onclick = () => initiateCall(customer);
    actionCell.appendChild(callButton);
    row.appendChild(actionCell);
    
    return row;
}

/**
 * Create status badge
 */
function createStatusBadge(status) {
    const badge = document.createElement('span');
    badge.className = 'badge';
    
    const statusMap = {
        'active': { text: 'Active', class: 'badge-active' },
        'promised_to_pay': { text: 'Promised', class: 'badge-promised' },
        'refused': { text: 'Refused', class: 'badge-refused' },
        'callback_requested': { text: 'Callback', class: 'badge-callback' },
        'voicemail': { text: 'Voicemail', class: 'badge-voicemail' },
        'wrong_number': { text: 'Wrong #', class: 'badge-wrong-number' }
    };
    
    const statusInfo = statusMap[status] || { text: status, class: 'bg-secondary' };
    badge.textContent = statusInfo.text;
    badge.classList.add(statusInfo.class);
    
    return badge;
}

/**
 * Create risk level badge
 */
function createRiskBadge(riskLevel) {
    const badge = document.createElement('span');
    badge.className = 'badge';
    
    const riskMap = {
        'low': { text: 'Low', class: 'badge-risk-low' },
        'medium': { text: 'Medium', class: 'badge-risk-medium' },
        'high': { text: 'High', class: 'badge-risk-high' }
    };
    
    const riskInfo = riskMap[riskLevel] || { text: riskLevel, class: 'bg-secondary' };
    badge.textContent = riskInfo.text;
    badge.classList.add(riskInfo.class);
    
    return badge;
}

/**
 * Initiate call to customer
 */
async function initiateCall(customer) {
    console.log('Initiating call to:', customer.name, customer.phone);
    
    // Show modal
    callModal.show();
    
    // Reset modal state
    document.getElementById('call-loading').classList.remove('d-none');
    document.getElementById('call-success').classList.add('d-none');
    document.getElementById('call-error').classList.add('d-none');
    
    // Set customer info
    document.getElementById('call-customer-name').textContent = customer.name;
    document.getElementById('call-customer-phone').textContent = customer.phone;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/call`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone: customer.phone
            })
        });
        
        const result = await response.json();
        
        // Hide loading
        document.getElementById('call-loading').classList.add('d-none');
        
        if (response.ok && result.success) {
            // Show success
            document.getElementById('call-success').classList.remove('d-none');
            document.getElementById('success-customer-name').textContent = result.customer_name;
            document.getElementById('conversation-id').textContent = result.conversation_id || 'N/A';
            
            // Reload customers after 2 seconds
            setTimeout(() => {
                loadCustomers();
            }, 2000);
            
        } else {
            // Show error
            document.getElementById('call-error').classList.remove('d-none');
            document.getElementById('call-error-message').textContent = 
                result.message || 'Unknown error occurred';
        }
        
    } catch (error) {
        console.error('Error initiating call:', error);
        
        // Hide loading, show error
        document.getElementById('call-loading').classList.add('d-none');
        document.getElementById('call-error').classList.remove('d-none');
        document.getElementById('call-error-message').textContent = 
            `Network error: ${error.message}`;
    }
}

/**
 * Format date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

