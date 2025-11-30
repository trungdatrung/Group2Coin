"""
Main Flask application entry point for Group2Coin blockchain
"""
from flask import Flask
from flask_cors import CORS
from blockchain.blockchain import Blockchain
from api.routes import api, init_routes
from travel.routes import travel_api, init_travel_routes
from travel.manager import TravelManager


def create_app():
    """
    Create and configure Flask application
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/travel/*": {"origins": "*"}})
    
    blockchain = Blockchain(difficulty=4, mining_reward=50)
    travel_manager = TravelManager()
    
    init_routes(blockchain)
    init_travel_routes(travel_manager)
    
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(travel_api, url_prefix='/travel')
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print("=" * 50)
    print("Group2Coin Blockchain Server")
    print("=" * 50)
    print("Server starting on http://localhost:5000")
    print("API endpoints available at http://localhost:5000/api")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
