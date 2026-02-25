"""
Firebase Manager for ACTN State Management
Handles all Firebase Firestore operations for the trading system.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from google.cloud import firestore
from google.cloud.exceptions import GoogleCloudError
import firebase_admin
from firebase_admin import credentials, firestore

from actn_config import config

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Manages all Firebase Firestore operations for ACTN"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            try:
                self._initialize_firebase()
                self._initialized = True
                logger.info("Firebase Manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                raise
    
    def _initialize_firebase(self):
        """Initialize Firebase connection with error handling"""
        try:
            if not firebase_admin._apps:
                if config.is_production:
                    cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH)
                else:
                    # Use emulator for development
                    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
                    cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH) if os.path.exists(config.FIREBASE_CREDENTIALS_PATH) else credentials.ApplicationDefault()
                
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self._test_connection()
            
        except FileNotFoundError as e:
            logger.error(f"Firebase credentials file not found: {e}")
            raise
        except GoogleCloudError as e:
            logger.error(f"Google Cloud error during Firebase init: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing Firebase: {e}")
            raise
    
    def _test_connection(self):
        """Test Firebase connection by writing and reading a test document"""
        test_ref = self.db.collection("system_health").document("connection_test")
        test_data = {
            "timestamp": datetime.utcnow(),
            "status": "testing",
            "config_env": config.is_production
        }
        
        test_ref.set(test_data)
        doc = test_ref.get()
        
        if not doc.exists:
            raise ConnectionError("Failed to verify Firebase write operation")
        
        test_ref.delete()
        logger.debug("Firebase connection test successful")
    
    def save_trading_signal(self, signal: Dict[str, Any]) -> str:
        """
        Save a trading signal to Firestore with comprehensive metadata
        
        Args:
            signal: Dictionary containing signal data
            
        Returns:
            Document ID of the saved signal
            
        Raises:
            ValueError: If signal is missing required fields
            GoogleCloudError: If Firebase operation fails
        """
        required_fields = ["signal_type", "asset", "confidence", "timestamp"]
        missing = [field for field in required_fields if field not in signal]
        
        if missing:
            raise ValueError(f"Signal missing required fields: {missing}")
        
        try:
            # Add metadata
            signal["processed_at"] = datetime.utcnow()
            signal["system_version"] = "actn_v1.0"
            signal["environment"] = "production" if config.is_production else "development"
            
            # Store in Firestore
            signals_ref = self.db.collection("trading_signals")
            doc_ref = signals_ref.add(signal)
            
            logger.info(f