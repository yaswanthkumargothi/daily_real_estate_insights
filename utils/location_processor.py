import json
import os
import re
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LocationProcessor")

class LocationProcessor:
    """
    Simple location processor that loads location coordinates from JSON
    and standardizes location names to just the village/locality name
    """
    
    def __init__(self, coordinates_file="../data/location_coordinates.json"):
        """Initialize with path to coordinates file"""
        self.coordinates_file = os.path.join(os.path.dirname(__file__), coordinates_file)
        self.location_data = {}
        self.location_aliases = {}  # Maps aliases to canonical names
        self.load_location_data()
    
    def load_location_data(self) -> None:
        """Load location data from file"""
        try:
            if os.path.exists(self.coordinates_file):
                with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                    file_content = f.read().strip()
                    if file_content:  # Check if file is not empty
                        self.location_data = json.loads(file_content)
                        logger.info(f"Loaded {len(self.location_data)} locations from {self.coordinates_file}")
                    else:
                        logger.warning(f"Coordinates file {self.coordinates_file} is empty.")
                        self.location_data = {}
            else:
                logger.warning(f"Coordinates file {self.coordinates_file} not found.")
                self.location_data = {}
        except Exception as e:
            logger.error(f"Error loading location data: {str(e)}")
            self.location_data = {}
    
    def standardize_location_name(self, location: str) -> str:
        """
        Standardize location name by removing district and keeping only village/locality
        """
        if not location or location.lower() in ["unknown", "not available"]:
            return "Unknown"
        
        # Remove ", Visakhapatnam" suffix
        location = re.sub(r',\s*Visakhapatnam\s*$', '', location, flags=re.IGNORECASE)
        
        # Remove other common suffixes
        location = re.sub(r',\s*Andhra Pradesh\s*$', '', location, flags=re.IGNORECASE)
        location = re.sub(r',\s*India\s*$', '', location, flags=re.IGNORECASE)
        
        # Remove any remaining commas and get the first part (village name only)
        parts = location.split(',')
        village_name = parts[0].strip()
        
        return village_name
    
    def get_canonical_name(self, location: str) -> str:
        """Get the canonical (standardized) name for a location"""
        if not location or location.lower() in ["unknown", "not available"]:
            return "Unknown"
        
        # Standardize the input name to get just the village name
        return self.standardize_location_name(location)
    
    def get_coordinates(self, location: str) -> Tuple[float, float]:
        """
        Get coordinates for a location from the JSON file
        Returns (latitude, longitude) or (None, None) if not found
        """
        # Standardize to get village name only
        canonical_name = self.get_canonical_name(location)
        
        # Check if we have coordinates for this location
        if canonical_name in self.location_data:
            coords = self.location_data[canonical_name]
            return coords["lat"], coords["lon"]
        
        logger.warning(f"No coordinates found for {canonical_name}")
        return None, None

# Example usage
if __name__ == "__main__":
    processor = LocationProcessor()
    
    # Test location standardization
    test_locations = [
        "Duvvada",
        "Duvvada, Visakhapatnam",
        "Pendurthi",
        "Pendurthi, Visakhapatnam",
        "Unknown"
    ]
    
    print("\nLocation standardization tests:")
    for loc in test_locations:
        canonical = processor.get_canonical_name(loc)
        lat, lon = processor.get_coordinates(canonical)
        print(f"{loc} -> {canonical} at ({lat}, {lon})")
