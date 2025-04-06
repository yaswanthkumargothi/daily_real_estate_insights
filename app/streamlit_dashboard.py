import streamlit as st
import json
import os
import pandas as pd
import asyncio
import sys
import time
import re
import logging
from typing import List, Dict, Any
from collections import defaultdict
from dotenv import load_dotenv
from openai import AsyncOpenAI
from models.property_schema import PropertyData
from utils.location_processor import LocationProcessor
from ui.dashboard_ui import display_dashboard
from agents.property_analysis_agent import display_analysis_ui

# Set page config first - this must be the first Streamlit command
st.set_page_config(
    page_title="Property Investment Dashboard",
    page_icon="🏡",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PropertyDashboard:
    """Generate analytics dashboard for property data"""
    
    def __init__(self):
        self.housing_data = []
        self.magicbricks_data = []
        self.all_properties = []
        self.location_stats = {}
        self.price_ranges = {}
        self.top_properties = []
        self.stats = {
            "total_properties": 0,
            "sources": {"Housing.com": 0, "MagicBricks": 0},
            "locations": {},
            "property_types": {},
            "ownership_types": {},
            "price_ranges": {},
            "area_ranges": {}
        }
        self.location_processor = LocationProcessor()  # Initialize location processor
    
    def load_data(self):
        """Load data from JSON files"""
        try:
            # Get the absolute paths to the JSON files in the 'data' directory
            housing_file = os.path.join(os.path.dirname(__file__), "..", "data", "housing_properties.json")
            magicbricks_file = os.path.join(os.path.dirname(__file__), "..", "data", "magicbricks_properties.json")
            
            # Load Housing.com data
            if os.path.exists(housing_file):
                with open(housing_file, "r", encoding="utf-8") as f:
                    self.housing_data = json.load(f)
                st.sidebar.success(f"Loaded {len(self.housing_data)} properties from Housing.com")
            
            # Load MagicBricks data
            if os.path.exists(magicbricks_file):
                with open(magicbricks_file, "r", encoding="utf-8") as f:
                    self.magicbricks_data = json.load(f)
                st.sidebar.success(f"Loaded {len(self.magicbricks_data)} properties from MagicBricks")
            
            # Combine all properties
            self.all_properties = self.housing_data + self.magicbricks_data
            
            # Ensure all properties have a scraped_date field
            for prop in self.all_properties:
                if "scraped_date" not in prop or not prop["scraped_date"]:
                    prop["scraped_date"] = "Legacy data"  # Mark old data without dates
            
            st.sidebar.info(f"Total {len(self.all_properties)} properties loaded")
            
            # Mark source for each property
            for prop in self.housing_data:
                prop["source"] = "Housing.com"
            for prop in self.magicbricks_data:
                prop["source"] = "MagicBricks"
                
            # Standardize locations in all properties
            for prop in self.all_properties:
                if "location" in prop:
                    original_location = prop["location"]
                    standardized_location = self.location_processor.get_canonical_name(original_location)
                    prop["original_location"] = original_location  # Keep original for reference
                    prop["location"] = standardized_location  # Use standardized location
                
            return len(self.all_properties) > 0
        
        except Exception as e:
            st.sidebar.error(f"Error loading data: {str(e)}")
            import traceback
            st.sidebar.error(traceback.format_exc())
            return False
    
    def generate_basic_stats(self):
        """Generate basic statistics about the properties"""
        if not self.all_properties:
            return "No properties found for analysis"
            
        stats = {
            "total_properties": len(self.all_properties),
            "sources": {
                "Housing.com": len(self.housing_data),
                "MagicBricks": len(self.magicbricks_data)
            },
            "locations": defaultdict(int),
            "property_types": defaultdict(int),
            "ownership_types": defaultdict(int),
            "price_ranges": defaultdict(int),
            "area_ranges": defaultdict(int)
        }
        
        # Process each property
        for prop in self.all_properties:
            # Count by location
            location = prop.get("location", "Unknown")
            stats["locations"][location] += 1
            
            # Count by property type
            prop_type = prop.get("property_type", "Unknown")
            stats["property_types"][prop_type] += 1
            
            # Count by ownership type
            ownership = prop.get("ownership_type", "Unknown")
            stats["ownership_types"][ownership] += 1
            
            # Process price (normalize and categorize)
            price_str = prop.get("price", "0")
            try:
                # Extract numeric value and convert to consistent format
                price_value = self._extract_price_value(price_str)
                
                # Categorize price
                if price_value < 1000000:  # < 10L
                    price_range = "Under 10 Lakhs"
                elif price_value < 3000000:  # 10L - 30L
                    price_range = "10 - 30 Lakhs"
                elif price_value < 5000000:  # 30L - 50L
                    price_range = "30 - 50 Lakhs"
                elif price_value < 10000000:  # 50L - 1Cr
                    price_range = "50 Lakhs - 1 Crore"
                else:  # > 1Cr
                    price_range = "Above 1 Crore"
                
                stats["price_ranges"][price_range] += 1
                
            except (ValueError, TypeError) as e:
                st.warning(f"Error processing price '{price_str}': {e}")
            
            # Process area (normalize and categorize)
            area_str = prop.get("plot_area", "0")
            try:
                # Extract numeric value and unit
                area_value, area_unit = self._extract_area_value_and_unit(area_str)
                
                # Convert to standard unit (sq.yd) if needed
                if area_unit.lower() in ["sq.ft", "sqft", "sq ft", "sft"]:
                    area_value = area_value / 9  # Convert sq.ft to sq.yd
                
                # Categorize area
                if area_value < 100:
                    area_range = "Under 100 sq.yd"
                elif area_value < 200:
                    area_range = "100-200 sq.yd"
                elif area_value < 300:
                    area_range = "200-300 sq.yd"
                elif area_value < 500:
                    area_range = "300-500 sq.yd"
                else:
                    area_range = "Above 500 sq.yd"
                
                stats["area_ranges"][area_range] += 1
                
            except (ValueError, TypeError, IndexError) as e:
                st.warning(f"Error processing area '{area_str}': {e}")
        
        self.stats = stats
        return stats
    
    def _extract_price_value(self, price_str):
        """Extract numerical price value from various string formats"""
        if not price_str or price_str == "Not available":
            return 0
            
        if isinstance(price_str, (int, float)):
            return float(price_str)
            
        # Convert to string and clean up
        price_str = str(price_str).strip()
        
        # Handle the Rupee symbol
        price_str = price_str.replace('₹', '').replace('\u20b9', '')
        
        # Remove commas and other non-numeric characters except decimal point and letters L, l, C, c
        price_str = ''.join(c for c in price_str if c.isdigit() or c == '.' or c.lower() in ['l', 'c', 'a', 'r'])
        
        # Check for Lac/Lakh/L suffix
        if any(suffix in price_str.lower() for suffix in ['lac', 'lakh', 'l']):
            numeric_part = re.search(r'(\d+\.?\d*)', price_str)
            if numeric_part:
                return float(numeric_part.group(1)) * 100000
        
        # Check for Crore/Cr suffix
        if any(suffix in price_str.lower() for suffix in ['cr', 'crore']):
            numeric_part = re.search(r'(\d+\.?\d*)', price_str)
            if numeric_part:
                return float(numeric_part.group(1)) * 10000000
        
        # Otherwise just extract the numeric part
        numeric_part = re.search(r'(\d+\.?\d*)', price_str)
        if numeric_part:
            return float(numeric_part.group(1))
        
        raise ValueError(f"Could not extract price from '{price_str}'")
    
    def _extract_area_value_and_unit(self, area_str):
        """Extract numerical area value and unit from string"""
        if not area_str or area_str == "Not available":
            return 0, "sq.yd"
        
        # Convert to string
        area_str = str(area_str).strip()
        
        # First try to find a numeric value followed by a unit
        area_match = re.search(r'(\d+\.?\d*)\s*(sq\.?[a-zA-Z]*|sqft|sq ft)', area_str, re.IGNORECASE)
        
        if area_match:
            value = float(area_match.group(1))
            unit = area_match.group(2)
            return value, unit
        
        # If that failed, just try to extract any numeric value
        numeric_part = re.search(r'(\d+\.?\d*)', area_str)
        if numeric_part:
            value = float(numeric_part.group(1))
            # Try to determine unit from remaining text
            if any(unit in area_str.lower() for unit in ["sq.yd", "sq yd", "sqyd", "yard"]):
                unit = "sq.yd"
            elif any(unit in area_str.lower() for unit in ["sq.ft", "sq ft", "sqft", "sft", "feet"]):
                unit = "sq.ft"
            else:
                unit = "sq.yd"  # Default assumption
            return value, unit
            
        raise ValueError(f"Could not extract area from '{area_str}'")
    
    def generate_location_analysis(self):
        """Generate detailed analysis by location"""
        locations = {}
        
        for location, count in self.stats["locations"].items():
            if location == "Unknown" or location == "Not available":
                continue
                
            # Get all properties in this location
            properties_in_location = [p for p in self.all_properties if p.get("location") == location]
            
            # Calculate average price
            prices = []
            for prop in properties_in_location:
                try:
                    price_value = self._extract_price_value(prop.get("price", "0"))
                    if price_value > 0:
                        prices.append(price_value)
                except (ValueError, TypeError):
                    continue
            
            avg_price = sum(prices) / len(prices) if prices else 0
            
            # Calculate average price per sq.yd
            price_per_area = []
            for prop in properties_in_location:
                try:
                    # Extract price
                    price_value = self._extract_price_value(prop.get("price", "0"))
                    
                    # Extract area and convert to sq.yd if needed
                    area_value, area_unit = self._extract_area_value_and_unit(prop.get("plot_area", "0"))
                    if area_unit.lower() in ["sq.ft", "sqft", "sq ft", "sft"]:
                        area_value = area_value / 9  # Convert sq.ft to sq.yd
                    
                    if area_value > 0:
                        price_per_area.append(price_value / area_value)
                except (ValueError, TypeError, IndexError, ZeroDivisionError):
                    continue
            
            avg_price_per_area = sum(price_per_area) / len(price_per_area) if price_per_area else 0
            
            locations[location] = {
                "property_count": count,
                "average_price": avg_price,
                "average_price_formatted": self._format_price(avg_price),
                "average_price_per_sqyd": avg_price_per_area,
                "average_price_per_sqyd_formatted": f"₹{avg_price_per_area:.2f}",
                "property_types": {},
                "sample_properties": [p["title"] for p in properties_in_location[:3]]
            }
            
            # Count property types in this location
            prop_types = {}
            for prop in properties_in_location:
                prop_type = prop.get("property_type", "Unknown")
                if prop_type not in prop_types:
                    prop_types[prop_type] = 0
                prop_types[prop_type] += 1
            
            locations[location]["property_types"] = prop_types
        
        self.location_stats = locations
        return locations
    
    def _format_price(self, price):
        """Format price in Indian numbering system"""
        if price >= 10000000:  # 1 Crore+
            return f"₹{price/10000000:.2f} Cr"
        elif price >= 100000:  # 1 Lakh+
            return f"₹{price/100000:.2f} L"
        else:
            return f"₹{price:.2f}"
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def load_and_process_data(_self, force_refresh=False):
        """Load and process data with caching"""
        if not _self.load_data():
            return False, "Failed to load data"
        
        # Generate basic statistics
        _self.generate_basic_stats()
        
        # Generate location analysis
        _self.generate_location_analysis()
        
        return True, "Data processed successfully"
    
    async def get_top_properties(self):
        """
        Legacy method maintained for compatibility
        The analysis is now handled by the PropertyAnalysisAgent
        """
        return []

    async def process_data(self):
        """Generate all dashboard data asynchronously"""
        if not self.load_data():
            if 'streamlit' in sys.modules:
                st.error("No property data found for analysis")
            else:
                print("No property data found for analysis")
            return False
        
        try:
            # Check if running in Streamlit context
            in_streamlit = 'streamlit' in sys.modules and hasattr(st, 'status')
            
            if in_streamlit:
                with st.status("Processing property data...") as status:
                    status.write("Generating basic statistics...")
                    self.generate_basic_stats()
                    
                    status.write("Analyzing locations...")
                    self.generate_location_analysis()
                    
                    status.write("Finding top property recommendations...")
                    await self.get_top_properties()
                    
                    status.update(label="Data processing complete!", state="complete")
            else:
                # Fallback for non-Streamlit context
                print("Generating basic statistics...")
                self.generate_basic_stats()
                
                print("Analyzing locations...")
                self.generate_location_analysis()
                
                print("Finding top property recommendations...")
                await self.get_top_properties()
                
                print("Data processing complete!")
            
            return True
        except Exception as e:
            if 'streamlit' in sys.modules:
                st.error(f"An error occurred: {str(e)}")
            else:
                print(f"An error occurred: {str(e)}")
            return False

    def get_location_coordinates(self):
        """Get coordinates for locations using location processor"""
        # Get all locations from properties
        all_locations = set(prop.get("location", "Unknown") for prop in self.all_properties)
        all_locations.discard("Unknown")
        all_locations.discard("Not available")
        
        # Initialize location data dict
        location_coords = {}
        
        # Get coordinates for each location
        for location in all_locations:
            lat, lon = self.location_processor.get_coordinates(location)
            if lat is not None and lon is not None:
                location_coords[location] = {"lat": lat, "lon": lon}
            else:
                # Skip locations with unknown coordinates instead of generating random ones
                
                logging.basicConfig(level=logging.WARNING)
                logger = logging.getLogger(__name__)
                logger.warning(f"No accurate coordinates available for {location} - excluding from map")
                continue
        
        return location_coords
    
    def get_all_scraped_dates(self):
        """Get list of all unique scraped dates in the dataset"""
        dates = set()
        for prop in self.all_properties:
            scraped_date = prop.get("scraped_date")
            if scraped_date and scraped_date != "Not available":
                dates.add(scraped_date)
        
        # Return sorted list of dates from oldest to newest
        return sorted(list(dates))
    
    def generate_map_data(self, date_filter=None):
        """
        Generate data for the map visualization using location coordinates
        Optional date_filter to show only properties from a specific date
        """
        map_data = []
        
        # Get coordinates using a more reliable method
        location_coords = self.get_location_coordinates()
        
        print(f"Found {len(self.location_stats)} locations in stats")
        print(f"Found {len(location_coords)} locations with coordinates")
        
        # Filter properties by date if specified
        filtered_properties = self.all_properties
        if date_filter:
            filtered_properties = [
                prop for prop in self.all_properties 
                if prop.get("scraped_date") == date_filter
            ]
            print(f"Filtered to {len(filtered_properties)} properties from {date_filter}")
        
        # Group all properties by standardized location first
        location_properties = {}
        for prop in filtered_properties:
            loc = prop.get("location", "Unknown")
            if loc not in ["Unknown", "Not available"]:
                if loc not in location_properties:
                    location_properties[loc] = []
                location_properties[loc].append(prop)
        
        # Process each location in the stats based on filtered properties
        for location, props in location_properties.items():
            if location in ["Unknown", "Not available"]:
                continue
                
            if location in location_coords:
                # Calculate stats for filtered properties
                count = len(props)
                
                # Calculate average price
                prices = []
                price_per_area = []
                for prop in props:
                    try:
                        price_value = self._extract_price_value(prop.get("price", "0"))
                        if price_value > 0:
                            prices.append(price_value)
                            
                            # Calculate price per area
                            area_value, area_unit = self._extract_area_value_and_unit(prop.get("plot_area", "0"))
                            if area_unit.lower() in ["sq.ft", "sqft", "sq ft", "sft"]:
                                area_value = area_value / 9  # Convert sq.ft to sq.yd
                            if area_value > 0:
                                price_per_area.append(price_value / area_value)
                    except (ValueError, TypeError, IndexError, ZeroDivisionError):
                        continue
                
                avg_price = sum(prices) / len(prices) if prices else 0
                avg_price_per_area = sum(price_per_area) / len(price_per_area) if price_per_area else 0
                
                # Create sample properties with dates
                sample_properties = []
                for prop in props[:2]:
                    sample_properties.append({
                        "title": prop.get("title", "Unknown property"),
                        "date": prop.get("scraped_date", "Unknown date")
                    })
                
                # Ensure we have valid coordinates
                if (isinstance(location_coords[location].get("lat"), (int, float)) and 
                    isinstance(location_coords[location].get("lon"), (int, float))):
                    
                    # Prepare data for the map
                    map_data.append({
                        "location": location,
                        "lat": location_coords[location]["lat"],
                        "lon": location_coords[location]["lon"],
                        "property_count": count,
                        "avg_price": self._format_price(avg_price),
                        "avg_price_per_sqyd": f"₹{avg_price_per_area:.2f}",
                        "sample_properties": sample_properties
                    })
                    print(f"Added {location} to map data with coords: {location_coords[location]}")
            else:
                print(f"Skipping {location} - no accurate coordinates available")
                
        print(f"Generated map data for {len(map_data)} locations")
        return map_data

async def process_data_async(dashboard: PropertyDashboard):
    """Process data asynchronously without updating the UI"""
    success, _ = dashboard.load_and_process_data(force_refresh=st.session_state.get('refresh_data', False))
    
    if success:
        # Get top property recommendations
        await dashboard.get_top_properties()
        return True
    else:
        return False

def main():
    """Main function to run the dashboard"""
    st.sidebar.title("Property Dashboard")
    st.sidebar.info("This dashboard analyzes property data from multiple sources.")
    
    # Add refresh button to sidebar to force reload data
    if st.sidebar.button("Refresh Data"):
        st.session_state['refresh_data'] = True
        st.cache_data.clear()
        st.rerun()
    else:
        st.session_state['refresh_data'] = False

    # Create dashboard instance
    dashboard = PropertyDashboard()
    
    # Show a spinner while loading data
    with st.spinner("Loading and processing property data..."):
        # Run async processing in a way compatible with Streamlit
        success = asyncio.run(process_data_async(dashboard))
    
    if success:
        display_dashboard(dashboard)
    else:
        st.error("Failed to process property data. Check if JSON files exist and are valid.")

if __name__ == "__main__":
    # Fix for Windows asyncio event loop closure issues
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    main()
    time.sleep(0.5)  # Small delay to avoid event loop errors
