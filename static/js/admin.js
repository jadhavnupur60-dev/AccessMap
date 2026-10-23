/* Admin panel functionality */
function updateReportStatus(reportId, status) {
    apiCall(`/api/report/${reportId}`, 'PUT', { status: status })
        .then(data => {
            if (data.success) {
                showNotification('Report updated!', 'success');
                setTimeout(() => location.reload(), 1000);
            }
        });
}

function showNotification(message, type) {
    const div = document.createElement('div');
    div.className = `flash flash-${type}`;
    div.textContent = message;
    document.querySelector('.flash-container')?.appendChild(div) ||
        document.body.insertBefore(div, document.body.firstChild);
    setTimeout(() => div.remove(), 3000);
}