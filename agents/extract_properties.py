import os
import json
import asyncio
import sys
import time
import re
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv
from models.property_schema import PropertyData
import openai
from openai import AsyncOpenAI
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create cache directory if it doesn't exist
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def normalize_unicode_characters(text: str) -> str:
    """
    Normalize common Unicode characters found in property listings
    to make them more consistent for processing
    """
    # Map of characters to replace
    replacements = {
        '\u2022': '-',  # Replace bullet point (•) with dash
        '\u00b7': '-',  # Replace middle dot (·) with dash
        '\u2013': '-',  # Replace en dash (–) with regular dash
        '\u2014': '-',  # Replace em dash (—) with regular dash
        # We keep the Rupee symbol as is, but document it here
        # '\u20b9': 'Rs.'  # Indian Rupee symbol (₹)
    }
    
    # Apply replacements
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

async def extract_property_listings(markdown_content: str) -> List[str]:
    """Split the markdown content into individual property listings"""
    # Simple pattern that matches text starting with "##" until the next "##" or end of file
    pattern = r"##\s+(.*?)(?=##|\Z)"
    
    # Find all property entries using the pattern
    listings = re.findall(pattern, markdown_content, re.DOTALL)
    
    if listings:
        return [listing.strip() for listing in listings]
    else:
        # If no matches found, return the entire content as one listing
        print("No property listings with '##' headers found. Using entire content.")
        return [markdown_content.strip()]

async def get_cache_path(content: str, schema_json: Dict[str, Any]) -> str:
    """Generate a cache path based on content and schema hash"""
    # Create a hash based on the content and schema
    content_hash = hashlib.md5((content + str(schema_json)).encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"property_data_{content_hash}.json")

async def extract_property_data(listing_text: str, schema_json: Dict[str, Any]) -> Dict[str, Any]:
    """Use LLM to extract structured data from a property listing, with caching"""
    
    # Normalize Unicode characters in the listing text
    normalized_text = normalize_unicode_characters(listing_text)
    
    # Check cache first
    cache_path = await get_cache_path(normalized_text, schema_json)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                print(f"Loading from cache: {os.path.basename(cache_path)}")
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
    
    system_prompt = """You are a real estate data extraction assistant. Your task is to extract property information from text into a structured JSON format. Follow these guidelines:
    
    1. Extract all available information that matches the provided schema
    2. If information is not present in the text, use "Not available" as the value
    3. Return ONLY the JSON object, nothing else
    4. For 'price', include ONLY the amount (e.g. "24.0 L" or "1400000"), NOT as a nested object
    5. All fields should be simple string values, not nested objects with title/type/value
    6. Format all property details consistently
    7. Convert all Unicode characters to their ASCII equivalents when appropriate:
       - Indian Rupee symbol (₹) can be replaced with "Rs." or kept as is
       - Bullet points (•) should be replaced with dashes or similar
       
    Example of the desired format:
    {
      "price": "1400000",
      "property_link": "https://housing.com/buy-130-sqft-residential-plot-in-pendurthi-for-rs-1400000-rid-16875688",
      "plot_area": "130 sq.yd",
      "average_price": "Rs.10.77k/sq.yd",
      "location": "Pendurthi"
      // Other fields
    }
    
    DO NOT use the format with nested objects like {title, type, value} for each field.
    """
    
    user_prompt = f"""Extract property information from the following text into JSON format according to this schema: 
    
    {json.dumps(schema_json, indent=2)}
    
    Here is the property listing text:
    
    {normalized_text}
    
    Respond ONLY with the valid JSON object.
    """
    
    try:
        print("Cache miss - calling OpenAI API...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Can be adjusted based on needs
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        # Get the response content
        response_content = response.choices[0].message.content
        data = json.loads(response_content)
        
        # Process the response to ensure consistent format
        standardized_data = {}
        
        # Check if response has nested 'properties' key
        if "properties" in data:
            data = data["properties"]
        
        # Process each field to ensure consistent format
        for key, value in data.items():
            if isinstance(value, dict):
                # Handle nested dictionaries
                if "amount" in value:
                    # Handle price with currency/amount structure
                    standardized_data[key] = value["amount"]
                elif "value" in value:
                    # Handle fields with title/type/value structure
                    standardized_data[key] = value["value"]
                else:
                    # Any other nested structure, convert to string
                    standardized_data[key] = str(value)
            else:
                # Already a simple value
                standardized_data[key] = value
        
        # Save to cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(standardized_data, f, indent=2)
            
        return standardized_data
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        return {}

async def process_markdown_file(file_path: str, output_path: str):
    """Process a markdown file and extract property data"""
    print(f"Processing {file_path}...")
    
    try:
        # Read the markdown file
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Split into individual property listings
        listings = await extract_property_listings(markdown_content)
        print(f"Found {len(listings)} property listings")
        
        # Get the schema in JSON format
        schema_json = PropertyData.model_json_schema()
        
        # Get current date for scraped_date field
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Ensure output path is in the 'data' directory
        output_path = os.path.join("data", output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Load existing properties if file exists
        existing_properties = []
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_properties = json.load(f)
                print(f"Loaded {len(existing_properties)} existing properties from {output_path}")
            except Exception as e:
                print(f"Error loading existing properties: {str(e)}")
        
        # Process each listing
        new_results = []
        for i, listing in enumerate(listings):
            print(f"Processing listing {i+1}/{len(listings)}...")
            # Extract data using LLM
            property_data = await extract_property_data(listing, schema_json)
            
            # Ensure all schema fields exist with default values
            for field in schema_json["properties"]:
                if field not in property_data:
                    property_data[field] = "Not available"
            
            # Add scraped_date field
            property_data["scraped_date"] = today_date
            
            if property_data:
                new_results.append(property_data)
        
        # Combine new and existing properties
        # Create a set of existing URLs to avoid duplicates
        existing_urls = set()
        for prop in existing_properties:
            url = prop.get("property_link", "")
            if url and url != "Not available":
                existing_urls.add(url)
        
        # Only add non-duplicate new properties
        for prop in new_results:
            url = prop.get("property_link", "")
            # If property has no URL or URL isn't in our set, add it
            if url == "Not available" or url not in existing_urls:
                existing_properties.append(prop)
                if url != "Not available":
                    existing_urls.add(url)
        
        # Save the combined results to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(existing_properties, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(existing_properties)} properties to {output_path}")
        print(f"Added {len(new_results)} new properties")
        return existing_properties
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

async def main():
    print("Property Data Extraction Agent")
    print("-----------------------------")
    
    # Process Housing.com properties
    housing_markdown = "data/housing_properties.md"
    housing_output = "data/housing_properties.json"
    if os.path.exists(housing_markdown):
        await process_markdown_file(housing_markdown, housing_output)
    else:
        print(f"File not found: {housing_markdown}")
    
    # Process MagicBricks properties
    magicbricks_markdown = "data/magicbricks_properties.md"
    magicbricks_output = "data/magicbricks_properties.json"
    if os.path.exists(magicbricks_markdown):
        await process_markdown_file(magicbricks_markdown, magicbricks_output)
    else:
        print(f"File not found: {magicbricks_markdown}")
    
    print("\nExtraction completed!")

if __name__ == "__main__":
    # Fix for Windows asyncio event loop closure issue
    if sys.platform == 'win32':
        # Use WindowsSelectorEventLoopPolicy to avoid ProactorEventLoop issues
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
    
    # Add a small delay before exiting to allow cleanup
    time.sleep(0.5)
