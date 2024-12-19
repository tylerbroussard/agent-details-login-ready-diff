import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Agent Login Analysis Tool",
    layout="wide"
)

# Title and description
st.title("Agent Login Analysis Tool")
st.write("Upload your CSV file containing agent login and ready times.")

def analyze_agent_times(df):
    """
    Analyze agent login and ready times from a DataFrame.
    Returns a DataFrame with analysis results.
    """
    # Convert TIME column to datetime
    df['TIME'] = pd.to_datetime(df['TIME'], format='%H:%M:%S').dt.time
    
    # Initialize dictionaries to store first login and ready times
    first_logins = {}
    first_ready = {}
    
    # Process each row
    for _, row in df.iterrows():
        agent = row['AGENT']
        time = row['TIME']
        state = row['STATE']
        
        # Skip invalid times (00:00:00)
        if time == datetime.strptime('00:00:00', '%H:%M:%S').time():
            continue
            
        # Store first login time for each agent
        if state == 'Login':
            if agent not in first_logins or time < first_logins[agent]:
                first_logins[agent] = time
                
        # Store first ready time for each agent
        if state == 'Ready':
            if agent not in first_ready or time < first_ready[agent]:
                first_ready[agent] = time
    
    # Calculate time differences
    results = []
    for agent in first_logins:
        if agent in first_ready:
            login_time = first_logins[agent]
            ready_time = first_ready[agent]
            
            # Convert times to seconds since midnight for calculation
            login_seconds = login_time.hour * 3600 + login_time.minute * 60 + login_time.second
            ready_seconds = ready_time.hour * 3600 + ready_time.minute * 60 + ready_time.second
            
            # Calculate difference in seconds
            diff_seconds = ready_seconds - login_seconds
            
            # Handle cases where ready time is on the next day
            if diff_seconds < -12 * 3600:  # If negative and more than 12 hours, assume next day
                diff_seconds += 24 * 3600
                
            # Only include reasonable differences (positive and less than 12 hours)
            if diff_seconds > 0 and diff_seconds < 12 * 3600:
                results.append({
                    'Agent': agent,
                    'First Login': login_time.strftime('%H:%M:%S'),
                    'First Ready': ready_time.strftime('%H:%M:%S'),
                    'Time to Ready (seconds)': diff_seconds,
                    'Time to Ready': f'{diff_seconds // 60} minutes, {diff_seconds % 60} seconds'
                })
    
    # Convert results to DataFrame and sort by agent name alphabetically
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Agent')
    
    return results_df

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        # Read the uploaded file
        df = pd.read_csv(uploaded_file)
        
        # Run analysis
        results = analyze_agent_times(df)
        
        # Display results
        st.subheader("Analysis Results")
        st.dataframe(results[['Agent', 'First Login', 'First Ready', 'Time to Ready']])
        
        # Display summary statistics
        st.subheader("Summary Statistics")
        times = results['Time to Ready (seconds)']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average time", f"{times.mean():.1f} seconds")
        with col2:
            st.metric("Minimum time", f"{times.min():.1f} seconds")
        with col3:
            st.metric("Maximum time", f"{times.max():.1f} seconds")
        with col4:
            st.metric("Median time", f"{times.median():.1f} seconds")
            
        # Add download button for results
        csv = results.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Results",
            csv,
            "agent_analysis_results.csv",
            "text/csv",
            key='download-csv'
        )
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.write("Please ensure your CSV file contains the required columns (AGENT, TIME, STATE) "
                "and the data is in the correct format.")
else:
    st.info("Please upload a CSV file to begin analysis.")
    st.markdown("""
    ### Sample CSV Format:
    ```
    AGENT,TIME,STATE
    Agent1,09:00:00,Login
    Agent1,09:05:30,Ready
    Agent2,09:15:00,Login
    Agent2,09:20:45,Ready
    ```
    """)
