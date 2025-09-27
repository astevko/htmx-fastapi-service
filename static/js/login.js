// HTMX FastAPI Service - Login Timezone Detection
// This script handles browser timezone detection for login
(function () {
    'use strict';

    // Detect browser timezone immediately (before DOM is ready)
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Configure HTMX to include timezone in login requests
    document.addEventListener('htmx:configRequest', function (evt) {
        if (evt.detail.verb === 'post' && evt.detail.path === '/api/login') {
            evt.detail.parameters.user_timezone = timezone;
        }
    });

    // Handle successful login redirect
    document.addEventListener('htmx:afterRequest', function (evt) {
        if (evt.detail.xhr.status === 200 && evt.detail.path === '/api/login') {
            // Check if the response contains a redirect instruction
            const response = evt.detail.xhr.responseText;
            if (response.includes('redirect') || response.includes('success')) {
                // Redirect to messages page
                window.location.href = '/msgs';
            }
        }
    });

    // Export timezone for debugging if needed
    window.detectedTimezone = timezone;
})();
