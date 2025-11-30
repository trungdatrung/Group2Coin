import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/travel',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request/response interceptors for debugging
api.interceptors.response.use(
  (response) => {
    console.log('Travel API Response:', response.config.url, response.data);
    return response;
  },
  (error) => {
    console.error('Travel API Error:', error.config?.url, error.message);
    return Promise.reject(error);
  }
);

export const travelAPI = {
  // Tours
  listTours: () => api.get('/tours'),
  getTour: (tourId) => api.get(`/tours/${tourId}`),
  createTour: (tourData) => api.post('/admin/tour/create', tourData),
  updateTour: (tourId, updates) => api.put(`/admin/tour/${tourId}/update`, updates),
  getAdminTours: (adminAddress) => api.get(`/admin/tours/${adminAddress}`),
  
  // Bookings
  createBooking: (bookingData) => api.post('/booking/create', bookingData),
  confirmBooking: (bookingId, paymentTxHash) => 
    api.post(`/booking/${bookingId}/confirm`, { payment_tx_hash: paymentTxHash }),
  cancelBooking: (bookingId, refundTxHash) => 
    api.post(`/booking/${bookingId}/cancel`, { refund_tx_hash: refundTxHash }),
  getUserBookings: (userAddress) => api.get(`/user/bookings/${userAddress}`),
  getAdminBookings: (adminAddress) => api.get(`/admin/bookings/${adminAddress}`),
  
  // Reviews
  addReview: (reviewData) => api.post('/review/add', reviewData),
  getReviews: (tourId) => api.get(`/reviews/${tourId}`),
  
  // Stats
  getAdminStats: (adminAddress) => api.get(`/admin/stats/${adminAddress}`),
};

export default api;
