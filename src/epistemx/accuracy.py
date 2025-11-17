from scipy import stats
import numpy as np
import ee
from typing import Dict, List, Tuple, Any, Optional
import logging
from .ee_config import ensure_ee_initialized

# Do not initialize Earth Engine at import time. Initialize when classes are instantiated.

#Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module 7: Thematic Accuracy Assessment
## System Response 7.2 Ground Reference Verification
#Create a class for thematic assesment
class Thematic_Accuracy_Assessment:
    """
    Module 7: Thematic Accuracy Assessment Manager
    Backend processing for land cover classification accuracy evaluation
    """
    
    def __init__(self):
        """
        Initialize the accuracy assessment manager
        Ensure Earth Engine is initialized lazily (avoids import-time failures).
        """
        # Ensure Earth Engine is initialized when first used (raises helpful error if not)
        ensure_ee_initialized()
        
        self.supported_metrics = [
            'overall_accuracy', 'kappa', 'producer_accuracy', 
            'user_accuracy', 'f1_scores', 'confusion_matrix'
        ]
    
    def validate_inputs(self, lcmap: ee.Image, validation_data: ee.FeatureCollection, 
                       class_property: str, scale: int) -> Tuple[bool, Optional[str]]:
        """Validate input parameters for accuracy assessment"""
        try:
            # Check if lcmap has classification band
            band_names = lcmap.bandNames().getInfo()
            if 'classification' not in band_names:
                return False, "Input land cover map must contain a band named 'classification'"
            
            # Check if validation data has the specified class property
            first_feature = validation_data.first()
            properties = first_feature.propertyNames().getInfo()
            if class_property not in properties:
                return False, f"Class property '{class_property}' not found in validation data"
            
            # Validate scale
            if not isinstance(scale, (int, float)) or scale <= 0:
                return False, "Scale must be a positive number"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _calculate_confidence_interval(self, n_correct: int, n_total: int, 
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for overall accuracy using normal approximation"""
        if n_total == 0:
            return 0.0, 0.0
        
        p = n_correct / n_total
        se = np.sqrt((p * (1 - p)) / n_total)
        z = stats.norm.ppf((1 + confidence) / 2)
        margin = z * se
        
        lower = max(0.0, p - margin)
        upper = min(1.0, p + margin)
        
        return lower, upper
    def _calculate_f1_scores(self, producer_accuracy: List[float], 
                           user_accuracy: List[float]) -> List[float]:
        """Calculate F1 scores for each class"""
        f1_scores = []
        
        for producer_acc, user_acc in zip(producer_accuracy, user_accuracy):
            if producer_acc + user_acc > 0:
                f1 = 2 * (producer_acc * user_acc) / (producer_acc + user_acc)
            else:
                f1 = 0.0
            f1_scores.append(f1)
        
        return f1_scores
    
    def _extract_confusion_matrix_data(self, confusion_matrix: ee.ConfusionMatrix) -> Dict[str, Any]:
        """Extract all metrics from Earth Engine confusion matrix"""
        try:
            # Get basic metrics
            overall_accuracy = confusion_matrix.accuracy().getInfo()
            kappa = confusion_matrix.kappa().getInfo()
            
            # Get per-class accuracies
            producers_accuracy_raw = confusion_matrix.producersAccuracy().getInfo()
            consumers_accuracy_raw = confusion_matrix.consumersAccuracy().getInfo()
            
            # Get confusion matrix array
            cm_info = confusion_matrix.getInfo()
            cm_array = cm_info['array'] if isinstance(cm_info, dict) else cm_info
            
            # Flatten accuracy arrays
            producers_accuracy = np.array(producers_accuracy_raw).flatten().tolist()
            consumers_accuracy = np.array(consumers_accuracy_raw).flatten().tolist()
            
            return {
                'overall_accuracy': overall_accuracy,
                'kappa': kappa,
                'producers_accuracy': producers_accuracy,
                'consumers_accuracy': consumers_accuracy,
                'cm_array': cm_array
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract confusion matrix data: {str(e)}")
    
    def run_accuracy_assessment(self, lcmap: ee.Image, validation_data: ee.FeatureCollection,
                               class_property: str, scale: int = 30, 
                               confidence: float = 0.95) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform comprehensive thematic accuracy assessment
        
        Args:
            lcmap: Classified land cover map with 'classification' band
            validation_data: Ground reference validation points
            class_property: Column name containing class IDs in validation data
            scale: Spatial resolution for sampling (meters)
            confidence: Confidence level for accuracy intervals
            
        Returns:
            Tuple of (success, results_dict or error_message)
        """
        try:
            # Validate inputs
            is_valid, error_msg = self.validate_inputs(lcmap, validation_data, class_property, scale)
            if not is_valid:
                return False, {"error": error_msg}
            
            logger.info("Starting accuracy assessment...")
            
            # Sample the classified map at validation points
            validation_sample = lcmap.select('classification').sampleRegions(
                collection=validation_data,
                properties=[class_property],
                scale=scale,
                geometries=False,
                tileScale=4
            )
            
            # Create confusion matrix
            confusion_matrix = validation_sample.errorMatrix(class_property, 'classification')
            
            # Extract all metrics
            cm_data = self._extract_confusion_matrix_data(confusion_matrix)
            
            # Calculate confidence interval
            n_correct = int(np.trace(np.array(cm_data['cm_array'])))
            n_total = int(np.sum(np.array(cm_data['cm_array'])))
            ci_lower, ci_upper = self._calculate_confidence_interval(n_correct, n_total, confidence)
            
            # Calculate F1 scores
            f1_scores = self._calculate_f1_scores(
                cm_data['producers_accuracy'], 
                cm_data['consumers_accuracy']
            )
            
            # Compile final results
            results = {
                'overall_accuracy': cm_data['overall_accuracy'],
                'kappa': cm_data['kappa'],
                'producer_accuracy': cm_data['producers_accuracy'],
                'user_accuracy': cm_data['consumers_accuracy'],
                'f1_scores': f1_scores,
                'confusion_matrix': cm_data['cm_array'],
                'overall_accuracy_ci': (ci_lower, ci_upper),
                'confidence_level': confidence,
                'n_total': n_total,
                'n_correct': n_correct,
                'scale': scale
            }
            
            logger.info("Accuracy assessment completed successfully")
            return True, results
            
        except Exception as e:
            error_msg = f"Accuracy assessment failed: {str(e)}"
            logger.error(error_msg)
            return False, {"error": error_msg}
    
    @staticmethod
    def format_accuracy_summary(results: Dict[str, Any]) -> Dict[str, str]:
        """Format accuracy results for display"""
        if 'error' in results:
            return results
        
        summary = {
            'overall_accuracy': f"{results['overall_accuracy']*100:.2f}%",
            'kappa': f"{results['kappa']:.3f}",
            'confidence_interval': f"{results['overall_accuracy_ci'][0]*100:.2f}% - {results['overall_accuracy_ci'][1]*100:.2f}%",
            'sample_size': str(results['n_total'])
        }
        
        return summary
# 