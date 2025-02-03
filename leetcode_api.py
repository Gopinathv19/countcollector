import streamlit as st
import pandas as pd
import requests
import time
import datetime
def fetch_leetcode_stats(username):
    """Fetch LeetCode statistics using GraphQL API"""
    if not username or pd.isna(username):  # Check for empty or NaN usernames
        return None
        
    url = 'https://leetcode.com/graphql'
    
    query = {
        "query": """
        {
          matchedUser(username: "%s") {
            username
            submitStats: submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
                submissions
              }
            }
          }
        }
        """ % username
    }
    
    try:
        response = requests.post(url, json=query, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('matchedUser'):
                stats = data['data']['matchedUser']['submitStats']['acSubmissionNum']
                easy_solved = next((item['count'] for item in stats if item['difficulty'] == 'Easy'), 0)
                medium_solved = next((item['count'] for item in stats if item['difficulty'] == 'Medium'), 0)
                hard_solved = next((item['count'] for item in stats if item['difficulty'] == 'Hard'), 0)
                calculated_total = easy_solved + medium_solved + hard_solved
                return {
                    'easySolved': easy_solved,
                    'mediumSolved': medium_solved,
                    'hardSolved': hard_solved,
                    'totalSolved': calculated_total
                }
            return None  # Explicitly return None if user not found
        return None
    except Exception as e:
        st.error(f"Error fetching data for {username}: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="LeetCode Stats Collector", layout="wide")
    st.title("🎯 LeetCode Statistics Collector")
    
    uploaded_file = st.file_uploader("Upload student data CSV", type=['csv'])
    
    if uploaded_file:
        try:
            students_df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            
            if st.button("Fetch Statistics"):
                stats_data = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_students = len(students_df)
                
                for index, student in students_df.iterrows():
                    username = student['LEETCODE USERNAME']
                    status_text.text(f"Fetching data for {student['NAME']} ({index + 1}/{total_students})")
                    
                    stats = fetch_leetcode_stats(username)
                    if stats:
                        stats_data.append({
                            'ROLL NUM': student['ROLL NUM'],
                            'NAME': student['NAME'],
                            'LEETCODE USERNAME': username,
                            'EASY SOLVED': stats['easySolved'],
                            'MEDIUM SOLVED': stats['mediumSolved'],
                            'HARD SOLVED': stats['hardSolved'],
                            'TOTAL SOLVED': stats['totalSolved']
                        })
                    else:
                        # Add row with zeros for invalid/not found username
                        stats_data.append({
                            'ROLL NUM': student['ROLL NUM'],
                            'NAME': student['NAME'],
                            'LEETCODE USERNAME': username,
                            'EASY SOLVED': 0,
                            'MEDIUM SOLVED': 0,
                            'HARD SOLVED': 0,
                            'TOTAL SOLVED': 0
                        })
                        st.warning(f"Failed to fetch stats for {student['NAME']} (Username: {username})")
                    
                    progress_bar.progress((index + 1) / total_students)
                    time.sleep(0.5)
                
                if stats_data:
                    result_df = pd.DataFrame(stats_data)
                    
                    st.subheader("Preview of Collected Data")
                    st.dataframe(result_df, use_container_width=True)
                    
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Statistics CSV",
                        data=csv,
                        file_name=f"leetcode_stats_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                    
                    st.success("✅ Statistics collection completed!")
                else:
                    st.error("No data was collected!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Instructions
    with st.expander("📋 Instructions"):
        st.markdown("""
        1. Upload a CSV file containing student data with columns:
           - ROLL NUM
           - NAME
           - LEETCODE USERNAME
        2. Click 'Fetch Statistics' to collect data
        3. Wait for the process to complete
        4. Download the resulting CSV file
        """)

if __name__ == "__main__":
    main()