"""
Main Flask application entry point for Group2Coin blockchain
"""
from flask import Flask
from flask_cors import CORS
from blockchain.blockchain import Blockchain
from api.routes import api, init_routes


def create_app():
    """
    Create and configure Flask application
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    blockchain = Blockchain(difficulty=4, mining_reward=50)
    
    init_routes(blockchain)
    
    app.register_blueprint(api, url_prefix='/api')
    
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
