import React, { useState } from 'react';
import { travelAPI } from '../services/travel';
import './BookingForm.css';

function BookingForm({ tour, wallet, onClose, onSuccess }) {
  const [numParticipants, setNumParticipants] = useState(1);
  const [specialRequests, setSpecialRequests] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('form'); // form, confirm, payment, success

  const totalPrice = numParticipants * tour.price;

  const handleCreateBooking = async () => {
    if (!wallet || !wallet.address) {
      alert('Please create or load a wallet first');
      return;
    }

    if (numParticipants < 1 || numParticipants > tour.available_spots) {
      alert(`Please select between 1 and ${tour.available_spots} participants`);
      return;
    }

    try {
      setLoading(true);
      const response = await travelAPI.createBooking({
        tour_id: tour.tour_id,
        user_address: wallet.address,
        num_participants: numParticipants,
        special_requests: specialRequests,
      });

      if (response.data.booking) {
        setStep('confirm');
      }
    } catch (error) {
      console.error('Error creating booking:', error);
      alert('Failed to create booking');
    }
    setLoading(false);
  };

  return (
    <div className="booking-form-modal">
      <div className="modal-overlay" onClick={onClose}></div>
      <div className="booking-modal-content">
        <button className="close-button" onClick={onClose}>✕</button>

        {step === 'form' && (
          <>
            <h2>Book Your Tour</h2>
            <div className="booking-summary">
              <div className="summary-item">
                <span>Tour:</span>
                <strong>{tour.title}</strong>
              </div>
              <div className="summary-item">
                <span>Price per person:</span>
                <strong>{tour.price} G2C</strong>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="participants">Number of Participants:</label>
              <input
                type="number"
                id="participants"
                min="1"
                max={tour.available_spots}
                value={numParticipants}
                onChange={(e) => setNumParticipants(Math.max(1, parseInt(e.target.value) || 1))}
              />
              <small>Available: {tour.available_spots} spots</small>
            </div>

            <div className="form-group">
              <label htmlFor="requests">Special Requests (optional):</label>
              <textarea
                id="requests"
                value={specialRequests}
                onChange={(e) => setSpecialRequests(e.target.value)}
                placeholder="Any special requirements or preferences?"
                rows="4"
              />
            </div>

            <div className="total-price">
              <span>Total Cost:</span>
              <strong>{totalPrice} G2C</strong>
            </div>

            <button
              className="submit-button"
              onClick={handleCreateBooking}
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Continue to Payment'}
            </button>
          </>
        )}

        {step === 'confirm' && (
          <div className="confirmation">
            <h2>Booking Confirmed!</h2>
            <p>Your booking has been created and is pending payment.</p>
            <p>You will need to process the payment from your wallet to finalize the booking.</p>
            <button className="close-button-alt" onClick={onClose}>
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default BookingForm;
