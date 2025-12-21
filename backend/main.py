"""
Main Flask application entry point for Group2Coin blockchain
"""
from flask import Flask
from flask_cors import CORS
from services.node_service import NodeService
from api.routes import api, init_routes


def create_app():
    """
    Create and configure Flask application
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Node Service (Singleton for the application)
    node_service = NodeService()
    
    init_routes(node_service)
    
    app.register_blueprint(api, url_prefix='/api')
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print("=" * 50)
    print("Group2Coin Blockchain Server")
    print("=" * 50)
    print("Server starting on http://localhost:5001")
    print("API endpoints available at http://localhost:5001/api")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
