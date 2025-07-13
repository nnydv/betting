"""
Configuration module for Football Match Prediction System

This module contains configuration settings for different environments
(development, testing, production) with proper defaults and validation.
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Base configuration class with common settings."""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'football-prediction-secret-key'
    DEBUG = False
    TESTING = False
    
    # Data paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    MODEL_DIR = BASE_DIR / 'models'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # Create directories if they don't exist
    for directory in [DATA_DIR, MODEL_DIR, LOGS_DIR]:
        directory.mkdir(exist_ok=True)
    
    # Data source configuration
    FOOTBALL_DATA_BASE_URL = "https://www.football-data.co.uk/mmz4281"
    DEFAULT_SEASON = "2324"
    DEFAULT_LEAGUE = "E0"
    
    # Model configuration
    MODEL_FILE = "model.joblib"
    METRICS_FILE = "model_metrics.json"
    RAW_DATA_FILE = "matches.csv"
    CLEAN_DATA_FILE = "cleaned_matches.csv"
    
    # Training parameters
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    CV_FOLDS = 5
    
    # API configuration
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 30
    RATE_LIMIT = "100 per hour"
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Flask configuration
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    
    # Development-specific settings
    FLASK_ENV = "development"
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Development-specific initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory or test databases
    TEST_DATA_FILE = "test_matches.csv"
    TEST_MODEL_FILE = "test_model.joblib"
    
    # Reduce timeouts for faster tests
    REQUEST_TIMEOUT = 5
    MAX_RETRIES = 1
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Testing-specific initialization
        import logging
        logging.disable(logging.CRITICAL)


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    
    # Production security settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production data sources
    FOOTBALL_DATA_BASE_URL = os.environ.get('DATA_SOURCE_URL', Config.FOOTBALL_DATA_BASE_URL)
    
    # Production logging
    LOG_LEVEL = "WARNING"
    
    # Production Flask settings
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = int(os.environ.get('PORT', 5000))
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Set up file logging
        if not app.debug and not app.testing:
            file_handler = RotatingFileHandler(
                'logs/football_prediction.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """
    Get configuration based on environment.
    
    Args:
        config_name: Configuration name ('development', 'testing', 'production')
        
    Returns:
        Configuration class instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])


# Model hyperparameters
HYPERPARAMETER_GRID = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 0.9, 1.0]
}

# Feature engineering settings
FEATURE_CONFIG = {
    'numeric_features': [
        'home_goals', 'away_goals', 'total_goals', 
        'goal_difference', 'month', 'day_of_week'
    ],
    'categorical_features': [
        'home_team', 'away_team'
    ],
    'derived_features': [
        'total_goals', 'goal_difference', 'home_win', 
        'draw', 'away_win', 'high_scoring'
    ]
}

# API endpoints configuration
API_ENDPOINTS = {
    'predict': '/predict',
    'metrics': '/metrics',
    'health': '/health',
    'model_info': '/model/info'
}

# Validation rules
VALIDATION_RULES = {
    'home_goals': {'min': 0, 'max': 20, 'type': int},
    'away_goals': {'min': 0, 'max': 20, 'type': int},
    'total_goals': {'min': 0, 'max': 40, 'type': int},
    'goal_difference': {'min': -20, 'max': 20, 'type': int}
}