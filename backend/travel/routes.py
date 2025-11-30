"""
Travel and Tour Management API Routes
"""
from flask import Blueprint, jsonify, request
from travel.manager import TravelManager

travel_api = Blueprint('travel', __name__)

# Global travel manager instance
travel_manager = None

def init_travel_routes(tm):
    """Initialize travel manager"""
    global travel_manager
    travel_manager = tm


# ============================================
# ADMIN ROUTES (Tour Creation & Management)
# ============================================

@travel_api.route('/admin/tour/create', methods=['POST'])
def create_tour():
    """Create a new tour (admin only)"""
    try:
        data = request.get_json()
        
        required = ['title', 'description', 'location', 'price', 'start_date', 'end_date',
                   'max_participants', 'admin_address', 'duration_days']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        tour = travel_manager.create_tour(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            price=data['price'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            max_participants=data['max_participants'],
            admin_address=data['admin_address'],
            duration_days=data['duration_days'],
            itinerary=data.get('itinerary', [])
        )
        
        return jsonify({
            'message': 'Tour created successfully',
            'tour': tour.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/admin/tour/<tour_id>/update', methods=['PUT'])
def update_tour(tour_id):
    """Update tour details (admin only)"""
    try:
        tour = travel_manager.get_tour(tour_id)
        if not tour:
            return jsonify({'error': 'Tour not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            tour.title = data['title']
        if 'description' in data:
            tour.description = data['description']
        if 'price' in data:
            tour.price = data['price']
        if 'is_active' in data:
            tour.is_active = data['is_active']
        if 'itinerary' in data:
            tour.itinerary = data['itinerary']
        
        return jsonify({
            'message': 'Tour updated successfully',
            'tour': tour.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/admin/tours/<admin_address>', methods=['GET'])
def get_admin_tours(admin_address):
    """Get all tours created by an admin"""
    try:
        tours = travel_manager.get_admin_tours(admin_address)
        stats = travel_manager.get_admin_stats(admin_address)
        
        return jsonify({
            'tours': [t.to_dict() for t in tours],
            'count': len(tours),
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/admin/bookings/<admin_address>', methods=['GET'])
def get_admin_bookings(admin_address):
    """Get all bookings for admin's tours"""
    try:
        admin_tours = travel_manager.get_admin_tours(admin_address)
        all_bookings = []
        
        for tour in admin_tours:
            for booking_id in tour.bookings:
                booking = travel_manager.get_booking(booking_id)
                if booking:
                    all_bookings.append({
                        'booking': booking.to_dict(),
                        'tour': tour.to_dict()
                    })
        
        return jsonify({
            'bookings': all_bookings,
            'total_bookings': len(all_bookings)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/admin/stats/<admin_address>', methods=['GET'])
def get_admin_stats(admin_address):
    """Get admin statistics"""
    try:
        stats = travel_manager.get_admin_stats(admin_address)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# USER ROUTES (Browsing & Booking)
# ============================================

@travel_api.route('/tours', methods=['GET'])
def list_tours():
    """List all active tours"""
    try:
        tours = travel_manager.list_tours(active_only=True)
        return jsonify({
            'tours': [t.to_dict() for t in tours],
            'total': len(tours)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/tours/<tour_id>', methods=['GET'])
def get_tour(tour_id):
    """Get tour details and reviews"""
    try:
        tour = travel_manager.get_tour(tour_id)
        if not tour:
            return jsonify({'error': 'Tour not found'}), 404
        
        reviews = travel_manager.get_tour_reviews(tour_id)
        avg_rating = (sum(r.rating for r in reviews) / len(reviews)) if reviews else 0
        
        return jsonify({
            'tour': tour.to_dict(),
            'reviews': [r.to_dict() for r in reviews],
            'average_rating': avg_rating,
            'review_count': len(reviews)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/booking/create', methods=['POST'])
def create_booking():
    """Create a booking (pending payment)"""
    try:
        data = request.get_json()
        
        required = ['tour_id', 'user_address', 'num_participants']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        booking, message = travel_manager.create_booking(
            tour_id=data['tour_id'],
            user_address=data['user_address'],
            num_participants=data['num_participants'],
            special_requests=data.get('special_requests', '')
        )
        
        if not booking:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'message': message,
            'booking': booking.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/booking/<booking_id>/confirm', methods=['POST'])
def confirm_booking(booking_id):
    """Confirm booking after payment"""
    try:
        data = request.get_json()
        payment_tx = data.get('payment_tx_hash')
        
        if not payment_tx:
            return jsonify({'error': 'payment_tx_hash required'}), 400
        
        success, message = travel_manager.confirm_booking(booking_id, payment_tx)
        
        if not success:
            return jsonify({'error': message}), 400
        
        booking = travel_manager.get_booking(booking_id)
        tour = travel_manager.get_tour(booking.tour_id)
        tour.total_revenue += booking.total_price
        
        return jsonify({
            'message': message,
            'booking': booking.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/booking/<booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        data = request.get_json()
        refund_tx = data.get('refund_tx_hash')
        
        success, message = travel_manager.cancel_booking(booking_id, refund_tx)
        
        if not success:
            return jsonify({'error': message}), 400
        
        booking = travel_manager.get_booking(booking_id)
        return jsonify({
            'message': message,
            'booking': booking.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/user/bookings/<user_address>', methods=['GET'])
def get_user_bookings(user_address):
    """Get all bookings for a user"""
    try:
        bookings = travel_manager.get_user_bookings(user_address)
        
        booking_details = []
        for booking in bookings:
            tour = travel_manager.get_tour(booking.tour_id)
            booking_details.append({
                'booking': booking.to_dict(),
                'tour': tour.to_dict() if tour else None
            })
        
        return jsonify({
            'bookings': booking_details,
            'total': len(bookings)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# REVIEW ROUTES
# ============================================

@travel_api.route('/review/add', methods=['POST'])
def add_review():
    """Add a review for a completed tour"""
    try:
        data = request.get_json()
        
        required = ['tour_id', 'user_address', 'booking_id', 'rating', 'comment']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        review = travel_manager.add_review(
            tour_id=data['tour_id'],
            user_address=data['user_address'],
            booking_id=data['booking_id'],
            rating=data['rating'],
            comment=data['comment']
        )
        
        return jsonify({
            'message': 'Review added successfully',
            'review': review.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@travel_api.route('/reviews/<tour_id>', methods=['GET'])
def get_reviews(tour_id):
    """Get all reviews for a tour"""
    try:
        reviews = travel_manager.get_tour_reviews(tour_id)
        avg_rating = (sum(r.rating for r in reviews) / len(reviews)) if reviews else 0
        
        return jsonify({
            'reviews': [r.to_dict() for r in reviews],
            'average_rating': avg_rating,
            'total_reviews': len(reviews)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
