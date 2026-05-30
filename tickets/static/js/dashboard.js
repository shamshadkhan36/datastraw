/**
 * datastraw CRM - Dashboard Workspace Script
 * Handles real-time search-as-you-type and status filtering via the REST API.
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const filterPills = document.querySelectorAll('.filter-pill');
    const tableBody = document.getElementById('ticketsTableBody');
    
    // State variables
    let currentSearch = '';
    let currentStatus = '';
    let debounceTimer = null;

    // Helper to format ISO dates to a clean local format
    function formatLocalDate(isoString) {
        if (!isoString) return '';
        try {
            const date = new Date(isoString);
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            });
        } catch (e) {
            return isoString;
        }
    }

    // Helper to escape regex special characters
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Helper to highlight matching text
    function highlightText(text, searchWord) {
        if (!searchWord || !text) return text;
        try {
            const regex = new RegExp(`(${escapeRegExp(searchWord)})`, 'gi');
            return text.replace(regex, '<mark class="search-highlight">$1</mark>');
        } catch (e) {
            return text;
        }
    }

    // Main fetch and render function
    async function fetchTickets() {
        // Build API URL
        const params = new URLSearchParams();
        if (currentStatus) params.append('status', currentStatus);
        if (currentSearch) params.append('search', currentSearch);
        
        const url = `/api/tickets?${params.toString()}`;
        
        try {
            // Visual feedback: show table opacity transition
            tableBody.style.opacity = '0.5';
            
            const response = await fetch(url);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const tickets = await response.json();
            
            // Render tickets
            renderTicketsTable(tickets);
            updateStatsCounters(tickets);
        } catch (error) {
            console.error('Error fetching tickets:', error);
            tableBody.innerHTML = `
                <tr class="error-state-row">
                    <td colspan="6">
                        <div class="empty-state">
                            <i class="fa-solid fa-triangle-exclamation" style="color: #f87171;"></i>
                            <h3>Failed to load tickets</h3>
                            <p>An error occurred while connecting to the server. Please try again later.</p>
                        </div>
                    </td>
                </tr>
            `;
        } finally {
            tableBody.style.opacity = '1';
        }
    }

    // Render table rows dynamically based on tickets JSON data
    function renderTicketsTable(tickets) {
        if (tickets.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-state-row">
                    <td colspan="6">
                        <div class="empty-state">
                            <i class="fa-solid fa-folder-open empty-icon"></i>
                            <h3>No matching tickets</h3>
                            <p>No results found for status "${currentStatus || 'All'}" matching "${currentSearch}".</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = tickets.map(ticket => {
            const statusLower = ticket.status.toLowerCase().replace(' ', '_');
            const safeSubject = escapeHTML(ticket.subject);
            const highlightedSubject = highlightText(safeSubject, currentSearch);
            const safeName = escapeHTML(ticket.customer_name);
            const highlightedName = highlightText(safeName, currentSearch);
            const safeEmail = escapeHTML(ticket.customer_email);
            const highlightedEmail = highlightText(safeEmail, currentSearch);
            const safeId = escapeHTML(ticket.ticket_id);
            const highlightedId = highlightText(safeId, currentSearch);
            
            return `
                <tr class="ticket-row" data-id="${ticket.ticket_id}" onclick="window.location.href='/tickets/${ticket.ticket_id}/'">
                    <td class="col-id">
                        <span class="ticket-id-tag">#${highlightedId}</span>
                    </td>
                    <td class="col-customer">
                        <div class="customer-info-cell">
                            <span class="customer-name">${highlightedName}</span>
                            <span class="customer-email">${highlightedEmail}</span>
                        </div>
                    </td>
                    <td class="col-subject">
                        <div class="subject-cell">
                            <span class="ticket-subject">${highlightedSubject}</span>
                            <span class="ticket-desc-excerpt">${escapeHTML(ticket.subject)}</span>
                        </div>
                    </td>
                    <td class="col-status">
                        <span class="status-pill status-${statusLower}">${ticket.status}</span>
                    </td>
                    <td class="col-date">
                        <span class="ticket-date">${formatLocalDate(ticket.created_at)}</span>
                    </td>
                    <td class="col-actions">
                        <a href="/tickets/${ticket.ticket_id}/" class="action-btn-view" onclick="event.stopPropagation();">
                            <i class="fa-solid fa-arrow-right-to-bracket"></i>
                        </a>
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Dynamic stats updater
    // Note: When filtering, we update the current counts shown in dashboard dynamically if it's "All" status.
    function updateStatsCounters(tickets) {
        if (!currentSearch && !currentStatus) {
            // If showing everything, recalculate stats count cards
            const total = tickets.length;
            const open = tickets.filter(t => t.status === 'Open').length;
            const progress = tickets.filter(t => t.status === 'In Progress').length;
            const closed = tickets.filter(t => t.status === 'Closed').length;

            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-open').textContent = open;
            document.getElementById('stat-progress').textContent = progress;
            document.getElementById('stat-closed').textContent = closed;
        }
    }

    // Escapes special HTML tags to prevent XSS
    function escapeHTML(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Listeners for Search
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value.trim();
        
        // Show/hide clear button
        if (currentSearch.length > 0) {
            clearSearchBtn.classList.add('visible');
        } else {
            clearSearchBtn.classList.remove('visible');
        }

        // Debounce search query
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchTickets();
        }, 250);
    });

    // Clear search action
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        currentSearch = '';
        clearSearchBtn.classList.remove('visible');
        fetchTickets();
        searchInput.focus();
    });

    // Listeners for Filter Pills
    filterPills.forEach(pill => {
        pill.addEventListener('click', (e) => {
            // Remove active class from others
            filterPills.forEach(p => p.classList.remove('active'));
            // Add active class to current
            pill.classList.add('active');
            
            currentStatus = pill.getAttribute('data-status');
            fetchTickets();
        });
    });

    // Convert static date stamps on page load to local timezone
    document.querySelectorAll('.ticket-date').forEach(el => {
        const utcStr = el.getAttribute('data-utc');
        if (utcStr) {
            el.textContent = formatLocalDate(utcStr);
        }
    });
});
