/* Search functionality with live filtering */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value;
            if (query.length > 2) {
                fetch(`/api/facilities?q=${encodeURIComponent(query)}`)
                    .then(r => r.json())
                    .then(data => console.log('Search results:', data.length));
            }
        }, 300));
    }
});