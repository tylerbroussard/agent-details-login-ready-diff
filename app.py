import pandas as pd
from datetime import datetime

def analyze_agent_times(csv_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
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

# Example usage:
if __name__ == "__main__":
    csv_path = 'agent-details.csv'
    results = analyze_agent_times(csv_path)
    
    # Print results
    pd.set_option('display.max_rows', None)
    print("\nAgent Login to Ready Time Analysis:")
    print("====================================")
    print(results[['Agent', 'First Login', 'First Ready', 'Time to Ready']])
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("==================")
    times = results['Time to Ready (seconds)']
    print(f"Average time to ready: {times.mean():.1f} seconds")
    print(f"Minimum time to ready: {times.min():.1f} seconds")
    print(f"Maximum time to ready: {times.max():.1f} seconds")
    print(f"Median time to ready: {times.median():.1f} seconds")