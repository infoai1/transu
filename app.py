import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd

# 1. Page Setup
st.set_page_config(page_title="YouTube Transcript Tool", layout="wide")
st.title("YouTube Transcript Extractor")

# 2. Input Box
url = st.text_input("Paste YouTube URL below:", placeholder="https://www.youtube.com/watch?v=...")

# 3. Helper Function to get Video ID
def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

# 4. Main Logic
if st.button("Get Transcript"):
    if url:
        video_id = get_video_id(url)
        if video_id:
            st.info("Extracting...")
            try:
                # Get the transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                
                # Process data
                data = []
                for item in transcript:
                    minutes = int(item['start'] // 60)
                    seconds = int(item['start'] % 60)
                    timestamp = f"{minutes:02d}:{seconds:02d}"
                    data.append({"Timestamp": timestamp, "Text": item['text']})
                
                # Show Table
                df = pd.DataFrame(data)
                st.success("Success!")
                st.dataframe(df, use_container_width=True)
                
                # Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, "transcript.csv", "text/csv")
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.write("Tip: Timestamps might be disabled on this video.")
        else:
            st.error("Invalid URL format.")
    else:
        st.warning("Please paste a URL first.")
