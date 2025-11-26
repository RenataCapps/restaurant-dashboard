import streamlit as st
import mysql.connector
import pandas as pd
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(page_title="London Restaurant Dashboard", layout="wide")

# Database connection configuration
# TODO: Update these with YOUR actual database credentials from your course materials
DB_CONFIG = {
    'host': 'db-mysql-itom-do-user-28250611-0.i.db.ondigitalocean.com',
    'port': 25060,
    'user': 'restaurant_readonly',
    'password': 'SecurePassword123!',
    'database': 'restaurant'
}

# Function to create database connection
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Test connection
def test_connection():
    conn = get_connection()
    if conn:
        st.success("Database connected successfully!")
        conn.close()
        return True
    return False

# Create tabs
tab1, tab2, tab3 = st.tabs(["HW Summary", "Database Search", "Interactive Map"])

# TAB 1: HW Summary
with tab1:
    st.title("Restaurant Dashboard - Homework Summary")
    
    st.header("Student Information")
    st.write("**Name:** Renata Capps")
    st.write("**Course:** ITOM6265")
    st.write("**Assignment:** Restaurant Dashboard with Streamlit")
    
    st.header("Dashboard Overview")
    st.write("""
    This interactive dashboard provides tools to explore London restaurant data:
    - **Tab 2:** Search restaurants by name and vote count with dynamic filters
    - **Tab 3:** Interactive map showing restaurant locations across London
    """)
    
    st.header("Customizations Implemented")
    st.markdown("""
    1. **Layout:** Used wide layout with multi-column design and custom containers
    2. **Map Tiles:** Implemented CartoDB Positron custom tiles for clean visualization
    3. **Data Display:** Enhanced tables with color-coded vote counts and formatted results
    """)
    
    # Test database connection
    st.header("Database Connection Status")
    test_connection()

# TAB 2: Database Search
with tab2:
    st.title("Restaurant Database Search")
    st.write("Search restaurants by name and filter by vote count")
    
    # Create input widgets
    col1, col2 = st.columns([2, 1])
    
    with col1:
        name_pattern = st.text_input(
            "Restaurant Name Pattern",
            placeholder="Enter restaurant name (e.g., 'Dishoom')",
            help="Leave empty to show all restaurants"
        )
    
    with col2:
        # Get min/max votes from database first
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(votes), MAX(votes) FROM business_location WHERE votes IS NOT NULL")
            min_votes, max_votes = cursor.fetchone()
            conn.close()
            
            vote_range = st.slider(
                "Vote Range",
                min_value=int(min_votes) if min_votes else 0,
                max_value=int(max_votes) if max_votes else 1000,
                value=(int(min_votes) if min_votes else 0, int(max_votes) if max_votes else 1000),
                help="Filter restaurants by vote count"
            )
    
    # Search button
    if st.button("Get results", type="primary"):
        conn = get_connection()
        if conn:
            try:
                # Build SQL query
                query = """
                    SELECT name, votes, city
                    FROM business_location
                    WHERE votes BETWEEN %s AND %s
                """
                params = [vote_range[0], vote_range[1]]
                
                # Add name filter if provided
                if name_pattern:
                    query += " AND name LIKE %s"
                    params.append(f"%{name_pattern}%")
                
                query += " ORDER BY votes DESC"
                
                # Execute query
                df = pd.read_sql(query, conn, params=params)
                conn.close()
                
                # Display results
                if len(df) > 0:
                    st.success(f"Found {len(df)} restaurant(s)")
                    
                    # Format the display
                    df_display = df.copy()
                    df_display.columns = ['Restaurant Name', 'Votes', 'City']
                    
                    # Color-code based on votes
                    def color_votes(val):
                        if val > 500:
                            return 'background-color: #d4edda'
                        elif val > 200:
                            return 'background-color: #fff3cd'
                        else:
                            return 'background-color: #f8d7da'
                    
                    styled_df = df_display.style.applymap(
                        color_votes, 
                        subset=['Votes']
                    )
                    
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.warning("No results found. Try adjusting your filters.")
                    
            except Exception as e:
                st.error(f"Query error: {e}")

# TAB 3: Interactive Map
with tab3:
    st.title("Restaurant Locations Map")
    
    if st.button("Display map!", type="primary"):
        st.caption("Map of restaurants in London. Click on teardrop to check names.")
        
        conn = get_connection()
        if conn:
            try:
                # Query location data - filter out NULL coordinates
                query = """
                    SELECT name, latitude, longitude
                    FROM business_location
                    WHERE latitude IS NOT NULL 
                    AND longitude IS NOT NULL
                """
                
                df = pd.read_sql(query, conn)
                conn.close()
                
                if len(df) > 0:
                    # Create map centered on London
                    m = folium.Map(
                        location=[51.5074, -0.1278],
                        zoom_start=12,
                        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                        attr='CartoDB Positron'
                    )
                    
                    # Add markers for each restaurant
                    for idx, row in df.iterrows():
                        folium.Marker(
                            location=[row['latitude'], row['longitude']],
                            popup=folium.Popup(row['name'], max_width=200),
                            tooltip=row['name'],
                            icon=folium.Icon(color='blue', icon='info-sign')
                        ).add_to(m)
                    
                    # Display map
                    st_folium(m, width=1200, height=600)
                    
                    st.info(f"Displaying {len(df)} restaurants on the map")
                else:
                    st.warning("No restaurants with valid coordinates found.")
                    
            except Exception as e:
                st.error(f"Map error: {e}")
