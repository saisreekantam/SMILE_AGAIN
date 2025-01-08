# chat/__init__.py
from typing import Optional
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Socket.IO with CORS settings
socketio = SocketIO(
    cors_allowed_origins=["http://localhost:3000"],
    logger=True,
    engineio_logger=True,
    async_mode='eventlet'
)

class ChatSystemManager:
    """
    Manages the chat system initialization and configuration
    """
    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize the chat system manager
        
        Args:
            app: Optional Flask application instance
        """
        self.app = app
        self.socketio = socketio
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize the chat system with a Flask application
        
        Args:
            app: Flask application instance
        """
        try:
            # Register blueprints and configure routes
            from .routes import create_chat_blueprint
            chat_bp = create_chat_blueprint()
            
            # Configure CORS for chat endpoints
            CORS(chat_bp, resources={
                r"/chats/*": {
                    "origins": ["http://localhost:3000"],
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"],
                    "supports_credentials": True,
                    "max_age": 3600
                }
            })
            
            # Register blueprint with prefix
            app.register_blueprint(chat_bp, url_prefix='/chats')
            
            # Initialize Socket.IO
            self.socketio.init_app(
                app,
                cors_allowed_origins="http://localhost:3000",
                message_queue='redis://'  # Optional: Redis for message queue
            )
            
            # Register error handlers
            self._register_error_handlers(app)
            
            logger.info("Chat system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize chat system: {str(e)}")
            raise

    def _register_error_handlers(self, app: Flask) -> None:
        """
        Register error handlers for the chat system
        
        Args:
            app: Flask application instance
        """
        @app.errorhandler(404)
        def not_found_error(error):
            return {'error': 'Resource not found'}, 404

        @app.errorhandler(500)
        def internal_error(error):
            return {'error': 'Internal server error'}, 500

def create_chat_system(app: Flask = None) -> ChatSystemManager:
    """
    Create and configure the chat system
    
    Args:
        app: Optional Flask application instance
        
    Returns:
        ChatSystemManager: Configured chat system manager
    """
    chat_system = ChatSystemManager(app)
    return chat_system