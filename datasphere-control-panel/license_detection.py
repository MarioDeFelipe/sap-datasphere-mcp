#!/usr/bin/env python3
"""
License Detection and Feature Management for SAP Catalog Integrator
Determines available SAP capabilities based on customer licensing
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    DATASPHERE_ONLY = "datasphere_only"
    DATASPHERE_BDC = "datasphere_bdc"
    NONE = "none"

@dataclass
class FeatureAvailability:
    """Defines which features are available based on licensing"""
    
    # Datasphere Core Features
    datasphere_catalog: bool = False
    datasphere_sync: bool = False
    datasphere_viewer: bool = False
    datasphere_query_gen: bool = False
    
    # BDC Enhanced Features
    bdc_data_products: bool = False
    bdc_data_sharing: bool = False
    bdc_api_management: bool = False
    bdc_cross_lineage: bool = False
    bdc_governance: bool = False
    
    # AWS Integration (available with Datasphere)
    aws_glue_sync: bool = False
    aws_athena_queries: bool = False
    aws_quicksight_prep: bool = False

class LicenseDetector:
    """Detects available SAP licenses and determines feature availability"""
    
    def __init__(self):
        self.datasphere_available = False
        self.bdc_available = False
        self.license_type = LicenseType.NONE
        self.features = FeatureAvailability()
        
    def detect_licenses(self) -> LicenseType:
        """Detect available SAP licenses"""
        
        # Check Datasphere availability
        self.datasphere_available = self._check_datasphere_access()
        
        # Check BDC availability
        self.bdc_available = self._check_bdc_access()
        
        # Determine license type
        if self.datasphere_available and self.bdc_available:
            self.license_type = LicenseType.DATASPHERE_BDC
        elif self.datasphere_available:
            self.license_type = LicenseType.DATASPHERE_ONLY
        else:
            self.license_type = LicenseType.NONE
            
        # Set feature availability
        self.features = self._get_feature_availability()
        
        logger.info(f"Detected license type: {self.license_type.value}")
        return self.license_type
    
    def _check_datasphere_access(self) -> bool:
        """Check if Datasphere API is accessible"""
        try:
            # In real implementation, test Datasphere API connectivity
            # For now, assume available (since we have working integration)
            return True
        except Exception as e:
            logger.warning(f"Datasphere access check failed: {e}")
            return False
    
    def _check_bdc_access(self) -> bool:
        """Check if BDC SDK is accessible"""
        try:
            # Test BDC SDK availability
            # For now, return False until SDK installation is resolved
            return False
        except Exception as e:
            logger.warning(f"BDC access check failed: {e}")
            return False
    
    def _get_feature_availability(self) -> FeatureAvailability:
        """Determine feature availability based on detected licenses"""
        
        features = FeatureAvailability()
        
        if self.datasphere_available:
            # Datasphere core features
            features.datasphere_catalog = True
            features.datasphere_sync = True
            features.datasphere_viewer = True
            features.datasphere_query_gen = True
            
            # AWS integration features
            features.aws_glue_sync = True
            features.aws_athena_queries = True
            features.aws_quicksight_prep = True
        
        if self.bdc_available:
            # BDC enhanced features
            features.bdc_data_products = True
            features.bdc_data_sharing = True
            features.bdc_api_management = True
            features.bdc_cross_lineage = True
            features.bdc_governance = True
        
        return features
    
    def get_license_status(self) -> Dict[str, Any]:
        """Get comprehensive license status information"""
        
        return {
            "license_type": self.license_type.value,
            "datasphere_available": self.datasphere_available,
            "bdc_available": self.bdc_available,
            "features": {
                # Datasphere features
                "datasphere_catalog": self.features.datasphere_catalog,
                "datasphere_sync": self.features.datasphere_sync,
                "datasphere_viewer": self.features.datasphere_viewer,
                "datasphere_query_gen": self.features.datasphere_query_gen,
                
                # BDC features
                "bdc_data_products": self.features.bdc_data_products,
                "bdc_data_sharing": self.features.bdc_data_sharing,
                "bdc_api_management": self.features.bdc_api_management,
                "bdc_cross_lineage": self.features.bdc_cross_lineage,
                "bdc_governance": self.features.bdc_governance,
                
                # AWS features
                "aws_glue_sync": self.features.aws_glue_sync,
                "aws_athena_queries": self.features.aws_athena_queries,
                "aws_quicksight_prep": self.features.aws_quicksight_prep
            },
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> Dict[str, str]:
        """Get recommendations based on current license status"""
        
        recommendations = {}
        
        if self.license_type == LicenseType.DATASPHERE_ONLY:
            recommendations["upgrade"] = (
                "Consider adding SAP Business Data Cloud for advanced data sharing, "
                "API management, and enterprise governance capabilities."
            )
            recommendations["current_value"] = (
                "You have full access to Datasphere catalog management and AWS integration. "
                "Perfect for data analytics and cloud migration scenarios."
            )
        
        elif self.license_type == LicenseType.DATASPHERE_BDC:
            recommendations["optimization"] = (
                "You have access to the complete SAP data ecosystem. "
                "Leverage both Datasphere and BDC for maximum data value."
            )
            recommendations["advanced_features"] = (
                "Explore cross-platform data lineage and enterprise data product management "
                "to maximize your investment."
            )
        
        elif self.license_type == LicenseType.NONE:
            recommendations["getting_started"] = (
                "Contact Ailien Studio to set up your SAP Datasphere integration. "
                "Start with core catalog management and AWS synchronization."
            )
        
        return recommendations

def get_ui_config(license_detector: LicenseDetector) -> Dict[str, Any]:
    """Generate UI configuration based on license detection"""
    
    features = license_detector.features
    
    # Define navigation structure
    navigation = {
        "datasphere": {
            "label": "SAP Datasphere",
            "available": license_detector.datasphere_available,
            "items": [
                {"id": "catalog", "label": "Asset Catalog", "available": features.datasphere_catalog},
                {"id": "viewer", "label": "Data Viewer", "available": features.datasphere_viewer},
                {"id": "sync", "label": "AWS Glue Sync", "available": features.datasphere_sync},
                {"id": "queries", "label": "Query Generator", "available": features.datasphere_query_gen}
            ]
        },
        "bdc": {
            "label": "Business Data Cloud",
            "available": license_detector.bdc_available,
            "items": [
                {"id": "products", "label": "Data Products", "available": features.bdc_data_products},
                {"id": "sharing", "label": "Data Sharing", "available": features.bdc_data_sharing},
                {"id": "apis", "label": "API Management", "available": features.bdc_api_management},
                {"id": "lineage", "label": "Cross-Platform Lineage", "available": features.bdc_cross_lineage},
                {"id": "governance", "label": "Governance", "available": features.bdc_governance}
            ]
        },
        "aws": {
            "label": "AWS Integration",
            "available": license_detector.datasphere_available,
            "items": [
                {"id": "glue", "label": "Glue Tables", "available": features.aws_glue_sync},
                {"id": "athena", "label": "Athena Queries", "available": features.aws_athena_queries},
                {"id": "quicksight", "label": "QuickSight Prep", "available": features.aws_quicksight_prep}
            ]
        }
    }
    
    # Define feature cards for dashboard
    feature_cards = [
        {
            "id": "datasphere_catalog",
            "title": "Data Catalog",
            "description": "Browse and manage your Datasphere assets",
            "license_required": "Datasphere",
            "available": features.datasphere_catalog,
            "url": "/catalog",
            "category": "core"
        },
        {
            "id": "aws_integration",
            "title": "AWS Integration",
            "description": "Synchronize metadata to AWS Glue and analytics services",
            "license_required": "Datasphere",
            "available": features.aws_glue_sync,
            "url": "/glue",
            "category": "core"
        },
        {
            "id": "data_viewer",
            "title": "Data Viewer",
            "description": "Explore and sample your data assets",
            "license_required": "Datasphere",
            "available": features.datasphere_viewer,
            "url": "/data",
            "category": "core"
        },
        {
            "id": "bdc_products",
            "title": "Data Products",
            "description": "Create and manage enterprise data products",
            "license_required": "Business Data Cloud",
            "available": features.bdc_data_products,
            "url": "/bdc/products",
            "category": "enhanced"
        },
        {
            "id": "bdc_sharing",
            "title": "Data Sharing",
            "description": "Share data across organizations securely",
            "license_required": "Business Data Cloud",
            "available": features.bdc_data_sharing,
            "url": "/bdc/sharing",
            "category": "enhanced"
        },
        {
            "id": "bdc_apis",
            "title": "API Management",
            "description": "Publish and manage data APIs",
            "license_required": "Business Data Cloud",
            "available": features.bdc_api_management,
            "url": "/bdc/apis",
            "category": "enhanced"
        }
    ]
    
    return {
        "license_type": license_detector.license_type.value,
        "navigation": navigation,
        "feature_cards": feature_cards,
        "license_status": license_detector.get_license_status(),
        "show_upgrade_prompts": license_detector.license_type == LicenseType.DATASPHERE_ONLY
    }

# Example usage
if __name__ == "__main__":
    detector = LicenseDetector()
    license_type = detector.detect_licenses()
    
    print(f"Detected License: {license_type.value}")
    print(f"Datasphere Available: {detector.datasphere_available}")
    print(f"BDC Available: {detector.bdc_available}")
    
    ui_config = get_ui_config(detector)
    print(f"UI Configuration: {ui_config}")