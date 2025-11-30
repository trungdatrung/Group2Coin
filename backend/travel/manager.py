"""
Travel and Tour Management Models
"""
from datetime import datetime
import uuid


class Tour:
    """Represents a travel tour/package"""
    
    def __init__(self, title, description, location, price, start_date, end_date, 
                 max_participants, admin_address, duration_days, itinerary=None):
        """
        Initialize a tour
        
        Args:
            title: Tour name
            description: Detailed description
            location: Destination
            price: Price in G2C (blockchain currency)
            start_date: Tour start date (ISO format string)
            end_date: Tour end date (ISO format string)
            max_participants: Maximum bookings allowed
            admin_address: Wallet address of admin creating the tour
            duration_days: Number of days
            itinerary: List of daily activities
        """
        self.tour_id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.location = location
        self.price = price
        self.start_date = start_date
        self.end_date = end_date
        self.max_participants = max_participants
        self.admin_address = admin_address
        self.duration_days = duration_days
        self.itinerary = itinerary or []
        self.created_at = datetime.now().isoformat()
        self.is_active = True
        self.bookings = []  # List of booking IDs
        self.total_revenue = 0  # In G2C
    
    def to_dict(self):
        """Convert tour to dictionary"""
        return {
            'tour_id': self.tour_id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'price': self.price,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'max_participants': self.max_participants,
            'admin_address': self.admin_address,
            'duration_days': self.duration_days,
            'itinerary': self.itinerary,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'bookings_count': len(self.bookings),
            'available_spots': self.max_participants - len(self.bookings),
            'total_revenue': self.total_revenue
        }


class Booking:
    """Represents a tour booking by a user"""
    
    def __init__(self, tour_id, user_address, num_participants, special_requests=None):
        """
        Initialize a booking
        
        Args:
            tour_id: ID of the tour being booked
            user_address: Wallet address of the person booking
            num_participants: Number of people in this booking
            special_requests: Any special requests/notes
        """
        self.booking_id = str(uuid.uuid4())
        self.tour_id = tour_id
        self.user_address = user_address
        self.num_participants = num_participants
        self.special_requests = special_requests or ""
        self.created_at = datetime.now().isoformat()
        self.status = "pending"  # pending, confirmed, completed, cancelled
        self.payment_tx_hash = None  # Blockchain transaction hash
        self.total_price = 0  # Will be calculated
        self.refund_tx_hash = None  # If refunded
    
    def to_dict(self):
        """Convert booking to dictionary"""
        return {
            'booking_id': self.booking_id,
            'tour_id': self.tour_id,
            'user_address': self.user_address,
            'num_participants': self.num_participants,
            'special_requests': self.special_requests,
            'created_at': self.created_at,
            'status': self.status,
            'payment_tx_hash': self.payment_tx_hash,
            'total_price': self.total_price,
            'refund_tx_hash': self.refund_tx_hash
        }


class Review:
    """Represents a user review of a completed tour"""
    
    def __init__(self, tour_id, user_address, booking_id, rating, comment):
        """
        Initialize a review
        
        Args:
            tour_id: ID of the tour being reviewed
            user_address: Wallet address of reviewer
            booking_id: Associated booking ID
            rating: Rating 1-5
            comment: Review text
        """
        self.review_id = str(uuid.uuid4())
        self.tour_id = tour_id
        self.user_address = user_address
        self.booking_id = booking_id
        self.rating = max(1, min(5, rating))  # Clamp 1-5
        self.comment = comment
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert review to dictionary"""
        return {
            'review_id': self.review_id,
            'tour_id': self.tour_id,
            'user_address': self.user_address[:20] + '...' if len(self.user_address) > 20 else self.user_address,
            'booking_id': self.booking_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at
        }


class TravelManager:
    """Manages all tours, bookings, and reviews"""
    
    def __init__(self):
        self.tours = {}  # tour_id -> Tour
        self.bookings = {}  # booking_id -> Booking
        self.reviews = {}  # review_id -> Review
        self.user_bookings = {}  # user_address -> [booking_ids]
    
    def create_tour(self, title, description, location, price, start_date, end_date,
                   max_participants, admin_address, duration_days, itinerary=None):
        """Create a new tour (admin only)"""
        tour = Tour(title, description, location, price, start_date, end_date,
                   max_participants, admin_address, duration_days, itinerary)
        self.tours[tour.tour_id] = tour
        return tour
    
    def get_tour(self, tour_id):
        """Get tour by ID"""
        return self.tours.get(tour_id)
    
    def list_tours(self, active_only=True):
        """List all tours"""
        tours = list(self.tours.values())
        if active_only:
            tours = [t for t in tours if t.is_active]
        return tours
    
    def create_booking(self, tour_id, user_address, num_participants, special_requests=None):
        """Create a booking for a user"""
        tour = self.get_tour(tour_id)
        if not tour:
            return None, "Tour not found"
        
        if not tour.is_active:
            return None, "Tour is not active"
        
        available = tour.max_participants - len(tour.bookings)
        if num_participants > available:
            return None, f"Not enough spots. Available: {available}"
        
        booking = Booking(tour_id, user_address, num_participants, special_requests)
        booking.total_price = num_participants * tour.price
        
        self.bookings[booking.booking_id] = booking
        tour.bookings.append(booking.booking_id)
        
        if user_address not in self.user_bookings:
            self.user_bookings[user_address] = []
        self.user_bookings[user_address].append(booking.booking_id)
        
        return booking, "Booking created"
    
    def get_booking(self, booking_id):
        """Get booking by ID"""
        return self.bookings.get(booking_id)
    
    def confirm_booking(self, booking_id, payment_tx_hash):
        """Confirm booking after payment"""
        booking = self.get_booking(booking_id)
        if not booking:
            return False, "Booking not found"
        
        booking.status = "confirmed"
        booking.payment_tx_hash = payment_tx_hash
        return True, "Booking confirmed"
    
    def cancel_booking(self, booking_id, refund_tx_hash=None):
        """Cancel a booking"""
        booking = self.get_booking(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.status == "cancelled":
            return False, "Booking already cancelled"
        
        tour = self.get_tour(booking.tour_id)
        if tour and booking.booking_id in tour.bookings:
            tour.bookings.remove(booking.booking_id)
        
        booking.status = "cancelled"
        booking.refund_tx_hash = refund_tx_hash
        return True, "Booking cancelled"
    
    def complete_booking(self, booking_id):
        """Mark booking as completed after tour"""
        booking = self.get_booking(booking_id)
        if not booking:
            return False, "Booking not found"
        
        booking.status = "completed"
        return True, "Booking completed"
    
    def add_review(self, tour_id, user_address, booking_id, rating, comment):
        """Add a review for a tour"""
        review = Review(tour_id, user_address, booking_id, rating, comment)
        self.reviews[review.review_id] = review
        return review
    
    def get_tour_reviews(self, tour_id):
        """Get all reviews for a tour"""
        return [r for r in self.reviews.values() if r.tour_id == tour_id]
    
    def get_user_bookings(self, user_address):
        """Get all bookings for a user"""
        booking_ids = self.user_bookings.get(user_address, [])
        return [self.get_booking(bid) for bid in booking_ids]
    
    def get_admin_tours(self, admin_address):
        """Get all tours created by an admin"""
        return [t for t in self.tours.values() if t.admin_address == admin_address]
    
    def get_admin_stats(self, admin_address):
        """Get stats for an admin"""
        tours = self.get_admin_tours(admin_address)
        total_bookings = sum(len(t.bookings) for t in tours)
        total_revenue = sum(t.total_revenue for t in tours)
        completed_tours = sum(1 for t in tours if not t.is_active)
        
        return {
            'total_tours': len(tours),
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'completed_tours': completed_tours
        }
