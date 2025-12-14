// GenuVoice Control Panel - JavaScript

// API Base URL (adjust if needed)
const API_BASE_URL = window.location.origin;

// Bootstrap Modal Instance
let callModal;
// Available Agents Cache
let availableAgents = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async function () {
    console.log('GenuVoice Control Panel Initialized');

    // Initialize Bootstrap Modal
    const callModalElement = document.getElementById('callModal');
    if (callModalElement) {
        callModal = new bootstrap.Modal(callModalElement);
    }

    // Load available agents first
    await loadAgents();

    // Then load customers
    loadCustomers();

    // Auto-refresh every 30 seconds
    setInterval(loadCustomers, 30000);
});

/**
 * Fetch available agents from API
 */
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/agents`);
        if (response.ok) {
            availableAgents = await response.json();
            console.log(`Loaded ${availableAgents.length} agents`);
        } else {
            console.error('Failed to load agents');
        }
    } catch (e) {
        console.error('Error loading agents:', e);
    }
}

/**
 * Load all customers from API
 */
async function loadCustomers() {
    console.log('Loading customers...');

    try {
        const response = await fetch(`${API_BASE_URL}/api/customers`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const customers = await response.json();
        console.log(`Loaded ${customers.length} customers`);

        updateStats(customers);
        populateCustomersTable(customers);

    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

/**
 * Update dashboard statistics
 */
function updateStats(customers) {
    const totalCustomers = customers.length;
    const totalRecovered = customers.reduce((sum, c) => c.status === 'promised_to_pay' ? sum + c.debt_amount : sum, 0);
    const totalDebt = customers.reduce((sum, c) => sum + c.debt_amount, 0);

    const elTotal = document.getElementById('total-debt');
    if (elTotal) elTotal.textContent = totalDebt.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });

    const elRecovered = document.getElementById('total-recovered');
    if (elRecovered) elRecovered.textContent = totalRecovered.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });

    // Active Calls (mock)
    const elCalls = document.getElementById('active-calls');
    if (elCalls) elCalls.textContent = "0";
}

/**
 * Populate customers table
 */
function populateCustomersTable(customers) {
    const tbody = document.getElementById('customers-tbody');
    if (!tbody) return;

    // Preserve current selections if refreshing? 
    // For simplicity, we just rebuild. Ideally we'd map customerId -> selectedAgent.
    // Given the requirement, resetting to default (first agent) is acceptable for now per "default selected".

    tbody.innerHTML = '';

    if (customers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-5">
                    <p class="mb-0">No active accounts found.</p>
                </td>
            </tr>
        `;
        return;
    }

    customers.forEach(customer => {
        const row = createCustomerRow(customer, availableAgents);
        tbody.appendChild(row);
    });
}

// --- CRUD Functions ---

const customerModal = new bootstrap.Modal(document.getElementById('customerModal'));
const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
let deleteCustomerId = null;

function openCreateModal() {
    document.getElementById('customerForm').reset();
    document.getElementById('customerId').value = '';
    document.getElementById('customerStatus').value = 'active';
    document.getElementById('customerRisk').value = 'medium';
    document.getElementById('customerModalTitle').textContent = 'New Customer';
    customerModal.show();
}

function openEditModal(customer) {
    document.getElementById('customerId').value = customer.id;
    document.getElementById('customerName').value = customer.name;
    document.getElementById('customerPhone').value = customer.phone;
    document.getElementById('customerDebt').value = customer.debt_amount;
    document.getElementById('customerDueDate').value = customer.due_date || ''; // Handle null due_date
    document.getElementById('customerStatus').value = customer.status;
    document.getElementById('customerRisk').value = customer.risk_level;
    document.getElementById('customerModalTitle').textContent = 'Edit Customer';
    customerModal.show();
}

async function saveCustomer() {
    const id = document.getElementById('customerId').value;
    const customer = {
        name: document.getElementById('customerName').value,
        phone: document.getElementById('customerPhone').value,
        debt_amount: parseFloat(document.getElementById('customerDebt').value),
        due_date: document.getElementById('customerDueDate').value || null,
        status: document.getElementById('customerStatus').value,
        risk_level: document.getElementById('customerRisk').value
    };

    if (!customer.name || !customer.phone || isNaN(customer.debt_amount)) {
        alert('Please fill in required fields (Name, Phone, Debt Amount)');
        return;
    }

    try {
        const url = id ? `${API_BASE_URL}/api/customers/${id}` : `${API_BASE_URL}/api/customers`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(customer)
        });

        if (response.ok) {
            customerModal.hide();
            loadCustomers(); // Refresh list
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail || 'Unknown error occurred'}`);
        }
    } catch (e) {
        console.error('Error saving customer:', e);
        alert('Failed to save customer due to network error.');
    }
}

function confirmDelete(id) {
    deleteCustomerId = id;
    deleteModal.show();
}

// --- Row Creation Update ---

/**
 * Creates a table row element for a customer.
 */
function createCustomerRow(customer, availableAgents) {
    const row = document.createElement('tr');
    row.className = "align-middle"; // Vertically center content

    // Customer Name & Phone
    const nameCell = document.createElement('td');
    nameCell.className = "ps-4"; // Left padding to match header
    nameCell.innerHTML = `
        <div class="fw-medium text-dark">${escapeHtml(customer.name)}</div>
        <div class="text-secondary small">${formatPhoneNumber(customer.phone)}</div>
    `;
    row.appendChild(nameCell);

    // Contact Status (Icon + Text) - This is a new column, distinct from the main 'Status'
    const contactStatusCell = document.createElement('td');
    contactStatusCell.innerHTML = getContactStatusBadge(customer.status); // Helper function below
    row.appendChild(contactStatusCell);

    // Debt Amount
    const debtCell = document.createElement('td');
    debtCell.className = "fw-medium";
    debtCell.textContent = formatCurrency(customer.debt_amount);
    row.appendChild(debtCell);

    // Status Column (The main status like 'active', 'promised_to_pay')
    const statusTextCell = document.createElement('td');
    statusTextCell.textContent = formatStatus(customer.status);
    row.appendChild(statusTextCell);

    // Risk Column
    const riskCell = document.createElement('td');
    riskCell.appendChild(createRiskBadge(customer.risk_level));
    row.appendChild(riskCell);

    // Aging (Days Overdue)
    const agingCell = document.createElement('td');
    if (customer.due_date) {
        const days = calculateDaysOverdue(customer.due_date);
        agingCell.innerHTML = `<span class="${days > 30 ? 'text-danger fw-medium' : 'text-secondary'}">${days} days</span>`;
    } else {
        agingCell.textContent = "-";
    }
    row.appendChild(agingCell);

    // Last Action
    const lastActionCell = document.createElement('td');
    const lastDate = customer.last_call_date || customer.updated_at;
    if (lastDate) {
        lastActionCell.innerHTML = `<small class="text-secondary">${formatDate(lastDate)}</small>`;
    } else {
        lastActionCell.textContent = "-";
    }
    row.appendChild(lastActionCell);

    // AGENT SELECTION COLUMN
    const agentCell = document.createElement('td');
    const agentSelect = document.createElement('select');
    agentSelect.className = 'form-select form-select-sm agent-select';
    agentSelect.id = `agent-select-${customer.id}`;
    agentSelect.style.width = '140px';

    if (availableAgents.length > 0) {
        availableAgents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent.agent_id;
            option.textContent = agent.name;
            agentSelect.appendChild(option);
        });
        // Set selected agent if customer has one, otherwise default to first
        if (customer.assigned_agent_id) {
            agentSelect.value = customer.assigned_agent_id;
        }
    } else {
        const option = document.createElement('option');
        option.textContent = "Loading...";
        agentSelect.appendChild(option);
    }

    agentCell.appendChild(agentSelect);
    row.appendChild(agentCell);

    // Action Buttons (Call + Edit + Delete)
    const actionCell = document.createElement('td');
    actionCell.className = "text-end pe-4";

    // Wrapper for buttons
    const btnGroup = document.createElement('div');
    btnGroup.className = "d-flex justify-content-end gap-2";

    // Call Button
    const callButton = document.createElement('button');
    callButton.className = 'btn btn-sm btn-action-call d-flex align-items-center';
    callButton.innerHTML = '<i class="bi bi-telephone-fill me-1"></i> Call';
    callButton.title = "Inject Call";
    callButton.onclick = () => {
        const selectedAgentId = document.getElementById(`agent-select-${customer.id}`).value;
        initiateCall(customer, selectedAgentId);
    };
    btnGroup.appendChild(callButton);

    // Edit Button
    const editButton = document.createElement('button');
    editButton.className = 'btn btn-sm btn-outline-secondary';
    editButton.innerHTML = '<i class="bi bi-pencil"></i>';
    editButton.title = "Edit";
    editButton.onclick = () => openEditModal(customer);
    btnGroup.appendChild(editButton);

    // Delete Button
    const deleteButton = document.createElement('button');
    deleteButton.className = 'btn btn-sm btn-outline-danger';
    deleteButton.innerHTML = '<i class="bi bi-trash"></i>';
    deleteButton.title = "Delete";
    deleteButton.onclick = () => confirmDelete(customer.id);
    btnGroup.appendChild(deleteButton);

    actionCell.appendChild(btnGroup);
    row.appendChild(actionCell);

    return row;
}

// Helper to format status text nice
function formatStatus(status) {
    if (!status) return '-';
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Helper to format phone number
function formatPhoneNumber(phoneNumber) {
    if (!phoneNumber) return '';
    // Basic formatting for 10-digit numbers
    const cleaned = ('' + phoneNumber).replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3];
    }
    return phoneNumber; // Return original if not 10 digits
}

// Helper to format currency
function formatCurrency(amount) {
    if (typeof amount !== 'number') return '-';
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Helper to calculate days overdue
function calculateDaysOverdue(dueDateString) {
    if (!dueDateString) return 0;
    const dueDate = new Date(dueDateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize today to start of day
    dueDate.setHours(0, 0, 0, 0); // Normalize due date to start of day

    if (dueDate >= today) {
        return 0; // Not overdue yet
    }

    const diffTime = Math.abs(today.getTime() - dueDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

/**
 * Create a badge for the 'Contact Status' column
 */
function getContactStatusBadge(status) {
    let iconClass = '';
    let textClass = '';
    let tooltip = '';

    switch (status) {
        case 'active':
            iconClass = 'bi bi-check-circle-fill text-success';
            textClass = 'text-success';
            tooltip = 'Active Account';
            break;
        case 'promised_to_pay':
            iconClass = 'bi bi-hourglass-split text-warning';
            textClass = 'text-warning';
            tooltip = 'Promised to Pay';
            break;
        case 'refused':
            iconClass = 'bi bi-x-circle-fill text-danger';
            textClass = 'text-danger';
            tooltip = 'Refused to Pay';
            break;
        case 'callback_requested':
            iconClass = 'bi bi-arrow-repeat text-info';
            textClass = 'text-info';
            tooltip = 'Callback Requested';
            break;
        case 'voicemail':
            iconClass = 'bi bi-mic-fill text-secondary';
            textClass = 'text-secondary';
            tooltip = 'Left Voicemail';
            break;
        case 'wrong_number':
            iconClass = 'bi bi-exclamation-triangle-fill text-muted';
            textClass = 'text-muted';
            tooltip = 'Wrong Number';
            break;
        default:
            iconClass = 'bi bi-question-circle-fill text-muted';
            textClass = 'text-muted';
            tooltip = 'Unknown Status';
            break;
    }

    return `
        <span class="d-inline-flex align-items-center" data-bs-toggle="tooltip" data-bs-placement="top" title="${tooltip}">
            <i class="${iconClass} me-1"></i>
            <span class="small ${textClass}">${formatStatus(status)}</span>
        </span>
    `;
}

/**
 * Create status badge (original function, used for the 'Status' column)
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

    const statusInfo = statusMap[status] || { text: status, class: 'badge-wrong-number' };
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
        'low': { text: 'Low', class: 'badge-active' }, // Reusing active/success color for low risk
        'medium': { text: 'Medium', class: 'badge-promised' }, // Reusing warning color
        'high': { text: 'High', class: 'badge-refused' } // Reusing danger color
    };

    const riskInfo = riskMap[riskLevel] || { text: riskLevel, class: 'badge-wrong-number' };
    badge.innerHTML = `<i class="bi bi-circle-fill" style="font-size: 6px; vertical-align: middle; margin-right: 4px;"></i> ${riskInfo.text}`;
    badge.classList.add(riskInfo.class);

    return badge;
}

/**
 * Initiate call to customer
 */
async function initiateCall(customer, agentId) {
    console.log('Initiating call to:', customer.name, customer.phone, 'Agent:', agentId);

    // Show modal
    callModal.show();

    // Reset modal state
    const elLoading = document.getElementById('call-loading');
    const elConversation = document.getElementById('call-conversation');
    const elCompleted = document.getElementById('call-completed');
    const elError = document.getElementById('call-error');

    if (elLoading) elLoading.classList.remove('d-none');
    if (elConversation) elConversation.classList.add('d-none');
    if (elCompleted) elCompleted.classList.add('d-none');
    if (elError) elError.classList.add('d-none');

    // Set customer info
    const elName = document.getElementById('call-customer-name');
    if (elName) elName.textContent = customer.name;

    try {
        const response = await fetch(`${API_BASE_URL}/api/call`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone: customer.phone,
                agent_id: agentId // Pass the selected agent
            })
        });

        const result = await response.json();

        // Hide loading
        if (elLoading) elLoading.classList.add('d-none');

        if (response.ok && result.success) {
            // Show "Conversation in progress"
            if (elConversation) elConversation.classList.remove('d-none');

            const logDiv = document.getElementById('conversation-log');
            if (logDiv) {
                // Find agent name for display
                const agentName = availableAgents.find(a => a.agent_id === agentId)?.name || "Agent";

                logDiv.innerHTML = `<div class="text-muted small">Connecting to ${agentName}...</div>`;
                setTimeout(() => {
                    logDiv.innerHTML += `<div class="mt-2"><strong>${agentName}:</strong> Hello, this is ${agentName} from GenuVoice.</div>`;
                }, 1000);
            }

            // Reload customers
            setTimeout(() => {
                loadCustomers();
            }, 2000);

        } else {
            // Show error
            if (elError) elError.classList.remove('d-none');
            const elMsg = document.getElementById('error-message');
            if (elMsg) elMsg.textContent = result.message || 'Unknown error occurred';
        }

    } catch (error) {
        console.error('Error initiating call:', error);

        // Hide loading, show error
        if (elLoading) elLoading.classList.add('d-none');
        if (elError) elError.classList.remove('d-none');

        const elMsg = document.getElementById('error-message');
        if (elMsg) elMsg.textContent = `Network error: ${error.message}`;
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
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
