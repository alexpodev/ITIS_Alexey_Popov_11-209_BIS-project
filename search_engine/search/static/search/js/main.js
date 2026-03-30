// Main JavaScript for vector search web interface

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results');

    // Focus search input on page load
    if (searchInput) {
        searchInput.focus();
    }

    // Handle HTMX events for better UX
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        if (evt.detail.elt.classList.contains('search-form')) {
            resultsContainer.classList.add('loading');
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.classList.contains('search-form')) {
            resultsContainer.classList.remove('loading');
        }
    });

    // Allow Enter key to submit search
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const form = this.closest('form');
                if (form) {
                    htmx.trigger(form, 'submit');
                }
            }
        });
    }
});
