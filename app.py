"""
Football Match Prediction Web Application

A Flask web application for predicting football match outcomes using trained ML models.
Provides a user-friendly interface for making predictions and viewing model performance.
"""

import logging
import json
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, flash
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'football-prediction-secret-key'
CORS(app)

# Global variables for model
model_data = None
model_metrics = None


def load_model_and_metrics():
    """Load the trained model and metrics."""
    global model_data, model_metrics
    
    try:
        # Load model
        model_path = "model.joblib"
        if Path(model_path).exists():
            model_data = joblib.load(model_path)
            logger.info("✅ Model loaded successfully")
        else:
            logger.warning("⚠️ Model file not found")
            return False
        
        # Load metrics
        metrics_path = "model_metrics.json"
        if Path(metrics_path).exists():
            with open(metrics_path, 'r') as f:
                model_metrics = json.load(f)
            logger.info("✅ Metrics loaded successfully")
        else:
            logger.warning("⚠️ Metrics file not found")
            model_metrics = {}
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        return False


@app.route('/')
def index():
    """Home page with prediction interface."""
    return render_template('index.html', metrics=model_metrics)


@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests."""
    try:
        if model_data is None:
            return jsonify({
                'error': 'Model not loaded. Please train the model first.'
            }), 500
        
        # Get input data
        data = request.get_json()
        
        # Validate input
        required_fields = ['home_goals', 'away_goals']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract features
        features = {}
        for col in model_data['feature_columns']:
            if col in data:
                features[col] = float(data[col])
            else:
                # Use default values for missing features
                default_values = {
                    'total_goals': data.get('home_goals', 0) + data.get('away_goals', 0),
                    'goal_difference': data.get('home_goals', 0) - data.get('away_goals', 0),
                    'month': 1,
                    'day_of_week': 0
                }
                features[col] = default_values.get(col, 0)
        
        # Prepare features for prediction
        feature_array = np.array([[features.get(col, 0) for col in model_data['feature_columns']]])
        
        # Make prediction
        model = model_data['model']
        label_encoder = model_data['label_encoder']
        
        prediction = model.predict(feature_array)[0]
        probabilities = model.predict_proba(feature_array)[0]
        
        # Decode prediction
        predicted_outcome = label_encoder.inverse_transform([prediction])[0]
        
        # Format response
        result = {
            'predicted_outcome': predicted_outcome,
            'probabilities': {
                class_name: float(prob) 
                for class_name, prob in zip(label_encoder.classes_, probabilities)
            },
            'features_used': features
        }
        
        logger.info(f"Prediction made: {predicted_outcome}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Prediction failed: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/metrics')
def get_metrics():
    """Get model performance metrics."""
    try:
        if model_metrics is None:
            return jsonify({'error': 'Metrics not available'}), 404
        
        return jsonify(model_metrics)
        
    except Exception as e:
        logger.error(f"❌ Failed to get metrics: {e}")
        return jsonify({'error': f'Failed to get metrics: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    status = {
        'status': 'healthy',
        'model_loaded': model_data is not None,
        'metrics_loaded': model_metrics is not None
    }
    return jsonify(status)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


def create_templates():
    """Create HTML templates for the application."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Match Predictor</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #34495e;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .metrics {
            margin-top: 30px;
            padding: 20px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        .probability {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .prob-bar {
            background-color: #3498db;
            height: 20px;
            border-radius: 10px;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚽ Football Match Predictor</h1>
        
        <form id="predictionForm">
            <div class="form-group">
                <label for="home_goals">Home Team Goals:</label>
                <input type="number" id="home_goals" name="home_goals" min="0" max="20" required>
            </div>
            
            <div class="form-group">
                <label for="away_goals">Away Team Goals:</label>
                <input type="number" id="away_goals" name="away_goals" min="0" max="20" required>
            </div>
            
            <button type="submit">Predict Match Outcome</button>
        </form>
        
        <div id="result" class="result"></div>
        
        {% if metrics %}
        <div class="metrics">
            <h3>📊 Model Performance</h3>
            <p><strong>Test Accuracy:</strong> {{ "%.2f"|format(metrics.test_accuracy * 100) }}%</p>
            <p><strong>Cross-Validation Score:</strong> {{ "%.2f"|format(metrics.best_cv_score * 100) }}%</p>
            {% if metrics.feature_importance %}
            <h4>Feature Importance:</h4>
            <ul>
                {% for feature, importance in metrics.feature_importance.items() %}
                <li>{{ feature }}: {{ "%.3f"|format(importance) }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <script>
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                home_goals: parseInt(formData.get('home_goals')),
                away_goals: parseInt(formData.get('away_goals'))
            };
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                
                if (response.ok) {
                    const outcomeMap = {
                        'H': 'Home Win',
                        'D': 'Draw',
                        'A': 'Away Win'
                    };
                    
                    let probHtml = '';
                    for (const [outcome, prob] of Object.entries(result.probabilities)) {
                        const percentage = (prob * 100).toFixed(1);
                        probHtml += `
                            <div class="probability">
                                <span>${outcomeMap[outcome] || outcome}:</span>
                                <span>${percentage}%</span>
                            </div>
                            <div style="background-color: #eee; border-radius: 10px; margin-bottom: 10px;">
                                <div class="prob-bar" style="width: ${percentage}%;"></div>
                            </div>
                        `;
                    }
                    
                    resultDiv.innerHTML = `
                        <h3>🎯 Prediction Result</h3>
                        <p><strong>Predicted Outcome:</strong> ${outcomeMap[result.predicted_outcome] || result.predicted_outcome}</p>
                        <h4>Probabilities:</h4>
                        ${probHtml}
                    `;
                    resultDiv.className = 'result success';
                } else {
                    resultDiv.innerHTML = `<h3>❌ Error</h3><p>${result.error}</p>`;
                    resultDiv.className = 'result error';
                }
                
                resultDiv.style.display = 'block';
                
            } catch (error) {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = `<h3>❌ Error</h3><p>Failed to make prediction: ${error.message}</p>`;
                resultDiv.className = 'result error';
                resultDiv.style.display = 'block';
            }
        });
    </script>
</body>
</html>"""
    
    with open(templates_dir / "index.html", "w") as f:
        f.write(index_html)
    
    logger.info("✅ Templates created")


def main():
    """Main function to run the Flask application."""
    # Create templates
    create_templates()
    
    # Load model and metrics
    if not load_model_and_metrics():
        logger.warning("⚠️ Model not loaded. Some features may not work.")
    
    # Run the application
    logger.info("🚀 Starting Football Prediction Web Application...")
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()