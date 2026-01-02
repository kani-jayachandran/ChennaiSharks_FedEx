import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Service for processing and transforming case data for AI models
    """
    
    def __init__(self):
        """Initialize the data processor"""
        pass
    
    def process_case_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw case data into features suitable for ML models
        
        Args:
            case_data: Raw case data dictionary
            
        Returns:
            Processed features dictionary
        """
        try:
            processed = {}
            
            # Basic numerical features
            processed['debtAmount'] = float(case_data.get('debtAmount', 0))
            processed['agingDays'] = int(case_data.get('agingDays', 0))
            processed['previousInteractions'] = int(case_data.get('previousInteractions', 0))
            
            # Categorical features
            processed['customerRiskProfile'] = case_data.get('customerRiskProfile', 'MEDIUM')
            processed['serviceType'] = case_data.get('serviceType', 'STANDARD')
            processed['customerSegment'] = case_data.get('customerSegment', 'STANDARD')
            
            # Date processing
            if 'invoiceDate' in case_data:
                processed['invoiceDate'] = case_data['invoiceDate']
            if 'dueDate' in case_data:
                processed['dueDate'] = case_data['dueDate']
            
            # Payment history processing
            payment_history = case_data.get('paymentHistory', [])
            processed['paymentHistory'] = payment_history
            processed['paymentHistoryLength'] = len(payment_history)
            
            # Calculate derived features
            processed['amountCategory'] = self._categorize_amount(processed['debtAmount'])
            processed['agingCategory'] = self._categorize_aging(processed['agingDays'])
            processed['riskScore'] = self._calculate_risk_score(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing case features: {e}")
            return case_data  # Return original data if processing fails
    
    def _categorize_amount(self, amount: float) -> str:
        """Categorize debt amount into buckets"""
        if amount >= 50000:
            return 'VERY_HIGH'
        elif amount >= 20000:
            return 'HIGH'
        elif amount >= 5000:
            return 'MEDIUM'
        elif amount >= 1000:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _categorize_aging(self, aging_days: int) -> str:
        """Categorize aging into buckets"""
        if aging_days >= 120:
            return 'CRITICAL'
        elif aging_days >= 90:
            return 'HIGH'
        elif aging_days >= 60:
            return 'MEDIUM'
        elif aging_days >= 30:
            return 'LOW'
        else:
            return 'FRESH'
    
    def _calculate_risk_score(self, processed_data: Dict[str, Any]) -> float:
        """Calculate a basic risk score"""
        risk_score = 0
        
        # Risk from aging
        aging_days = processed_data.get('agingDays', 0)
        if aging_days > 90:
            risk_score += 40
        elif aging_days > 60:
            risk_score += 25
        elif aging_days > 30:
            risk_score += 10
        
        # Risk from customer profile
        risk_profile = processed_data.get('customerRiskProfile', 'MEDIUM')
        risk_mapping = {'LOW': 5, 'MEDIUM': 15, 'HIGH': 30, 'CRITICAL': 50}
        risk_score += risk_mapping.get(risk_profile, 15)
        
        # Risk from interactions
        interactions = processed_data.get('previousInteractions', 0)
        if interactions > 10:
            risk_score += 20
        elif interactions > 5:
            risk_score += 10
        
        return min(100, risk_score)