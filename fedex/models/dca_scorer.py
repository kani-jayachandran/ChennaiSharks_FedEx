import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DCAScorer:
    """
    AI model for scoring DCA (Debt Collection Agency) performance
    """
    
    def __init__(self):
        """Initialize the DCA Scorer"""
        self.performance_weights = {
            'recovery_rate': 0.35,
            'resolution_time': 0.25,
            'sla_compliance': 0.20,
            'customer_satisfaction': 0.20
        }
        
        # Benchmarks for scoring
        self.benchmarks = {
            'excellent_recovery_rate': 80.0,
            'good_recovery_rate': 65.0,
            'average_recovery_rate': 50.0,
            'excellent_resolution_time': 30.0,  # days
            'good_resolution_time': 45.0,
            'average_resolution_time': 60.0,
            'excellent_sla_compliance': 95.0,
            'good_sla_compliance': 85.0,
            'average_sla_compliance': 75.0,
            'excellent_satisfaction': 4.5,
            'good_satisfaction': 3.5,
            'average_satisfaction': 2.5
        }
    
    def calculate_performance_score(self, dca_data: Dict[str, Any]) -> float:
        """Calculate performance score based on recovery metrics"""
        try:
            recovery_rate = dca_data.get('averageRecoveryRate', 0)
            resolution_time = dca_data.get('averageResolutionTime', 60)
            
            # Score recovery rate (0-100)
            if recovery_rate >= self.benchmarks['excellent_recovery_rate']:
                recovery_score = 100
            elif recovery_rate >= self.benchmarks['good_recovery_rate']:
                recovery_score = 70 + (recovery_rate - self.benchmarks['good_recovery_rate']) / \
                               (self.benchmarks['excellent_recovery_rate'] - self.benchmarks['good_recovery_rate']) * 30
            elif recovery_rate >= self.benchmarks['average_recovery_rate']:
                recovery_score = 40 + (recovery_rate - self.benchmarks['average_recovery_rate']) / \
                               (self.benchmarks['good_recovery_rate'] - self.benchmarks['average_recovery_rate']) * 30
            else:
                recovery_score = max(0, recovery_rate / self.benchmarks['average_recovery_rate'] * 40)
            
            # Score resolution time (lower is better)
            if resolution_time <= self.benchmarks['excellent_resolution_time']:
                time_score = 100
            elif resolution_time <= self.benchmarks['good_resolution_time']:
                time_score = 70 + (self.benchmarks['good_resolution_time'] - resolution_time) / \
                           (self.benchmarks['good_resolution_time'] - self.benchmarks['excellent_resolution_time']) * 30
            elif resolution_time <= self.benchmarks['average_resolution_time']:
                time_score = 40 + (self.benchmarks['average_resolution_time'] - resolution_time) / \
                           (self.benchmarks['average_resolution_time'] - self.benchmarks['good_resolution_time']) * 30
            else:
                time_score = max(0, 40 - (resolution_time - self.benchmarks['average_resolution_time']) * 0.5)
            
            # Weighted average
            performance_score = (recovery_score * 0.7 + time_score * 0.3)
            
            return min(100, max(0, performance_score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 50.0
    
    def calculate_reliability_score(self, dca_data: Dict[str, Any]) -> float:
        """Calculate reliability score based on SLA compliance"""
        try:
            sla_compliance = dca_data.get('slaCompliance', 80.0)
            
            # Score SLA compliance
            if sla_compliance >= self.benchmarks['excellent_sla_compliance']:
                reliability_score = 100
            elif sla_compliance >= self.benchmarks['good_sla_compliance']:
                reliability_score = 70 + (sla_compliance - self.benchmarks['good_sla_compliance']) / \
                                  (self.benchmarks['excellent_sla_compliance'] - self.benchmarks['good_sla_compliance']) * 30
            elif sla_compliance >= self.benchmarks['average_sla_compliance']:
                reliability_score = 40 + (sla_compliance - self.benchmarks['average_sla_compliance']) / \
                                  (self.benchmarks['good_sla_compliance'] - self.benchmarks['average_sla_compliance']) * 30
            else:
                reliability_score = max(0, sla_compliance / self.benchmarks['average_sla_compliance'] * 40)
            
            return min(100, max(0, reliability_score))
            
        except Exception as e:
            logger.error(f"Error calculating reliability score: {e}")
            return 80.0
    
    def calculate_efficiency_score(self, dca_data: Dict[str, Any]) -> float:
        """Calculate efficiency score based on customer satisfaction and other metrics"""
        try:
            customer_satisfaction = dca_data.get('customerSatisfactionScore', 3.5)
            total_cases = dca_data.get('totalCasesHandled', 0)
            capacity = dca_data.get('capacity', {})
            
            # Score customer satisfaction
            if customer_satisfaction >= self.benchmarks['excellent_satisfaction']:
                satisfaction_score = 100
            elif customer_satisfaction >= self.benchmarks['good_satisfaction']:
                satisfaction_score = 70 + (customer_satisfaction - self.benchmarks['good_satisfaction']) / \
                                   (self.benchmarks['excellent_satisfaction'] - self.benchmarks['good_satisfaction']) * 30
            elif customer_satisfaction >= self.benchmarks['average_satisfaction']:
                satisfaction_score = 40 + (customer_satisfaction - self.benchmarks['average_satisfaction']) / \
                                   (self.benchmarks['good_satisfaction'] - self.benchmarks['average_satisfaction']) * 30
            else:
                satisfaction_score = max(0, customer_satisfaction / self.benchmarks['average_satisfaction'] * 40)
            
            # Score capacity utilization (optimal around 70-80%)
            max_cases = capacity.get('maxCases', 1000)
            current_cases = capacity.get('currentCases', 0)
            
            if max_cases > 0:
                utilization = (current_cases / max_cases) * 100
                if 70 <= utilization <= 80:
                    utilization_score = 100
                elif 60 <= utilization < 70 or 80 < utilization <= 90:
                    utilization_score = 80
                elif 50 <= utilization < 60 or 90 < utilization <= 95:
                    utilization_score = 60
                else:
                    utilization_score = 40
            else:
                utilization_score = 50
            
            # Score experience (based on total cases handled)
            if total_cases >= 5000:
                experience_score = 100
            elif total_cases >= 2000:
                experience_score = 80
            elif total_cases >= 500:
                experience_score = 60
            else:
                experience_score = 40
            
            # Weighted efficiency score
            efficiency_score = (satisfaction_score * 0.5 + utilization_score * 0.3 + experience_score * 0.2)
            
            return min(100, max(0, efficiency_score))
            
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {e}")
            return 70.0
    
    def generate_insights(self, dca_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Generate strengths and improvement suggestions"""
        strengths = []
        improvements = []
        
        try:
            recovery_rate = dca_data.get('averageRecoveryRate', 0)
            resolution_time = dca_data.get('averageResolutionTime', 60)
            sla_compliance = dca_data.get('slaCompliance', 80)
            customer_satisfaction = dca_data.get('customerSatisfactionScore', 3.5)
            total_cases = dca_data.get('totalCasesHandled', 0)
            
            # Analyze recovery rate
            if recovery_rate >= self.benchmarks['excellent_recovery_rate']:
                strengths.append("Excellent recovery rate performance")
            elif recovery_rate >= self.benchmarks['good_recovery_rate']:
                strengths.append("Good recovery rate performance")
            elif recovery_rate < self.benchmarks['average_recovery_rate']:
                improvements.append("Improve recovery strategies and techniques")
            
            # Analyze resolution time
            if resolution_time <= self.benchmarks['excellent_resolution_time']:
                strengths.append("Outstanding case resolution speed")
            elif resolution_time <= self.benchmarks['good_resolution_time']:
                strengths.append("Good case resolution efficiency")
            elif resolution_time > self.benchmarks['average_resolution_time']:
                improvements.append("Reduce average case resolution time")
            
            # Analyze SLA compliance
            if sla_compliance >= self.benchmarks['excellent_sla_compliance']:
                strengths.append("Excellent SLA compliance record")
            elif sla_compliance >= self.benchmarks['good_sla_compliance']:
                strengths.append("Good SLA compliance performance")
            elif sla_compliance < self.benchmarks['average_sla_compliance']:
                improvements.append("Focus on meeting SLA requirements consistently")
            
            # Analyze customer satisfaction
            if customer_satisfaction >= self.benchmarks['excellent_satisfaction']:
                strengths.append("Outstanding customer satisfaction scores")
            elif customer_satisfaction >= self.benchmarks['good_satisfaction']:
                strengths.append("Good customer satisfaction levels")
            elif customer_satisfaction < self.benchmarks['average_satisfaction']:
                improvements.append("Improve customer service and communication")
            
            # Analyze experience
            if total_cases >= 5000:
                strengths.append("Extensive experience with high case volume")
            elif total_cases >= 2000:
                strengths.append("Good experience with substantial case handling")
            elif total_cases < 500:
                improvements.append("Build experience through increased case volume")
            
            # Capacity analysis
            capacity = dca_data.get('capacity', {})
            if capacity:
                max_cases = capacity.get('maxCases', 1000)
                current_cases = capacity.get('currentCases', 0)
                
                if max_cases > 0:
                    utilization = (current_cases / max_cases) * 100
                    if utilization > 95:
                        improvements.append("Consider expanding capacity to handle demand")
                    elif utilization < 50:
                        improvements.append("Optimize capacity utilization")
                    elif 70 <= utilization <= 80:
                        strengths.append("Optimal capacity utilization")
            
            # Specialization analysis
            specializations = dca_data.get('specializations', [])
            if len(specializations) >= 3:
                strengths.append("Diverse specialization portfolio")
            elif len(specializations) == 0:
                improvements.append("Develop specialized expertise in key areas")
            
            # Default messages if no specific insights
            if not strengths:
                strengths.append("Consistent performance across key metrics")
            
            if not improvements:
                improvements.append("Continue maintaining current performance standards")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            strengths = ["Performance data available for analysis"]
            improvements = ["Regular performance monitoring recommended"]
        
        return strengths, improvements
    
    def calculate_overall_score(self, dca_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate all scores and overall rating"""
        try:
            performance_score = self.calculate_performance_score(dca_data)
            reliability_score = self.calculate_reliability_score(dca_data)
            efficiency_score = self.calculate_efficiency_score(dca_data)
            
            # Calculate weighted overall score
            overall_score = (
                performance_score * 0.4 +
                reliability_score * 0.3 +
                efficiency_score * 0.3
            )
            
            return {
                'performance_score': performance_score,
                'reliability_score': reliability_score,
                'efficiency_score': efficiency_score,
                'overall_score': overall_score
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return {
                'performance_score': 50.0,
                'reliability_score': 50.0,
                'efficiency_score': 50.0,
                'overall_score': 50.0
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get model status information"""
        return {
            "loaded": True,
            "model_type": "DCAScorer",
            "benchmarks_count": len(self.benchmarks),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }