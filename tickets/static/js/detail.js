/**
 * datastraw CRM - Ticket Detail Workspace Script
 * Handles asynchronous status changes and note creation via the REST API.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Read context variables passed from template
    const ticketId = window.ticketId;
    const csrfToken = window.csrfToken;

    if (!ticketId) return;

    // Elements
    const statusSelector = document.getElementById('statusSelector');
    const updateStatusBtn = document.getElementById('updateStatusBtn');
    const statusAlert = document.getElementById('statusAlert');
    const ticketStatusPill = document.getElementById('ticketStatusPill');
    const ticketUpdatedAt = document.getElementById('ticketUpdatedAt');

    const notesTimeline = document.getElementById('notesTimeline');
    const emptyTimelineState = document.getElementById('emptyTimelineState');
    const newNoteText = document.getElementById('newNoteText');
    const submitNoteBtn = document.getElementById('submitNoteBtn');
    const noteAlert = document.getElementById('noteAlert');
    const charCount = document.getElementById('charCount');

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

    // Initialize character counter
    if (newNoteText && charCount) {
        newNoteText.addEventListener('input', (e) => {
            const count = e.target.value.length;
            charCount.textContent = `${count} character${count === 1 ? '' : 's'}`;
        });
    }

    // 1. UPDATE STATUS HANDLER
    if (updateStatusBtn && statusSelector) {
        updateStatusBtn.addEventListener('click', async () => {
            const selectedStatus = statusSelector.value;
            
            // Visual feedback: disable controls
            updateStatusBtn.disabled = true;
            statusSelector.disabled = true;
            statusAlert.classList.add('hidden');

            try {
                const response = await fetch(`/api/tickets/${ticketId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ status: selectedStatus })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to update status');
                }

                // Update UI status pill
                ticketStatusPill.className = `status-pill status-${selectedStatus.toLowerCase().replace(' ', '_')}`;
                ticketStatusPill.textContent = selectedStatus;

                // Update updated_at timestamp
                if (data.updated_at) {
                    ticketUpdatedAt.textContent = formatLocalDate(data.updated_at);
                }

                // Show success feedback
                statusAlert.classList.remove('hidden');
                setTimeout(() => {
                    statusAlert.classList.add('hidden');
                }, 3000);

            } catch (error) {
                alert(`Error: ${error.message}`);
            } finally {
                updateStatusBtn.disabled = false;
                statusSelector.disabled = false;
            }
        });
    }

    // 2. SUBMIT NOTE HANDLER
    if (submitNoteBtn && newNoteText) {
        submitNoteBtn.addEventListener('click', async () => {
            const noteContent = newNoteText.value.trim();
            
            if (!noteContent) {
                showNoteAlert('Note text cannot be empty.', 'error');
                return;
            }

            // Visual feedback: disable controls
            submitNoteBtn.disabled = true;
            newNoteText.disabled = true;
            hideNoteAlert();

            try {
                const response = await fetch(`/api/tickets/${ticketId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ notes: noteContent })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to add note');
                }

                // Reset inputs
                newNoteText.value = '';
                charCount.textContent = '0 characters';

                // Update updated_at timestamp
                if (data.updated_at) {
                    ticketUpdatedAt.textContent = formatLocalDate(data.updated_at);
                }

                // Dynamic rendering of the new note in timeline
                appendNoteToTimeline(noteContent, new Date().toISOString());

            } catch (error) {
                showNoteAlert(`Error: ${error.message}`, 'error');
            } finally {
                submitNoteBtn.disabled = false;
                newNoteText.disabled = false;
            }
        });
    }

    // Append a new note block to timeline programmatically
    function appendNoteToTimeline(text, isoDate) {
        // Remove empty state if visible
        if (emptyTimelineState) {
            emptyTimelineState.remove();
        }

        const noteHTML = `
            <div class="timeline-item">
                <div class="timeline-badge">
                    <i class="fa-solid fa-user-pen"></i>
                </div>
                <div class="timeline-card">
                    <div class="timeline-header">
                        <span class="timeline-author">Agent Note</span>
                        <span class="timeline-time">${formatLocalDate(isoDate)}</span>
                    </div>
                    <div class="timeline-body">
                        <p>${escapeHTML(text).replace(/\n/g, '<br>')}</p>
                    </div>
                </div>
            </div>
        `;

        // Insert at the bottom of the timeline
        notesTimeline.insertAdjacentHTML('beforeend', noteHTML);
        
        // Scroll timeline to the bottom
        notesTimeline.scrollTop = notesTimeline.scrollHeight;
    }

    // Alert functions for Note Submission
    function showNoteAlert(msg, type) {
        noteAlert.textContent = msg;
        noteAlert.className = `alert alert-${type} mt-2`;
    }

    function hideNoteAlert() {
        noteAlert.textContent = '';
        noteAlert.className = 'alert alert-error mt-2 hidden';
    }

    // Localize any static timestamps
    document.querySelectorAll('[data-utc]').forEach(el => {
        const utcStr = el.getAttribute('data-utc');
        if (utcStr) {
            el.textContent = formatLocalDate(utcStr);
        }
    });
});
