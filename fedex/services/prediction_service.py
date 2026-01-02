import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Service for coordinating AI predictions and recommendations
    """
    
    def __init__(self):
        """Initialize the prediction service"""
        self.prediction_cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    def get_comprehensive_prediction(self, case_data: Dict[str, Any], models: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive prediction combining all AI models
        
        Args:
            case_data: Case information
            models: Dictionary of AI models
            
        Returns:
            Comprehensive prediction results
        """
        try:
            case_id = case_data.get('caseId', 'unknown')
            
            # Check cache first
            cache_key = f"prediction_{case_id}_{hash(str(case_data))}"
            if cache_key in self.prediction_cache:
                cached_result = self.prediction_cache[cache_key]
                if datetime.now() - cached_result['timestamp'] < timedelta(seconds=self.cache_ttl):
                    return cached_result['data']
            
            # Process case features
            features = models['data_processor'].process_case_features(case_data)
            
            # Get individual predictions
            recovery_prob = models['recovery_predictor'].predict_probability(features)
            priority_score = models['case_prioritizer'].calculate_priority(features)
            risk_score = models['case_prioritizer'].calculate_risk_score(features)
            
            # Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(
                case_data, recovery_prob, priority_score, risk_score
            )
            
            # Calculate confidence
            confidence = self._calculate_overall_confidence(case_data, recovery_prob, priority_score)
            
            # Determine urgency level
            urgency = self._determine_urgency(priority_score, risk_score, case_data.get('agingDays', 0))
            
            # Generate next actions
            next_actions = self._generate_next_actions(case_data, recovery_prob, priority_score, urgency)
            
            # Compile comprehensive result
            result = {
                'caseId': case_id,
                'predictions': {
                    'recoveryProbability': float(recovery_prob),
                    'priorityScore': float(priority_score),
                    'riskScore': float(risk_score),
                    'confidence': float(confidence)
                },
                'classification': {
                    'urgency': urgency,
                    'riskCategory': self._classify_risk(risk_score),
                    'priorityCategory': self._classify_priority(priority_score),
                    'recoveryCategory': self._classify_recovery_probability(recovery_prob)
                },
                'recommendations': recommendations,
                'nextActions': next_actions,
                'timeline': self._generate_timeline(case_data, urgency),
                'metadata': {
                    'predictionTimestamp': datetime.now().isoformat(),
                    'modelVersions': {
                        'recovery_predictor': '1.0.0',
                        'case_prioritizer': '1.0.0',
                        'dca_scorer': '1.0.0'
                    }
                }
            }
            
            # Cache result
            self.prediction_cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating comprehensive prediction: {e}")
            return {
                'caseId': case_data.get('caseId', 'unknown'),
                'error': 'Failed to generate prediction',
                'predictions': {
                    'recoveryProbability': 0.5,
                    'priorityScore': 50.0,
                    'riskScore': 50.0,
                    'confidence': 0.1
                }
            }
    
    def batch_predict_with_optimization(self, cases: List[Dict[str, Any]], models: Dict[str, Any]) -> Dict[str, Any]:
        """
        Batch prediction with optimization recommendations
        
        Args:
            cases: List of case data
            models: Dictionary of AI models
            
        Returns:
            Batch prediction results with optimization
        """
        try:
            predictions = []
            optimization_insights = {
                'totalCases': len(cases),
                'highPriorityCases': 0,
                'highRiskCases': 0,
                'lowRecoveryProbabilityCases': 0,
                'recommendedActions': []
            }
            
            for case_data in cases:
                try:
                    prediction = self.get_comprehensive_prediction(case_data, models)
                    predictions.append(prediction)
                    
                    # Collect optimization insights
                    if prediction['predictions']['priorityScore'] > 80:
                        optimization_insights['highPriorityCases'] += 1
                    
                    if prediction['predictions']['riskScore'] > 70:
                        optimization_insights['highRiskCases'] += 1
                    
                    if prediction['predictions']['recoveryProbability'] < 0.3:
                        optimization_insights['lowRecoveryProbabilityCases'] += 1
                        
                except Exception as case_error:
                    logger.error(f"Error processing case {case_data.get('caseId', 'unknown')}: {case_error}")
                    predictions.append({
                        'caseId': case_data.get('caseId', 'unknown'),
                        'error': 'Processing failed',
                        'predictions': {'recoveryProbability': 0.5, 'priorityScore': 50.0, 'riskScore': 50.0, 'confidence': 0.1}
                    })
            
            # Generate batch-level recommendations
            optimization_insights['recommendedActions'] = self._generate_batch_recommendations(optimization_insights)
            
            # Sort predictions by priority
            predictions.sort(key=lambda x: x.get('predictions', {}).get('priorityScore', 0), reverse=True)
            
            return {
                'predictions': predictions,
                'optimization': optimization_insights,
                'summary': {
                    'totalProcessed': len(predictions),
                    'averagePriority': np.mean([p.get('predictions', {}).get('priorityScore', 0) for p in predictions]),
                    'averageRecoveryProb': np.mean([p.get('predictions', {}).get('recoveryProbability', 0) for p in predictions]),
                    'processingTimestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in batch prediction: {e}")
            return {
                'error': 'Batch prediction failed',
                'predictions': [],
                'optimization': {}
            }
    
    def _generate_comprehensive_recommendations(self, case_data: Dict[str, Any], recovery_prob: float, 
                                             priority_score: float, risk_score: float) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        # Recovery probability based recommendations
        if recovery_prob > 0.8:
            recommendations.append("High recovery probability - prioritize immediate contact")
            recommendations.append("Consider offering early payment incentives")
        elif recovery_prob > 0.6:
            recommendations.append("Moderate recovery probability - standard collection process")
            recommendations.append("Schedule regular follow-ups")
        else:
            recommendations.append("Low recovery probability - consider alternative strategies")
            recommendations.append("Evaluate for legal action or settlement")
        
        # Priority based recommendations
        if priority_score > 80:
            recommendations.append("High priority case - assign to senior agent")
            recommendations.append("Daily monitoring required")
        elif priority_score > 60:
            recommendations.append("Medium priority - weekly review recommended")
        
        # Risk based recommendations
        if risk_score > 70:
            recommendations.append("High-risk case - proceed with caution")
            recommendations.append("Ensure full compliance documentation")
        
        # Aging based recommendations
        aging_days = case_data.get('agingDays', 0)
        if aging_days > 90:
            recommendations.append("Significantly aged case - consider escalation")
            recommendations.append("Review for potential write-off")
        elif aging_days > 60:
            recommendations.append("Aging case - increase contact frequency")
        
        # Amount based recommendations
        debt_amount = case_data.get('debtAmount', 0)
        if debt_amount > 25000:
            recommendations.append("High-value case - specialized handling required")
            recommendations.append("Consider payment plan options")
        elif debt_amount < 500:
            recommendations.append("Low-value case - cost-effective approach needed")
        
        return recommendations
    
    def _calculate_overall_confidence(self, case_data: Dict[str, Any], recovery_prob: float, priority_score: float) -> float:
        """Calculate overall confidence in predictions"""
        confidence = 0.6  # Base confidence
        
        # Data completeness factor
        if case_data.get('paymentHistory'):
            confidence += 0.1
        if case_data.get('previousInteractions', 0) > 0:
            confidence += 0.1
        if case_data.get('customerRiskProfile') != 'MEDIUM':
            confidence += 0.05
        
        # Prediction certainty factor
        if recovery_prob > 0.8 or recovery_prob < 0.2:
            confidence += 0.1
        if priority_score > 80 or priority_score < 20:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _determine_urgency(self, priority_score: float, risk_score: float, aging_days: int) -> str:
        """Determine urgency level"""
        urgency_score = (priority_score * 0.4 + risk_score * 0.3 + min(aging_days, 120) * 0.3)
        
        if urgency_score > 80 or aging_days > 90:
            return "CRITICAL"
        elif urgency_score > 60 or aging_days > 60:
            return "HIGH"
        elif urgency_score > 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _classify_risk(self, risk_score: float) -> str:
        """Classify risk level"""
        if risk_score > 80:
            return "CRITICAL"
        elif risk_score > 60:
            return "HIGH"
        elif risk_score > 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _classify_priority(self, priority_score: float) -> str:
        """Classify priority level"""
        if priority_score > 80:
            return "CRITICAL"
        elif priority_score > 60:
            return "HIGH"
        elif priority_score > 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _classify_recovery_probability(self, recovery_prob: float) -> str:
        """Classify recovery probability"""
        if recovery_prob > 0.8:
            return "EXCELLENT"
        elif recovery_prob > 0.6:
            return "GOOD"
        elif recovery_prob > 0.4:
            return "FAIR"
        else:
            return "POOR"
    
    def _generate_next_actions(self, case_data: Dict[str, Any], recovery_prob: float, 
                             priority_score: float, urgency: str) -> List[Dict[str, Any]]:
        """Generate specific next actions"""
        actions = []
        
        if urgency == "CRITICAL":
            actions.append({
                "action": "immediate_contact",
                "description": "Contact customer within 24 hours",
                "priority": "HIGH",
                "deadline": (datetime.now() + timedelta(days=1)).isoformat()
            })
        
        if recovery_prob > 0.7:
            actions.append({
                "action": "payment_negotiation",
                "description": "Initiate payment plan discussion",
                "priority": "MEDIUM",
                "deadline": (datetime.now() + timedelta(days=3)).isoformat()
            })
        
        if case_data.get('agingDays', 0) > 60:
            actions.append({
                "action": "escalation_review",
                "description": "Review case for potential escalation",
                "priority": "MEDIUM",
                "deadline": (datetime.now() + timedelta(days=7)).isoformat()
            })
        
        return actions
    
    def _generate_timeline(self, case_data: Dict[str, Any], urgency: str) -> Dict[str, Any]:
        """Generate expected timeline"""
        base_days = {
            "CRITICAL": 7,
            "HIGH": 14,
            "MEDIUM": 30,
            "LOW": 60
        }
        
        expected_resolution_days = base_days.get(urgency, 30)
        
        return {
            "expectedResolutionDays": expected_resolution_days,
            "nextReviewDate": (datetime.now() + timedelta(days=7)).isoformat(),
            "escalationDate": (datetime.now() + timedelta(days=expected_resolution_days * 0.8)).isoformat(),
            "writeOffDate": (datetime.now() + timedelta(days=120)).isoformat()
        }
    
    def _generate_batch_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate batch-level recommendations"""
        recommendations = []
        
        total_cases = insights['totalCases']
        high_priority_rate = insights['highPriorityCases'] / total_cases if total_cases > 0 else 0
        high_risk_rate = insights['highRiskCases'] / total_cases if total_cases > 0 else 0
        
        if high_priority_rate > 0.3:
            recommendations.append("High concentration of priority cases - consider additional resources")
        
        if high_risk_rate > 0.2:
            recommendations.append("Significant risk exposure - implement enhanced monitoring")
        
        if insights['lowRecoveryProbabilityCases'] > total_cases * 0.4:
            recommendations.append("Many cases with low recovery probability - review collection strategies")
        
        return recommendations
    
    def get_status(self) -> Dict[str, Any]:
        """Get prediction service status"""
        return {
            "loaded": True,
            "cache_size": len(self.prediction_cache),
            "cache_ttl_seconds": self.cache_ttl,
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }