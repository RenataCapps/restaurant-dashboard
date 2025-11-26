# Test connection function
def test_connection():
    conn = get_connection()
    if conn:
        st.success("✅ Database connected successfully!")
        conn.close()
        return True
    return False

# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 HW Summary", "🔍 Database Search", "🗺️ Interactive Map"])

# TAB 1: HW Summary
with tab1:
    st.title("🍽️ Restaurant Dashboard - Homework Summary")
    
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
