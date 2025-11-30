import React, { useState, useEffect } from 'react';
import { travelAPI } from '../services/travel';
import './TourManagement.css';

function TourManagement({ wallet }) {
  const [activeTab, setActiveTab] = useState('create');
  const [tours, setTours] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    price: 100,
    start_date: '',
    end_date: '',
    max_participants: 10,
    duration_days: 3,
    itinerary: [],
  });

  useEffect(() => {
    if (wallet && wallet.address) {
      loadAdminData();
    }
  }, [wallet]);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      const [toursRes, bookingsRes, statsRes] = await Promise.all([
        travelAPI.getAdminTours(wallet.address),
        travelAPI.getAdminBookings(wallet.address),
        travelAPI.getAdminStats(wallet.address),
      ]);
      console.log('Admin tours:', toursRes.data);
      console.log('Admin bookings:', bookingsRes.data);
      console.log('Admin stats:', statsRes.data);
      setTours(toursRes.data.tours || []);
      setBookings(bookingsRes.data.bookings || []);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading admin data:', error);
    }
    setLoading(false);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleCreateTour = async (e) => {
    e.preventDefault();
    if (!wallet || !wallet.address) {
      alert('Please load a wallet first');
      return;
    }

    try {
      await travelAPI.createTour({
        ...formData,
        admin_address: wallet.address,
        price: parseFloat(formData.price),
        max_participants: parseInt(formData.max_participants),
        duration_days: parseInt(formData.duration_days),
      });
      alert('Tour created successfully!');
      setFormData({
        title: '',
        description: '',
        location: '',
        price: 100,
        start_date: '',
        end_date: '',
        max_participants: 10,
        duration_days: 3,
        itinerary: [],
      });
      loadAdminData();
    } catch (error) {
      console.error('Error creating tour:', error);
      alert('Failed to create tour');
    }
  };

  return (
    <div className="tour-management">
      {!wallet || !wallet.address ? (
        <div className="empty-state">
          <p>Please create or load a wallet first to access admin panel</p>
          <p className="hint">Go to the Wallet tab to get started</p>
        </div>
      ) : (
        <>
          <div className="management-header">
            <h2>Tour Management (Admin)</h2>
            {wallet && <p>Logged in as: {wallet.address?.substring(0, 20)}...</p>}
          </div>

          {stats && (
            <div className="stats-dashboard">
              <div className="stat-box">
                <div className="stat-label">Total Tours</div>
                <div className="stat-value">{stats.total_tours}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Total Bookings</div>
                <div className="stat-value">{stats.total_bookings}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Total Revenue</div>
                <div className="stat-value">{stats.total_revenue} G2C</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Completed Tours</div>
                <div className="stat-value">{stats.completed_tours}</div>
              </div>
            </div>
          )}

          <div className="tabs">
            <button
              className={`tab-button ${activeTab === 'create' ? 'active' : ''}`}
              onClick={() => setActiveTab('create')}
            >
              Create Tour
            </button>
            <button
              className={`tab-button ${activeTab === 'tours' ? 'active' : ''}`}
              onClick={() => setActiveTab('tours')}
            >
              My Tours ({tours.length})
            </button>
            <button
              className={`tab-button ${activeTab === 'bookings' ? 'active' : ''}`}
              onClick={() => setActiveTab('bookings')}
            >
              Bookings ({bookings.length})
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'create' && (
              <form onSubmit={handleCreateTour} className="create-tour-form">
            <div className="form-group">
              <label>Tour Title</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleFormChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleFormChange}
                rows="4"
                required
              ></textarea>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Price (G2C)</label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleFormChange}
                  min="1"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Start Date</label>
                <input
                  type="date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>End Date</label>
                <input
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleFormChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Max Participants</label>
                <input
                  type="number"
                  name="max_participants"
                  value={formData.max_participants}
                  onChange={handleFormChange}
                  min="1"
                  required
                />
              </div>

              <div className="form-group">
                <label>Duration (days)</label>
                <input
                  type="number"
                  name="duration_days"
                  value={formData.duration_days}
                  onChange={handleFormChange}
                  min="1"
                  required
                />
              </div>
            </div>

            <button type="submit" className="submit-button">
              Create Tour
            </button>
              </form>
            )}

            {activeTab === 'tours' && (
              <div className="tours-list">
                {tours.length === 0 ? (
                  <p>No tours created yet</p>
                ) : (
                  tours.map((tour) => (
                    <div key={tour.tour_id} className="tour-item">
                      <div className="tour-item-header">
                        <h3>{tour.title}</h3>
                        <span className={`status ${tour.is_active ? 'active' : 'inactive'}`}>
                          {tour.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <p className="location">{tour.location}</p>
                      <div className="tour-stats">
                        <span>Bookings: {tour.bookings_count}/{tour.max_participants}</span>
                        <span>Revenue: {tour.total_revenue} G2C</span>
                        <span>Price: {tour.price} G2C</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'bookings' && (
              <div className="bookings-list">
                {bookings.length === 0 ? (
                  <p>No bookings yet</p>
                ) : (
                  bookings.map((item, idx) => (
                    <div key={idx} className="booking-item">
                      <div className="booking-header">
                        <h4>{item.tour?.title}</h4>
                        <span className={`booking-status ${item.booking.status}`}>
                          {item.booking.status}
                        </span>
                      </div>
                      <div className="booking-details">
                        <span>User: {item.booking.user_address?.substring(0, 20)}...</span>
                        <span>Participants: {item.booking.num_participants}</span>
                        <span>Total: {item.booking.total_price} G2C</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default TourManagement;
