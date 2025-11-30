import React, { useState, useEffect } from 'react';
import { travelAPI } from '../services/travel';
import Reviews from './Reviews';
import './MyBookings.css';

function MyBookings({ wallet }) {
  const [bookings, setBookings] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);
  const [showReviewTourId, setShowReviewTourId] = useState(null);

  useEffect(() => {
    if (wallet?.address) {
      loadUserBookings();
    } else {
      setLoading(false);
    }
  }, [wallet?.address]);

  const loadUserBookings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await travelAPI.getUserBookings(wallet.address);
      setBookings(response.data.bookings || []);
    } catch (error) {
      console.error('Error loading bookings:', error);
      setError(error.message || 'Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return;
    }

    try {
      await travelAPI.cancelBooking(bookingId);
      alert('Booking cancelled successfully');
      loadUserBookings();
    } catch (error) {
      console.error('Error cancelling booking:', error);
      alert('Failed to cancel booking');
    }
  };

  const getFilteredBookings = () => {
    if (filter === 'all') return bookings;
    return bookings.filter((item) => item.booking.status === filter);
  };

  const filteredBookings = getFilteredBookings();

  const getStatusColor = (status) => {
    const colors = {
      pending: '#FFA500',
      confirmed: '#4CAF50',
      completed: '#2196F3',
      cancelled: '#f44336',
    };
    return colors[status] || '#999';
  };

  if (!wallet?.address) {
    return (
      <div className="my-bookings">
        <div className="empty-state">
          <p>Please create or load a wallet first to view your bookings</p>
          <p className="hint">Go to the Wallet tab to get started</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="my-bookings">
        <div className="bookings-header">
          <h2>My Bookings</h2>
          <p className="wallet-info">Account: {wallet.address.substring(0, 30)}...</p>
        </div>
        <div className="loading">Loading your bookings...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-bookings">
        <div className="bookings-header">
          <h2>My Bookings</h2>
          <p className="wallet-info">Account: {wallet.address.substring(0, 30)}...</p>
        </div>
        <div className="error-message">
          <p>Error: {error}</p>
          <button className="refresh-btn" onClick={loadUserBookings}>Try Again</button>
        </div>
      </div>
    );
  }

  return (
    <div className="my-bookings">
      <div className="bookings-header">
        <h2>My Bookings</h2>
        {wallet && (
          <p className="wallet-info">Account: {wallet.address?.substring(0, 30)}...</p>
        )}
      </div>

      <div className="filter-buttons">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({bookings.length})
        </button>
        <button
          className={`filter-btn ${filter === 'pending' ? 'active' : ''}`}
          onClick={() => setFilter('pending')}
        >
          Pending ({bookings.filter((b) => b.booking.status === 'pending').length})
        </button>
        <button
          className={`filter-btn ${filter === 'confirmed' ? 'active' : ''}`}
          onClick={() => setFilter('confirmed')}
        >
          Confirmed ({bookings.filter((b) => b.booking.status === 'confirmed').length})
        </button>
        <button
          className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
          onClick={() => setFilter('completed')}
        >
          Completed ({bookings.filter((b) => b.booking.status === 'completed').length})
        </button>
      </div>

      <div className="bookings-container">
        {loading ? (
          <p className="loading">Loading your bookings...</p>
        ) : filteredBookings.length === 0 ? (
          <div className="empty-state">
            <p>No bookings found</p>
            <p className="hint">
              {filter === 'all'
                ? 'Start by booking a tour to see it here'
                : `No ${filter} bookings at this time`}
            </p>
          </div>
        ) : (
          filteredBookings.map((item) => (
            <div
              key={item.booking.booking_id}
              className={`booking-card ${item.booking.status}`}
            >
              <div className="booking-card-header">
                <div className="booking-title-section">
                  <h3>{item.tour.title}</h3>
                  <p className="booking-location">{item.tour.location}</p>
                </div>
                <div
                  className="booking-status-badge"
                  style={{ backgroundColor: getStatusColor(item.booking.status) }}
                >
                  {item.booking.status.toUpperCase()}
                </div>
              </div>

              <div className="booking-summary">
                <span className="summary-item">
                  <strong>Booking ID:</strong> {item.booking.booking_id?.substring(0, 12)}...
                </span>
                <span className="summary-item">
                  <strong>Date:</strong>{' '}
                  {new Date(item.tour.start_date).toLocaleDateString()}
                </span>
                <span className="summary-item">
                  <strong>Participants:</strong> {item.booking.num_participants}
                </span>
                <span className="summary-item">
                  <strong>Total Price:</strong> {item.booking.total_price} G2C
                </span>
              </div>

              <button
                className="expand-button"
                onClick={() =>
                  setExpandedId(
                    expandedId === item.booking.booking_id ? null : item.booking.booking_id
                  )
                }
              >
                {expandedId === item.booking.booking_id ? '▲ Hide Details' : '▼ Show Details'}
              </button>

              {expandedId === item.booking.booking_id && (
                <div className="booking-details-expanded">
                  <div className="detail-section">
                    <h4>Tour Information</h4>
                    <div className="tour-info">
                      <p>
                        <strong>Description:</strong> {item.tour.description}
                      </p>
                      <p>
                        <strong>Duration:</strong> {item.tour.duration_days} days
                      </p>
                      <p>
                        <strong>Start Date:</strong>{' '}
                        {new Date(item.tour.start_date).toLocaleDateString()}
                      </p>
                      <p>
                        <strong>End Date:</strong>{' '}
                        {new Date(item.tour.end_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {item.tour.itinerary && item.tour.itinerary.length > 0 && (
                    <div className="detail-section">
                      <h4>Itinerary</h4>
                      <ul className="itinerary-list">
                        {item.tour.itinerary.map((day, idx) => (
                          <li key={idx}>{day}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="detail-section">
                    <h4>Booking Details</h4>
                    <div className="booking-info">
                      <p>
                        <strong>Booking Date:</strong>{' '}
                        {new Date(item.booking.created_at).toLocaleDateString()}
                      </p>
                      <p>
                        <strong>Special Requests:</strong>{' '}
                        {item.booking.special_requests || 'None'}
                      </p>
                      <p>
                        <strong>Price per Person:</strong> {item.tour.price} G2C
                      </p>
                      <p>
                        <strong>Total Price:</strong>{' '}
                        <span className="price-highlight">{item.booking.total_price} G2C</span>
                      </p>
                    </div>
                  </div>

                  {item.booking.blockchain_tx_hash && (
                    <div className="detail-section">
                      <h4>Payment Confirmation</h4>
                      <div className="tx-info">
                        <p>
                          <strong>Transaction Hash:</strong>
                          <br />
                          <code>{item.booking.blockchain_tx_hash}</code>
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="booking-actions">
                    {item.booking.status === 'pending' && (
                      <button
                        className="action-button cancel-btn"
                        onClick={() => handleCancelBooking(item.booking.booking_id)}
                      >
                        Cancel Booking
                      </button>
                    )}
                    {item.booking.status === 'completed' && (
                      <button
                        className="action-button review-btn"
                        onClick={() => setShowReviewTourId(item.tour.tour_id)}
                      >
                        Leave a Review
                      </button>
                    )}
                  </div>

                  {showReviewTourId === item.tour.tour_id && (
                    <div className="review-modal-wrapper">
                      <div className="review-modal-overlay"></div>
                      <div className="review-modal">
                        <button
                          className="close-review"
                          onClick={() => setShowReviewTourId(null)}
                        >
                          ✕
                        </button>
                        <Reviews tourId={item.tour.tour_id} />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default MyBookings;
