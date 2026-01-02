import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RecoveryPredictor:
    """
    AI model for predicting debt recovery probability
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the Recovery Predictor model"""
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path or "models/recovery_predictor_model.joblib"
        self.scaler_path = "models/recovery_predictor_scaler.joblib"
        
        self._load_or_initialize_model()
    
    def _load_or_initialize_model(self):
        """Load existing model or initialize a new one"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Loaded existing recovery predictor model")
            else:
                self._initialize_model()
                logger.info("Initialized new recovery predictor model")
        except Exception as e:
            logger.warning(f"Error loading model: {e}. Initializing new model.")
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new model with default parameters"""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def predict_probability(self, case_features: Dict[str, Any]) -> float:
        """
        Predict recovery probability for a case
        
        Args:
            case_features: Dictionary containing case features
            
        Returns:
            Recovery probability between 0 and 1
        """
        try:
            # For now, use a heuristic-based approach
            # In production, this would use the trained ML model
            
            debt_amount = case_features.get('debtAmount', 0)
            aging_days = case_features.get('agingDays', 0)
            risk_profile = case_features.get('customerRiskProfile', 'MEDIUM')
            interactions = case_features.get('previousInteractions', 0)
            payment_history = case_features.get('paymentHistory', [])
            
            # Base probability
            base_prob = 0.65
            
            # Adjust based on aging
            if aging_days > 120:
                base_prob -= 0.3
            elif aging_days > 90:
                base_prob -= 0.2
            elif aging_days > 60:
                base_prob -= 0.1
            
            # Adjust based on amount
            if debt_amount > 20000:
                base_prob += 0.1
            elif debt_amount < 500:
                base_prob -= 0.15
            
            # Adjust based on risk profile
            risk_adjustments = {
                'LOW': 0.15,
                'MEDIUM': 0,
                'HIGH': -0.15,
                'CRITICAL': -0.25
            }
            base_prob += risk_adjustments.get(risk_profile, 0)
            
            # Adjust based on interactions
            if interactions > 10:
                base_prob -= 0.2
            elif interactions > 5:
                base_prob -= 0.1
            
            # Adjust based on payment history
            if payment_history:
                successful_payments = len([p for p in payment_history if p.get('status') == 'paid'])
                total_payments = len(payment_history)
                if total_payments > 0:
                    payment_rate = successful_payments / total_payments
                    base_prob += (payment_rate - 0.5) * 0.2
            
            # Ensure probability is between 0 and 1
            return max(0.05, min(0.95, base_prob))
            
        except Exception as e:
            logger.error(f"Error predicting recovery probability: {e}")
            return 0.5  # Default probability
    
    def predict_batch(self, cases: List[Dict[str, Any]]) -> List[float]:
        """Predict recovery probabilities for multiple cases"""
        return [self.predict_probability(case) for case in cases]
    
    def get_status(self) -> Dict[str, Any]:
        """Get model status information"""
        return {
            "loaded": self.model is not None,
            "model_type": type(self.model).__name__ if self.model else None,
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }