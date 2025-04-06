"""
Dashboard styling components and CSS definitions
"""

# Map legend style for price per sq.yd
PRICE_LEGEND_CSS = """
<style>
.map-legend {
    border-radius: 5px;
    padding: 15px;
    margin-top: 20px;
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(150, 150, 150, 0.2);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.legend-title {
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 15px;
    border-bottom: 1px solid rgba(150, 150, 150, 0.3);
    padding-bottom: 5px;
}
.legend-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}
.legend-color {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    margin-right: 10px;
    display: inline-block;
}
.red-marker { background-color: #e74c3c; }
.orange-marker { background-color: #f39c12; }
.green-marker { background-color: #2ecc71; }
.blue-marker { background-color: #3498db; }
.gray-marker { background-color: #95a5a6; }
</style>
"""

# Price legend HTML
def get_price_legend_html():
    """Return the HTML for the price legend"""
    return f"""{PRICE_LEGEND_CSS}
    <div class="map-legend">
        <div class="legend-title">Price per sq.yd</div>
        <div class="legend-item">
            <span class="legend-color red-marker"></span>
            <span>Above ₹20,000/sq.yd</span>
        </div>
        <div class="legend-item">
            <span class="legend-color orange-marker"></span>
            <span>₹15,000 - ₹20,000/sq.yd</span>
        </div>
        <div class="legend-item">
            <span class="legend-color green-marker"></span>
            <span>₹10,000 - ₹15,000/sq.yd</span>
        </div>
        <div class="legend-item">
            <span class="legend-color blue-marker"></span>
            <span>Below ₹10,000/sq.yd</span>
        </div>
        <div class="legend-item">
            <span class="legend-color gray-marker"></span>
            <span>Price data unavailable</span>
        </div>
    </div>
    """

# Function to determine marker color based on price
def get_marker_color(price_text):
    """Determine marker color based on price per sq.yd"""
    try:
        price_value = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
        
        if price_value > 20000:
            return 'red'
        elif price_value > 15000:
            return 'orange'
        elif price_value > 10000:
            return 'green'
        else:
            return 'blue'
    except:
        return 'gray'
