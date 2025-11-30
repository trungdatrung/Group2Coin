import React, { useState, useEffect } from 'react';
import { travelAPI } from '../services/travel';
import BookingForm from './BookingForm';
import Reviews from './Reviews';
import './TourListing.css';

function TourListing({ wallet }) {
  const [tours, setTours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTour, setSelectedTour] = useState(null);

  useEffect(() => {
    loadTours();
  }, []);

  const loadTours = async () => {
    try {
      setLoading(true);
      const response = await travelAPI.listTours();
      console.log('Tours API Response:', response.data);
      setTours(response.data.tours || []);
    } catch (error) {
      console.error('Error loading tours:', error);
      setTours([]);
      alert('Failed to load tours: ' + (error.message || 'Unknown error'));
    }
    setLoading(false);
  };

  if (loading) {
    return <div className="tour-listing"><div className="loading">Loading tours...</div></div>;
  }

  if (!tours || tours.length === 0) {
    return <div className="tour-listing"><div className="no-tours">No tours available</div></div>;
  }

  return (
    <div className="tour-listing">
      <div className="listing-header">
        <h2>Explore Tours</h2>
        <p>Find and book your next adventure</p>
        <button className="refresh-btn" onClick={loadTours}>🔄 Refresh</button>
      </div>

      <div className="tours-grid">
        {tours.map((tour) => (
          <div
            key={tour.tour_id}
            className="tour-card"
            onClick={() => setSelectedTour(tour)}
          >
            <div className="tour-card-header">
              <h3>{tour.title}</h3>
              <span className="location-badge">{tour.location}</span>
            </div>
            <div className="tour-card-details">
              <p className="description">{tour.description.substring(0, 100)}...</p>
              <div className="tour-meta">
                <span className="duration">📅 {tour.duration_days} days</span>
                <span className="price">{tour.price} G2C</span>
              </div>
              <div className="availability">
                <span className="spots">Available: {tour.available_spots} / {tour.max_participants}</span>
              </div>
            </div>
            <button className="view-button">View Details</button>
          </div>
        ))}
      </div>

      {selectedTour && (
        <TourDetail tour={selectedTour} wallet={wallet} onClose={() => setSelectedTour(null)} />
      )}
    </div>
  );
}

function TourDetail({ tour, wallet, onClose }) {
  const [showBooking, setShowBooking] = useState(false);

  return (
    <div className="tour-detail-modal">
      <div className="modal-overlay" onClick={onClose}></div>
      <div className="modal-content">
        <button className="close-button" onClick={onClose}>✕</button>
        
        <div className="detail-header">
          <h2>{tour.title}</h2>
          <div className="tour-info">
            <span className="badge location">{tour.location}</span>
            <span className="badge duration">{tour.duration_days} days</span>
            <span className="price-large">{tour.price} G2C per person</span>
          </div>
        </div>

        <div className="detail-body">
          <section>
            <h3>About this tour</h3>
            <p>{tour.description}</p>
          </section>

          {tour.itinerary && tour.itinerary.length > 0 && (
            <section>
              <h3>Itinerary</h3>
              <ul className="itinerary-list">
                {tour.itinerary.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </section>
          )}

          <section>
            <h3>Tour Details</h3>
            <div className="details-grid">
              <div>
                <strong>Start Date:</strong> {new Date(tour.start_date).toLocaleDateString()}
              </div>
              <div>
                <strong>End Date:</strong> {new Date(tour.end_date).toLocaleDateString()}
              </div>
              <div>
                <strong>Available Spots:</strong> {tour.available_spots} / {tour.max_participants}
              </div>
              <div>
                <strong>Total Bookings:</strong> {tour.bookings_count}
              </div>
            </div>
          </section>

          <Reviews tourId={tour.tour_id} />
        </div>

        <div className="detail-footer">
          {tour.available_spots > 0 ? (
            <button className="book-button" onClick={() => setShowBooking(true)}>
              Book Now
            </button>
          ) : (
            <button className="book-button disabled" disabled>
              No spots available
            </button>
          )}
        </div>

        {showBooking && (
          <BookingForm tour={tour} wallet={wallet} onClose={() => setShowBooking(false)} />
        )}
      </div>
    </div>
  );
}

export default TourListing;
