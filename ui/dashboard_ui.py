"""
Dashboard UI components and visualization functions
"""
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from ui.dashboard_styles import get_price_legend_html, get_marker_color
from agents.property_analysis_agent import display_analysis_ui

def display_summary_stats(dashboard):
    """Display summary statistics in a multi-column layout"""
    st.header("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Properties", dashboard.stats["total_properties"])
    
    with col2:
        st.metric("From Housing.com", dashboard.stats["sources"]["Housing.com"])
    
    with col3:
        st.metric("From MagicBricks", dashboard.stats["sources"]["MagicBricks"])
        
    with col4:
        st.metric("Locations Covered", len(dashboard.stats["locations"]))

def display_distribution_charts(dashboard):
    """Display property distribution charts"""
    st.header("Property Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_price_distribution(dashboard)
    
    with col2:
        display_area_distribution(dashboard)

def display_price_distribution(dashboard):
    """Display price range distribution chart"""
    st.subheader("Price Range Distribution")
    
    # Define the correct order for price ranges
    price_range_order = [
        "Under 10 Lakhs",
        "10 - 30 Lakhs",
        "30 - 50 Lakhs",
        "50 Lakhs - 1 Crore",
        "Above 1 Crore"
    ]
    
    # Create data for price ranges
    price_data = []
    for price_range in price_range_order:
        count = dashboard.stats["price_ranges"].get(price_range, 0)
        price_data.append({
            'Price Range': price_range,
            'Count': count
        })
    
    # Convert to DataFrame with categorical type to maintain order
    price_df = pd.DataFrame(price_data)
    price_df['Price Range'] = pd.Categorical(
        price_df['Price Range'], 
        categories=price_range_order, 
        ordered=True
    )
    
    # Display the chart
    st.bar_chart(price_df.set_index('Price Range'))
    
    # Show the raw data in a table for verification
    with st.expander("Price Range Details"):
        st.dataframe(price_df, use_container_width=True)

def display_area_distribution(dashboard):
    """Display plot area distribution chart"""
    st.subheader("Plot Area Distribution")
    
    # Define the correct order for area ranges
    area_range_order = [
        "Under 100 sq.yd",
        "100-200 sq.yd",
        "200-300 sq.yd",
        "300-500 sq.yd",
        "Above 500 sq.yd"
    ]
    
    # Create data for area ranges
    area_data = []
    for area_range in area_range_order:
        count = dashboard.stats["area_ranges"].get(area_range, 0)
        area_data.append({
            'Area Range': area_range,
            'Count': count
        })
    
    # Convert to DataFrame with categorical type to maintain order
    area_df = pd.DataFrame(area_data)
    area_df['Area Range'] = pd.Categorical(
        area_df['Area Range'], 
        categories=area_range_order, 
        ordered=True
    )
    
    # Display the chart
    st.bar_chart(area_df.set_index('Area Range'))
    
    # Show the raw data in a table for verification
    with st.expander("Area Range Details"):
        st.dataframe(area_df, use_container_width=True)

def display_location_analysis(dashboard):
    """Display location analysis section with map and table views"""
    st.header("Location Analysis")
    
    # Create DataFrame for locations
    location_data = []
    for loc, data in dashboard.location_stats.items():
        if loc == "Unknown" or loc == "Not available":
            continue
            
        location_data.append({
            'Location': loc,
            'Property Count': data['property_count'],
            'Average Price': data['average_price_formatted'],
            'Price/sq.yd': data['average_price_per_sqyd_formatted']
        })
    
    location_df = pd.DataFrame(location_data)
    
    if not location_df.empty:
        # Create tabs for different location views
        loc_tab1, loc_tab2 = st.tabs(["Map View", "Table View"])
        
        with loc_tab1:
            display_location_map(dashboard, location_df)
        
        with loc_tab2:
            display_location_table(location_df)
    else:
        st.warning("No location data available for analysis")

def display_location_map(dashboard, location_df):
    """Display the location map with markers"""
    st.subheader("Property Locations Map")
    
    # Add date filter controls - make them more prominent
    all_dates = dashboard.get_all_scraped_dates()
    
    # Create date filter with a better UI placement
    if all_dates:
        # Create a container with a border for better visibility
        date_filter_container = st.container()
        with date_filter_container:
            # Show date filter only if we have more than just "Legacy data"
            if len(all_dates) > 1 or (len(all_dates) == 1 and all_dates[0] != "Legacy data"):
                st.write("### Filter properties by date:")
                
                # Add "All dates" option at the beginning
                filter_dates = ["All dates"] + all_dates
                
                # Use a more prominent selectbox with a column layout
                col1, col2 = st.columns([1, 2])
                with col1:
                    selected_date = st.selectbox(
                        "Select date:", 
                        filter_dates,
                        index=0,
                        key="date_filter"
                    )
                with col2:
                    if selected_date != "All dates":
                        st.info(f"Showing properties scraped on {selected_date}")
                    else:
                        st.info("Showing properties from all dates")
            else:
                # Only legacy data, don't show filter
                selected_date = "All dates"
    else:
        selected_date = "All dates"
    
    # Generate map data - with error handling
    try:
        # Pass the selected date to filter the map data
        map_data = dashboard.generate_map_data(date_filter=None if selected_date == "All dates" else selected_date)
        
        if map_data and len(map_data) > 0:
            # Create a two-column layout for map and legend
            map_col, legend_col = st.columns([3, 1])
            
            with map_col:
                # Create a map centered on Visakhapatnam
                m = folium.Map(location=[17.7384, 83.2627], zoom_start=10)
                
                # Add marker clusters
                marker_cluster = MarkerCluster().add_to(m)
                
                # Add markers for each location
                for item in map_data:
                    # Create popup content
                    html = f"""
                    <div style="min-width: 200px; max-width: 300px;">
                        <h4 style="color:#2C3E50;">{item['location']}</h4>
                        <div><strong>Properties:</strong> {item['property_count']}</div>
                        <div><strong>Avg Price:</strong> {item['avg_price']}</div>
                        <div><strong>Price/sq.yd:</strong> {item['avg_price_per_sqyd']}</div>
                    """
                    
                    # Add sample properties if available
                    if item['sample_properties']:
                        html += "<div><strong>Sample Properties:</strong><ul>"
                        for prop_info in item['sample_properties']:
                            prop_title = prop_info["title"]
                            prop_date = prop_info.get("date", "Unknown date")
                            html += f"<li>{prop_title} ({prop_date})</li>"
                        html += "</ul></div>"
                    
                    html += "</div>"
                    
                    # Determine marker color based on price
                    color = get_marker_color(item['avg_price_per_sqyd'])
                    
                    # Create marker
                    folium.Marker(
                        location=[item['lat'], item['lon']],
                        popup=folium.Popup(html, max_width=300),
                        tooltip=f"{item['location']} - {item['property_count']} properties",
                        icon=folium.Icon(color=color, icon="home", prefix="fa")
                    ).add_to(marker_cluster)
                
                # Display the map
                folium_static(m, width=700, height=500)
            
            with legend_col:
                # Fix the legend rendering by directly inserting HTML
                st.write("#### Price Legend")
                st.markdown("""
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
                """, unsafe_allow_html=True)
                
                # Add some additional information about the map
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Map Information")
                st.write("• Click on markers for property details")
                st.write("• Clusters show multiple properties")
                date_info = f"filtered to {selected_date}" if selected_date != "All dates" else "all dates"
                st.write(f"• Showing data for {len(map_data)} locations ({date_info})")
        else:
            st.error("No location data available for the selected filter.")
            st.write("Try selecting a different date filter")
                
    except Exception as e:
        st.error(f"Error displaying map: {str(e)}")
        st.write("Please check the location data and try again.")

def display_location_table(location_df):
    """Display location data in tabular format"""
    st.subheader("Properties by Location")
    
    # Create a bar chart of properties by location
    st.bar_chart(location_df.set_index('Location')['Property Count'])
    
    # Display location details in an expandable table
    with st.expander("View Detailed Location Analysis"):
        st.dataframe(location_df, use_container_width=True)

def display_dashboard(dashboard):
    """Display the complete dashboard using data from the dashboard object"""
    # Dashboard header
    st.title("🏡 Property Investment Dashboard")
    st.markdown("### Analysis of property listings in Visakhapatnam")
    
    # Check if stats are populated
    if not dashboard.stats or dashboard.stats["total_properties"] == 0:
        st.warning("No property data has been loaded or processed.")
        return
    
    # Display the main dashboard sections
    display_summary_stats(dashboard)
    display_distribution_charts(dashboard)
    display_location_analysis(dashboard)
    
    # Add the analysis agent UI instead of automatically showing top properties
    display_analysis_ui(dashboard)
