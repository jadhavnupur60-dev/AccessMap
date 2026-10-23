/* Reviews functionality */
function submitReview(facilityId, rating, comment) {
    return apiCall(`/api/reviews/${facilityId}`, 'POST', {
        rating: rating,
        comment: comment
    });
}