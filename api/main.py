from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Real Estate Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_property_data(source: str) -> List[dict]:
    file_path = f"data/{source}_properties.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.get("/api/properties/{source}")
async def get_properties(
    source: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None
):
    """Get properties with optional filters"""
    if source not in ["housing", "magicbricks"]:
        raise HTTPException(status_code=400, detail="Invalid source")
    
    properties = load_property_data(source)
    
    # Apply filters
    if min_price is not None or max_price is not None or location:
        filtered_properties = []
        for prop in properties:
            price_str = prop.get("price", "0").replace("L", "00000").replace(",", "")
            try:
                price = float(''.join(filter(str.isdigit, price_str)))
            except ValueError:
                continue
                
            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue
            if location and location.lower() not in prop.get("location", "").lower():
                continue
                
            filtered_properties.append(prop)
        return filtered_properties
    
    return properties

@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    stats = {
        "total_properties": 0,
        "sources": {},
        "last_updated": None
    }
    
    for source in ["housing", "magicbricks"]:
        properties = load_property_data(source)
        stats["sources"][source] = len(properties)
        stats["total_properties"] += len(properties)
        
        # Get last updated date
        if properties:
            last_date = max(p.get("scraped_date", "1900-01-01") for p in properties)
            if not stats["last_updated"] or last_date > stats["last_updated"]:
                stats["last_updated"] = last_date
    
    return stats

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": str(datetime.now())}