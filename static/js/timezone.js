// HTMX FastAPI Service - Timezone Detection and Configuration
// This script handles browser timezone detection and HTMX configuration

(function () {
    'use strict';

    // Detect browser timezone immediately (before DOM is ready)
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Configure HTMX to include timezone in all requests (except the initial load)
    document.addEventListener('htmx:configRequest', function (evt) {
        if (evt.detail.verb === 'post') {
            evt.detail.parameters.user_timezone = timezone;
        }
    });

    // Add timezone info and update initial load URL when DOM is ready
    document.addEventListener('DOMContentLoaded', function () {
        // Update the refresh button to include timezone
        const refreshButton = document.getElementById('refresh-button');
        if (refreshButton) {
            refreshButton.setAttribute('hx-get', `/api/messages?user_timezone=${encodeURIComponent(timezone)}`);
        }

        // Add timezone info to the page
        const timezoneInfo = document.createElement('div');
        timezoneInfo.className = 'text-sm text-gray-200 text-center mb-4';
        timezoneInfo.textContent = `Timezone: ${timezone}`;

        const container = document.querySelector('.max-w-2xl');
        if (container) {
            container.insertBefore(timezoneInfo, container.firstChild);
        }

        // Trigger the initial load with the timezone parameter
        htmx.ajax('GET', `/api/messages?user_timezone=${encodeURIComponent(timezone)}`, {
            target: '#messages-container',
            swap: 'innerHTML'
        });
    });

    // Export timezone for debugging if needed
    window.detectedTimezone = timezone;
})();
