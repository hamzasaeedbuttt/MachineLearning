import pandas as pd
import numpy as np
import joblib
from scipy import stats
from typing import Dict, List

def detect_data_drift(current_features: Dict, training_stats_path: str = "model_registry/training_stats.joblib") -> Dict:
    """
    Detect data drift by comparing current stock features to training dataset statistics.
    
    Args:
        current_features: Dictionary with current stock features
            Expected keys: 'return', 'ma5', 'ma10', 'volatility'
        training_stats_path: Path to saved training statistics
    
    Returns:
        Dictionary with drift detection results
    """
    try:
        # Load training statistics
        training_stats = joblib.load(training_stats_path)
        
        drift_results = {
            'has_drift': False,
            'features_analyzed': [],
            'drift_severity': 'none',
            'warnings': []
        }
        
        drift_scores = []
        
        # Analyze each feature
        for feature_name in ['return', 'ma5', 'ma10', 'volatility']:
            if feature_name not in current_features:
                continue
            
            current_value = current_features[feature_name]
            train_mean = training_stats['mean'][feature_name]
            train_std = training_stats['std'][feature_name]
            train_min = training_stats['min'][feature_name]
            train_max = training_stats['max'][feature_name]
            
            # Calculate z-score (how many standard deviations away from mean)
            if train_std > 0:
                z_score = abs((current_value - train_mean) / train_std)
            else:
                z_score = 0
            
            # Check if outside 3 standard deviations (statistical outlier)
            is_outlier = z_score > 3
            
            # Check if outside min/max range
            is_out_of_range = current_value < train_min or current_value > train_max
            
            # Calculate percentile position
            if train_std > 0:
                percentile = stats.norm.cdf((current_value - train_mean) / train_std) * 100
            else:
                percentile = 50
            
            # Determine drift severity
            if is_out_of_range:
                severity = 'high'
                drift_results['has_drift'] = True
            elif z_score > 2:
                severity = 'medium'
                drift_results['has_drift'] = True
            elif z_score > 1.5:
                severity = 'low'
            else:
                severity = 'none'
            
            drift_scores.append({
                'feature': feature_name,
                'current_value': current_value,
                'training_mean': train_mean,
                'training_std': train_std,
                'z_score': z_score,
                'percentile': percentile,
                'is_outlier': is_outlier,
                'is_out_of_range': is_out_of_range,
                'severity': severity,
                'interpretation': _interpret_drift(feature_name, current_value, train_mean, train_std, severity)
            })
            
            if severity != 'none':
                drift_results['warnings'].append(
                    f"{feature_name}: {severity.upper()} drift - {drift_scores[-1]['interpretation']}"
                )
        
        drift_results['features_analyzed'] = drift_scores
        
        # Overall drift severity
        if drift_scores:
            max_severity_score = max([s['z_score'] for s in drift_scores])
            if max_severity_score > 3:
                drift_results['drift_severity'] = 'high'
            elif max_severity_score > 2:
                drift_results['drift_severity'] = 'medium'
            elif max_severity_score > 1.5:
                drift_results['drift_severity'] = 'low'
        
        return drift_results
        
    except Exception as e:
        return {
            'has_drift': False,
            'error': str(e),
            'features_analyzed': [],
            'drift_severity': 'unknown',
            'warnings': [f"Drift detection error: {str(e)}"]
        }

def _interpret_drift(feature_name: str, current_value: float, train_mean: float, train_std: float, severity: str) -> str:
    """Provide human-readable interpretation of drift."""
    
    diff = current_value - train_mean
    diff_pct = (diff / train_mean * 100) if train_mean != 0 else 0
    
    if feature_name == 'return':
        if abs(diff) > train_std * 2:
            if diff > 0:
                return f"Returns are {abs(diff_pct):.1f}% higher than typical - Market may be more volatile"
            else:
                return f"Returns are {abs(diff_pct):.1f}% lower than typical - Market may be more stable"
    elif feature_name == 'volatility':
        if diff > train_std * 2:
            return f"Volatility is {abs(diff_pct):.1f}% higher - Market is more volatile than training period"
        elif diff < -train_std * 2:
            return f"Volatility is {abs(diff_pct):.1f}% lower - Market is more stable than training period"
    elif feature_name in ['ma5', 'ma10']:
        if abs(diff_pct) > 10:
            return f"Moving average is {abs(diff_pct):.1f}% different - Price trend differs from training period"
    
    return f"Value differs from training data average"

def get_drift_summary(drift_results: Dict) -> str:
    """Get a summary message about data drift."""
    if not drift_results.get('has_drift', False):
        return "✅ No significant data drift detected. Stock behavior aligns with training data."
    
    severity = drift_results.get('drift_severity', 'unknown')
    warnings = drift_results.get('warnings', [])
    
    if severity == 'high':
        return f"⚠️ HIGH DRIFT DETECTED: {warnings[0] if warnings else 'Stock behavior significantly differs from training data.'}"
    elif severity == 'medium':
        return f"⚡ MEDIUM DRIFT: {warnings[0] if warnings else 'Stock behavior shows moderate differences from training data.'}"
    else:
        return f"ℹ️ LOW DRIFT: {warnings[0] if warnings else 'Minor differences from training data detected.'}"

