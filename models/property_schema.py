from pydantic import BaseModel, Field
from typing import Optional

class PropertyData(BaseModel):
    """Schema for property data"""
    price: Optional[str] = Field(None, description="Property price")
    property_link: Optional[str] = Field(None, description="URL link to property listing")
    plot_area: Optional[str] = Field(None, description="Plot area with units")
    average_price: Optional[str] = Field(None, description="Average price per sq.ft or sq.yd")
    location: Optional[str] = Field(None, description="Location of the property")
    property_type: Optional[str] = Field(None, description="Type of property")
    descripion: Optional[str] = Field(None, description="Description of the property")
    title: Optional[str] = Field(None, description="Title of the property listing")
    posted_on: Optional[str] = Field(None, description="When the listing was posted")
    ownership_type: Optional[str] = Field(None, description="Type of ownership")
    dimensions: Optional[str] = Field(None, description="Dimensions of the plot")
    facing: Optional[str] = Field(None, description="Direction the property is facing")
    amenities: Optional[str] = Field(None, description="Amenities available")
    transaction_type: Optional[str] = Field(None, description="Type of transaction (New, Resale)")
    scraped_date: Optional[str] = Field("Legacy data", description="Date when the property was scraped")
