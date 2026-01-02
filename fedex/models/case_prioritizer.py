import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CasePrioritizer:
    """
    AI model for prioritizing debt collection cases based on multiple factors
    including recovery probability, debt amount, aging, customer risk profile, etc.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the Case Prioritizer model"""
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = [
            'debt_amount', 'aging_days', 'previous_interactions', 
            'customer_risk_score', 'service_type_encoded', 'customer_segment_encoded',
            'payment_history_score', 'seasonal_factor', 'amount_category'
        ]
        self.model_path = model_path or "models/case_prioritizer_model.joblib"
        self.scaler_path = "models/case_prioritizer_scaler.joblib"
        self.encoders_path = "models/case_prioritizer_encoders.joblib"
        
        # Priority weights for different factors
        self.priority_weights = {
            'debt_amount': 0.25,
            'aging_factor': 0.30,
            'recovery_probability': 0.25,
            'customer_risk': 0.15,
            'business_impact': 0.05
        }
        
        self._load_or_initialize_model()
    
    def _load_or_initialize_model(self):
        """Load existing model or initialize a new one"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.label_encoders = joblib.load(self.encoders_path)
                logger.info("Loaded existing case prioritizer model")
            else:
                self._initialize_model()
                logger.info("Initialized new case prioritizer model")
        except Exception as e:
            logger.warning(f"Error loading model: {e}. Initializing new model.")
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new model with default parameters"""
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        # Initialize label encoders for categorical features
        self.label_encoders = {
            'service_type': LabelEncoder(),
            'customer_segment': LabelEncoder(),
            'customer_risk_profile': LabelEncoder()
        }
        
        # Fit encoders with common values
        self.label_encoders['service_type'].fit(['STANDARD', 'PREMIUM', 'ENTERPRISE', 'SMALL_BUSINESS'])
        self.label_encoders['customer_segment'].fit(['STANDARD', 'VIP', 'CORPORATE', 'SME'])
        self.label_encoders['customer_risk_profile'].fit(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
    
    def calculate_priority(self, case_features: Dict[str, Any]) -> float:
        """
        Calculate priority score for a case (0-100 scale)
        
        Args:
            case_features: Dictionary containing case features
            
        Returns:
            Priority score between 0 and 100
        """
        try:
            # Extract and process features
            processed_features = self._process_features(case_features)
            
            # Calculate individual priority components
            debt_score = self._calculate_debt_amount_score(case_features.get('debtAmount', 0))
            aging_score = self._calculate_aging_score(case_features.get('agingDays', 0))
            risk_score = self._calculate_customer_risk_score(case_features.get('customerRiskProfile', 'MEDIUM'))
            recovery_score = self._estimate_recovery_probability(processed_features)
            business_score = self._calculate_business_impact_score(case_features)
            
            # Weighted priority calculation
            priority_score = (
                debt_score * self.priority_weights['debt_amount'] +
                aging_score * self.priority_weights['aging_factor'] +
                recovery_score * self.priority_weights['recovery_probability'] +
                risk_score * self.priority_weights['customer_risk'] +
                business_score * self.priority_weights['business_impact']
            )
            
            # Normalize to 0-100 scale
            priority_score = max(0, min(100, priority_score))
            
            logger.debug(f"Priority calculation - Debt: {debt_score:.2f}, Aging: {aging_score:.2f}, "
                        f"Risk: {risk_score:.2f}, Recovery: {recovery_score:.2f}, "
                        f"Business: {business_score:.2f}, Final: {priority_score:.2f}")
            
            return priority_score
            
        except Exception as e:
            logger.error(f"Error calculating priority: {e}")
            return 50.0  # Default medium priority
    
    def calculate_risk_score(self, case_features: Dict[str, Any]) -> float:
        """
        Calculate risk score for a case (0-100 scale, higher = riskier)
        
        Args:
            case_features: Dictionary containing case features
            
        Returns:
            Risk score between 0 and 100
        """
        try:
            risk_factors = []
            
            # Aging risk
            aging_days = case_features.get('agingDays', 0)
            if aging_days > 120:
                risk_factors.append(85)
            elif aging_days > 90:
                risk_factors.append(70)
            elif aging_days > 60:
                risk_factors.append(50)
            else:
                risk_factors.append(20)
            
            # Amount risk (very high or very low amounts are riskier)
            debt_amount = case_features.get('debtAmount', 0)
            if debt_amount > 50000:
                risk_factors.append(75)
            elif debt_amount < 100:
                risk_factors.append(80)
            else:
                risk_factors.append(30)
            
            # Customer risk profile
            risk_profile = case_features.get('customerRiskProfile', 'MEDIUM')
            risk_mapping = {'LOW': 20, 'MEDIUM': 50, 'HIGH': 80, 'CRITICAL': 95}
            risk_factors.append(risk_mapping.get(risk_profile, 50))
            
            # Payment history risk
            payment_history = case_features.get('paymentHistory', [])
            if len(payment_history) == 0:
                risk_factors.append(70)  # No payment history is risky
            else:
                # Analyze payment patterns
                recent_payments = len([p for p in payment_history[-5:] if p.get('status') == 'paid'])
                if recent_payments == 0:
                    risk_factors.append(85)
                elif recent_payments < 2:
                    risk_factors.append(60)
                else:
                    risk_factors.append(25)
            
            # Previous interactions risk
            interactions = case_features.get('previousInteractions', 0)
            if interactions > 10:
                risk_factors.append(75)  # Many interactions without resolution
            elif interactions > 5:
                risk_factors.append(50)
            else:
                risk_factors.append(30)
            
            # Calculate weighted average
            risk_score = np.mean(risk_factors)
            
            return max(0, min(100, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 50.0  # Default medium risk
    
    def _process_features(self, case_features: Dict[str, Any]) -> np.ndarray:
        """Process raw case features into model-ready format"""
        try:
            features = {}
            
            # Numerical features
            features['debt_amount'] = float(case_features.get('debtAmount', 0))
            features['aging_days'] = int(case_features.get('agingDays', 0))
            features['previous_interactions'] = int(case_features.get('previousInteractions', 0))
            
            # Encode categorical features
            service_type = case_features.get('serviceType', 'STANDARD')
            try:
                features['service_type_encoded'] = self.label_encoders['service_type'].transform([service_type])[0]
            except ValueError:
                features['service_type_encoded'] = 0  # Default to first category
            
            customer_segment = case_features.get('customerSegment', 'STANDARD')
            try:
                features['customer_segment_encoded'] = self.label_encoders['customer_segment'].transform([customer_segment])[0]
            except ValueError:
                features['customer_segment_encoded'] = 0
            
            # Calculate derived features
            features['customer_risk_score'] = self._encode_risk_profile(case_features.get('customerRiskProfile', 'MEDIUM'))
            features['payment_history_score'] = self._calculate_payment_history_score(case_features.get('paymentHistory', []))
            features['seasonal_factor'] = self._calculate_seasonal_factor()
            features['amount_category'] = self._categorize_amount(features['debt_amount'])
            
            # Convert to array in correct order
            feature_array = np.array([features[col] for col in self.feature_columns]).reshape(1, -1)
            
            return feature_array
            
        except Exception as e:
            logger.error(f"Error processing features: {e}")
            # Return default feature array
            return np.zeros((1, len(self.feature_columns)))
    
    def _calculate_debt_amount_score(self, debt_amount: float) -> float:
        """Calculate priority score based on debt amount"""
        if debt_amount >= 50000:
            return 95
        elif debt_amount >= 20000:
            return 85
        elif debt_amount >= 10000:
            return 75
        elif debt_amount >= 5000:
            return 65
        elif debt_amount >= 1000:
            return 50
        else:
            return 30
    
    def _calculate_aging_score(self, aging_days: int) -> float:
        """Calculate priority score based on case aging"""
        if aging_days >= 120:
            return 100
        elif aging_days >= 90:
            return 90
        elif aging_days >= 60:
            return 75
        elif aging_days >= 30:
            return 60
        else:
            return 40
    
    def _calculate_customer_risk_score(self, risk_profile: str) -> float:
        """Calculate priority score based on customer risk profile"""
        risk_mapping = {
            'CRITICAL': 95,
            'HIGH': 80,
            'MEDIUM': 50,
            'LOW': 30
        }
        return risk_mapping.get(risk_profile, 50)
    
    def _estimate_recovery_probability(self, processed_features: np.ndarray) -> float:
        """Estimate recovery probability (mock implementation)"""
        try:
            # This would use a trained recovery prediction model
            # For now, using a simple heuristic
            debt_amount = processed_features[0][0]
            aging_days = processed_features[0][1]
            
            base_probability = 70
            
            # Adjust based on aging
            if aging_days > 90:
                base_probability -= 30
            elif aging_days > 60:
                base_probability -= 15
            
            # Adjust based on amount
            if debt_amount > 20000:
                base_probability += 10
            elif debt_amount < 500:
                base_probability -= 20
            
            return max(10, min(95, base_probability))
            
        except Exception as e:
            logger.error(f"Error estimating recovery probability: {e}")
            return 50.0
    
    def _calculate_business_impact_score(self, case_features: Dict[str, Any]) -> float:
        """Calculate business impact score"""
        service_type = case_features.get('serviceType', 'STANDARD')
        customer_segment = case_features.get('customerSegment', 'STANDARD')
        
        impact_score = 50  # Base score
        
        if service_type == 'ENTERPRISE':
            impact_score += 20
        elif service_type == 'PREMIUM':
            impact_score += 10
        
        if customer_segment == 'VIP':
            impact_score += 15
        elif customer_segment == 'CORPORATE':
            impact_score += 10
        
        return min(100, impact_score)
    
    def _encode_risk_profile(self, risk_profile: str) -> float:
        """Encode risk profile to numerical value"""
        mapping = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        return mapping.get(risk_profile, 2)
    
    def _calculate_payment_history_score(self, payment_history: List[Dict]) -> float:
        """Calculate score based on payment history"""
        if not payment_history:
            return 0
        
        total_payments = len(payment_history)
        successful_payments = len([p for p in payment_history if p.get('status') == 'paid'])
        
        if total_payments == 0:
            return 0
        
        return (successful_payments / total_payments) * 100
    
    def _calculate_seasonal_factor(self) -> float:
        """Calculate seasonal factor based on current month"""
        current_month = datetime.now().month
        
        # Higher collection rates typically in certain months
        seasonal_multipliers = {
            1: 0.9,   # January - post-holiday low
            2: 1.0,   # February - normal
            3: 1.1,   # March - tax season
            4: 1.2,   # April - tax refunds
            5: 1.0,   # May - normal
            6: 0.95,  # June - summer start
            7: 0.9,   # July - vacation season
            8: 0.9,   # August - vacation season
            9: 1.1,   # September - back to business
            10: 1.1,  # October - Q4 push
            11: 0.95, # November - holiday prep
            12: 0.8   # December - holidays
        }
        
        return seasonal_multipliers.get(current_month, 1.0)
    
    def _categorize_amount(self, amount: float) -> int:
        """Categorize debt amount into buckets"""
        if amount >= 50000:
            return 5
        elif amount >= 20000:
            return 4
        elif amount >= 10000:
            return 3
        elif amount >= 1000:
            return 2
        else:
            return 1
    
    def get_status(self) -> Dict[str, Any]:
        """Get model status information"""
        return {
            "loaded": self.model is not None,
            "model_type": type(self.model).__name__ if self.model else None,
            "feature_count": len(self.feature_columns),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }