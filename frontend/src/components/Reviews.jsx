import React, { useState, useEffect } from 'react';
import { travelAPI } from '../services/travel';
import './Reviews.css';

function Reviews({ tourId, onClose }) {
  const [reviews, setReviews] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    user_address: '',
    rating: 5,
    comment: '',
  });

  useEffect(() => {
    loadReviews();
  }, [tourId]);

  const loadReviews = async () => {
    try {
      setLoading(true);
      const response = await travelAPI.getReviews(tourId);
      setReviews(response.data.reviews || []);
    } catch (error) {
      console.error('Error loading reviews:', error);
    }
    setLoading(false);
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();

    if (!formData.user_address) {
      alert('Please enter your wallet address');
      return;
    }

    if (!formData.comment.trim()) {
      alert('Please write a comment');
      return;
    }

    try {
      await travelAPI.addReview({
        tour_id: tourId,
        user_address: formData.user_address,
        rating: parseInt(formData.rating),
        comment: formData.comment,
      });

      alert('Review submitted successfully!');
      setFormData({ user_address: '', rating: 5, comment: '' });
      setShowForm(false);
      loadReviews();
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Failed to submit review');
    }
  };

  const getStarRating = (rating) => {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating);
  };

  const getAverageRating = () => {
    if (reviews.length === 0) return 0;
    const total = reviews.reduce((sum, r) => sum + r.rating, 0);
    return (total / reviews.length).toFixed(1);
  };

  return (
    <div className="reviews-section">
      <div className="reviews-header">
        <h3>Customer Reviews</h3>
        {reviews.length > 0 && (
          <div className="rating-summary">
            <span className="stars">{getStarRating(Math.round(getAverageRating()))}</span>
            <span className="rating-value">{getAverageRating()}</span>
            <span className="review-count">({reviews.length} reviews)</span>
          </div>
        )}
      </div>

      {!showForm && (
        <button className="write-review-btn" onClick={() => setShowForm(true)}>
          Write a Review
        </button>
      )}

      {showForm && (
        <form className="review-form" onSubmit={handleSubmitReview}>
          <div className="form-group">
            <label>Your Wallet Address</label>
            <input
              type="text"
              value={formData.user_address}
              onChange={(e) =>
                setFormData({ ...formData, user_address: e.target.value })
              }
              placeholder="Your wallet address"
              required
            />
          </div>

          <div className="form-group">
            <label>Rating (1-5 stars)</label>
            <div className="rating-input">
              {[1, 2, 3, 4, 5].map((num) => (
                <button
                  key={num}
                  type="button"
                  className={`star ${formData.rating >= num ? 'active' : ''}`}
                  onClick={() => setFormData({ ...formData, rating: num })}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Your Comment</label>
            <textarea
              value={formData.comment}
              onChange={(e) =>
                setFormData({ ...formData, comment: e.target.value })
              }
              placeholder="Share your experience with this tour..."
              rows="5"
              required
            ></textarea>
          </div>

          <div className="form-actions">
            <button type="submit" className="submit-btn">
              Submit Review
            </button>
            <button
              type="button"
              className="cancel-btn"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="reviews-list">
        {loading ? (
          <p className="loading">Loading reviews...</p>
        ) : reviews.length === 0 ? (
          <p className="no-reviews">No reviews yet. Be the first to review!</p>
        ) : (
          reviews.map((review, idx) => (
            <div key={idx} className="review-item">
              <div className="review-header">
                <span className="stars">{getStarRating(review.rating)}</span>
                <span className="reviewer">
                  {review.user_address?.substring(0, 15)}...
                </span>
              </div>
              <p className="review-comment">{review.comment}</p>
              <span className="review-date">
                {new Date(review.created_at).toLocaleDateString()}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Reviews;
