"""
Football Match Prediction Model Training Module

This module handles training machine learning models for football match prediction
with comprehensive evaluation, hyperparameter tuning, and model validation.
"""

import logging
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FootballPredictor:
    """
    A class to handle training and evaluation of football match prediction models.
    """
    
    def __init__(self):
        """Initialize the predictor."""
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.model_metrics = {}
    
    def load_data(self, file_path: str = "cleaned_matches.csv") -> Optional[pd.DataFrame]:
        """
        Load cleaned match data.
        
        Args:
            file_path: Path to the cleaned data CSV file
            
        Returns:
            DataFrame with cleaned data or None if loading fails
        """
        try:
            if not Path(file_path).exists():
                logger.error(f"❌ File not found: {file_path}")
                return None
            
            df = pd.read_csv(file_path)
            logger.info(f"✅ Loaded {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load data: {e}")
            return None
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target variable for training.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (features DataFrame, target Series)
        """
        try:
            logger.info("🔧 Preparing features for training...")
            
            # Define feature columns
            numeric_features = ['home_goals', 'away_goals', 'total_goals', 
                              'goal_difference', 'month', 'day_of_week']
            
            # Check which features are available
            available_features = [col for col in numeric_features if col in df.columns]
            
            if not available_features:
                # Fallback to basic features
                available_features = ['home_goals', 'away_goals']
                logger.warning("⚠️ Using basic features only")
            
            self.feature_columns = available_features
            
            # Prepare features
            X = df[available_features].copy()
            
            # Prepare target variable (predict home team outcome)
            y = df['result'].copy()
            
            # Encode target variable
            y_encoded = self.label_encoder.fit_transform(y)
            
            logger.info(f"✅ Features prepared: {len(available_features)} features, {len(y)} samples")
            logger.info(f"Features: {available_features}")
            logger.info(f"Target classes: {list(self.label_encoder.classes_)}")
            
            return X, pd.Series(y_encoded)
            
        except Exception as e:
            logger.error(f"❌ Feature preparation failed: {e}")
            raise
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, 
                   test_size: float = 0.2, random_state: int = 42) -> bool:
        """
        Train the XGBoost model with hyperparameter tuning.
        
        Args:
            X: Features DataFrame
            y: Target Series
            test_size: Proportion of data for testing
            random_state: Random state for reproducibility
            
        Returns:
            bool: True if training successful, False otherwise
        """
        try:
            logger.info("🚀 Starting model training...")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            logger.info(f"Training set: {len(X_train)} samples")
            logger.info(f"Test set: {len(X_test)} samples")
            
            # Define hyperparameter grid
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            }
            
            # Initialize base model
            base_model = xgb.XGBClassifier(
                objective='multi:softprob',
                random_state=random_state,
                eval_metric='mlogloss'
            )
            
            # Perform grid search
            logger.info("🔍 Performing hyperparameter tuning...")
            grid_search = GridSearchCV(
                base_model, param_grid, cv=5, scoring='accuracy',
                n_jobs=-1, verbose=0
            )
            
            grid_search.fit(X_train, y_train)
            
            # Get best model
            self.model = grid_search.best_estimator_
            
            logger.info(f"✅ Best parameters: {grid_search.best_params_}")
            logger.info(f"✅ Best CV score: {grid_search.best_score_:.4f}")
            
            # Evaluate on test set
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"🎯 Test Accuracy: {accuracy:.4f}")
            
            # Store metrics
            self.model_metrics = {
                'test_accuracy': float(accuracy),
                'best_cv_score': float(grid_search.best_score_),
                'best_params': grid_search.best_params_,
                'feature_importance': dict(zip(
                    self.feature_columns,
                    self.model.feature_importances_.tolist()
                ))
            }
            
            # Detailed evaluation
            self._detailed_evaluation(X_test, y_test, y_pred)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return False
    
    def _detailed_evaluation(self, X_test: pd.DataFrame, y_test: pd.Series, y_pred: np.ndarray):
        """
        Perform detailed model evaluation.
        
        Args:
            X_test: Test features
            y_test: Test target
            y_pred: Predictions
        """
        try:
            logger.info("📊 Detailed Model Evaluation:")
            
            # Classification report
            target_names = self.label_encoder.classes_
            report = classification_report(y_test, y_pred, target_names=target_names)
            logger.info(f"\nClassification Report:\n{report}")
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            logger.info(f"\nConfusion Matrix:\n{cm}")
            
            # Feature importance
            if hasattr(self.model, 'feature_importances_'):
                feature_importance = dict(zip(
                    self.feature_columns,
                    self.model.feature_importances_
                ))
                logger.info("Feature Importance:")
                for feature, importance in sorted(
                    feature_importance.items(), key=lambda x: x[1], reverse=True
                ):
                    logger.info(f"  {feature}: {importance:.4f}")
            
            # Cross-validation scores
            if len(X_test) > 10:  # Only if we have enough data
                cv_scores = cross_val_score(self.model, X_test, y_test, cv=3)
                logger.info(f"Cross-validation scores: {cv_scores}")
                logger.info(f"Mean CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
        except Exception as e:
            logger.warning(f"⚠️ Detailed evaluation failed: {e}")
    
    def save_model(self, model_path: str = "model.joblib", 
                  metrics_path: str = "model_metrics.json") -> bool:
        """
        Save the trained model and metrics.
        
        Args:
            model_path: Path to save the model
            metrics_path: Path to save the metrics
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            if self.model is None:
                logger.error("❌ No trained model to save")
                return False
            
            # Save model
            joblib.dump({
                'model': self.model,
                'label_encoder': self.label_encoder,
                'feature_columns': self.feature_columns
            }, model_path)
            
            # Save metrics
            with open(metrics_path, 'w') as f:
                json.dump(self.model_metrics, f, indent=2)
            
            logger.info(f"✅ Model saved to {model_path}")
            logger.info(f"✅ Metrics saved to {metrics_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            return False
    
    def load_model(self, model_path: str = "model.joblib") -> bool:
        """
        Load a pre-trained model.
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            bool: True if load successful, False otherwise
        """
        try:
            if not Path(model_path).exists():
                logger.error(f"❌ Model file not found: {model_path}")
                return False
            
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.feature_columns = model_data['feature_columns']
            
            logger.info(f"✅ Model loaded from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def predict(self, features: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """
        Make a prediction for a single match.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            Dictionary with prediction and probabilities
        """
        try:
            if self.model is None:
                logger.error("❌ No trained model available")
                return None
            
            # Prepare features
            feature_array = np.array([[features.get(col, 0) for col in self.feature_columns]])
            
            # Make prediction
            prediction = self.model.predict(feature_array)[0]
            probabilities = self.model.predict_proba(feature_array)[0]
            
            # Decode prediction
            predicted_outcome = self.label_encoder.inverse_transform([prediction])[0]
            
            return {
                'predicted_outcome': predicted_outcome,
                'probabilities': {
                    class_name: float(prob) 
                    for class_name, prob in zip(self.label_encoder.classes_, probabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return None


def main():
    """Main function to run the model training process."""
    predictor = FootballPredictor()
    
    # Load data
    data = predictor.load_data()
    if data is None:
        logger.error("❌ Failed to load data")
        return
    
    # Prepare features
    try:
        X, y = predictor.prepare_features(data)
    except Exception as e:
        logger.error(f"❌ Feature preparation failed: {e}")
        return
    
    # Train model
    if predictor.train_model(X, y):
        # Save model
        if predictor.save_model():
            logger.info("🎉 Model training completed successfully!")
        else:
            logger.error("❌ Failed to save model")
    else:
        logger.error("❌ Model training failed")


if __name__ == "__main__":
    main()