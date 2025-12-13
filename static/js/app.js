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
        const row = createCustomerRow(customer);
        tbody.appendChild(row);
    });
}

/**
 * Create a table row for a customer
 */
function createCustomerRow(customer) {
    const row = document.createElement('tr');

    // Name
    const nameCell = document.createElement('td');
    nameCell.className = "ps-4";
    nameCell.innerHTML = `
        <div class="customer-name">${escapeHtml(customer.name)}</div>
        <div class="small text-muted d-md-none">${escapeHtml(customer.phone)}</div>
    `;
    row.appendChild(nameCell);

    // Phone
    const phoneCell = document.createElement('td');
    phoneCell.innerHTML = `<span class="customer-phone">${escapeHtml(customer.phone)}</span>`;
    row.appendChild(phoneCell);

    // Debt Amount
    const debtCell = document.createElement('td');
    debtCell.innerHTML = `<span class="debt-amount">$${customer.debt_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>`;
    row.appendChild(debtCell);

    // Status
    const statusCell = document.createElement('td');
    statusCell.appendChild(createStatusBadge(customer.status));
    row.appendChild(statusCell);

    // Aging / Overdue
    const overdueCell = document.createElement('td');
    let overdueClass = 'overdue-low';
    if (customer.days_overdue > 30) overdueClass = 'overdue-high';
    else if (customer.days_overdue > 7) overdueClass = 'overdue-med';

    overdueCell.innerHTML = `<span class="${overdueClass}">${customer.days_overdue} days</span>`;
    row.appendChild(overdueCell);

    // Last Call
    const lastCallCell = document.createElement('td');
    lastCallCell.innerHTML = customer.last_call_date ?
        `<span class="text-muted small">${formatDate(customer.last_call_date)}</span>` :
        `<span class="text-muted small">-</span>`;
    row.appendChild(lastCallCell);

    // AGENT SELECTION COLUMN
    const agentCell = document.createElement('td');
    const agentSelect = document.createElement('select');
    agentSelect.className = 'form-select form-select-sm agent-select';
    agentSelect.id = `agent-select-${customer.id}`; // unique ID
    agentSelect.style.width = '140px';

    // Populate dropdown
    if (availableAgents.length > 0) {
        availableAgents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent.agent_id;
            option.textContent = agent.name;
            agentSelect.appendChild(option);
        });
        // First one selected by default (browser behavior)
    } else {
        const option = document.createElement('option');
        option.textContent = "Loading...";
        agentSelect.appendChild(option);
    }

    agentCell.appendChild(agentSelect);
    row.appendChild(agentCell);

    // Action Button
    const actionCell = document.createElement('td');
    actionCell.className = "text-end pe-4";
    const callButton = document.createElement('button');
    callButton.className = 'btn-call-action';
    callButton.innerHTML = '<i class="bi bi-telephone-fill me-1"></i> Call';

    // Pass the customer AND the specific selector ID to the call function
    callButton.onclick = () => {
        const selectedAgentId = document.getElementById(`agent-select-${customer.id}`).value;
        initiateCall(customer, selectedAgentId);
    };

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

    const statusInfo = statusMap[status] || { text: status, class: 'badge-wrong-number' };
    badge.textContent = statusInfo.text;
    badge.classList.add(statusInfo.class);

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
