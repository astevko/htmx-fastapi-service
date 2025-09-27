// HTMX FastAPI Service - Timezone Detection and Configuration
// This script handles browser timezone detection and HTMX configuration
// Now uses cookies for timezone management
(function () {
    'use strict';

    // Get timezone from cookie or detect it
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    const timezone = getCookie('user_timezone') || Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Configure HTMX to include timezone in all requests
    document.addEventListener('htmx:configRequest', function (evt) {
        if (evt.detail.verb === 'post') {
            evt.detail.parameters.user_timezone = timezone;
        }
    });

    // Add timezone info and update initial load when DOM is ready
    document.addEventListener('DOMContentLoaded', function () {
        // Update the refresh button
        const refreshButton = document.getElementById('refresh-button');
        if (refreshButton) {
            refreshButton.setAttribute('hx-get', '/api/messages');
        }

        // Add timezone info to the page
        const timezoneInfo = document.createElement('div');
        timezoneInfo.className = 'text-sm text-gray-200 text-center mb-4';
        timezoneInfo.textContent = `Timezone: ${timezone}`;

        const container = document.querySelector('.max-w-2xl');
        if (container) {
            container.insertBefore(timezoneInfo, container.firstChild);
        }

        // Trigger the initial load
        htmx.ajax('GET', '/api/messages', {
            target: '#messages-container',
            swap: 'innerHTML'
        });
    });

    // Export timezone for debugging if needed
    window.detectedTimezone = timezone;
})();
