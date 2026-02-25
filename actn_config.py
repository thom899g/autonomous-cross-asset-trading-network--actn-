"""
ACTN Configuration and Constants
Centralized configuration management for the Autonomous Cross-Asset Trading Network.
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# Asset classes supported by ACTN
class AssetClass(Enum):
    CRYPTO = "crypto"
    EQUITIES = "equities"
    FOREX = "forex"
    COMMODITIES = "commodities"
    BONDS = "bonds"

# Trading signals from alternative data
class SignalType(Enum):
    SATELLITE = "satellite"
    SOCIAL_SENTIMENT = "social_sentiment"
    IOT_SUPPLY_CHAIN = "iot_supply_chain"
    TRADITIONAL_TECHNICAL = "traditional_technical"

@dataclass
class ACTNConfig:
    """Main configuration container for ACTN"""
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "actn-trading-system")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS", "./firebase_credentials.json")
    
    # Trading Parameters
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio per trade
    MAX_DAILY_LOSS_PCT: float = 0.02  # 2% max daily loss
    MIN_CONFIDENCE_THRESHOLD: float = 0.65  # Minimum confidence to execute
    
    # Data Source Configuration
    SATELLITE_DATA_ENDPOINT: str = os.getenv("SATELLITE_ENDPOINT", "")
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    IOT_DATA_STREAM: str = os.getenv("IOT_STREAM_URL", "")
    
    # DeFi Integration
    DEFI_PROTOCOLS: List[str] = None
    DEFAULT_DEX: str = "uniswap_v3"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_FIREBASE: bool = True
    
    def __post_init__(self):
        if self.DEFI_PROTOCOLS is None:
            self.DEFI_PROTOCOLS = ["uniswap_v3", "sushiswap", "curve"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ACTN_ENV", "development") == "production"
    
    def validate_config(self) -> bool:
        """Validate critical configuration parameters"""
        missing_configs = []
        
        if not self.TWITTER_API_KEY:
            missing_configs.append("TWITTER_API_KEY")
        
        if self.is_production and not os.path.exists(self.FIREBASE_CREDENTIALS_PATH):
            missing_configs.append("FIREBASE_CREDENTIALS_PATH")
        
        if missing_configs:
            raise ValueError(f"Missing required configurations: {missing_configs}")
        
        return True

# Global configuration instance
config = ACTNConfig()