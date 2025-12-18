import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import scrapetube
import time

st.set_page_config(page_title="YouTube Transcript Ripper", layout="wide")

st.title("YouTube Timestamped Transcript Extractor")
st.markdown("Enter Video URLs or a Channel ID below.")

# Sidebar for mode selection
mode = st.sidebar.radio("Select Mode", ["List of Video URLs", "Whole Channel (Caution)"])
language_code = st.sidebar.text_input("Language Code", value="hi", help="hi for Hindi, en for English")

def get_transcript_data(video_id):
    """Fetches transcript with timestamps."""
    try:
        # Try fetching specific language, fallback to English, then auto-generated
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code, 'en'])
        
        formatter = []
        for line in transcript:
            # Format: [Start Time] Text
            timestamp = time.strftime('%H:%M:%S', time.gmtime(line['start']))
            text_line = f"[{timestamp}] {line['text']}"
            formatter.append(text_line)
            
        return " ".join(formatter)
    except Exception as e:
        return f"Error: {str(e)}"

# --- MODE 1: LIST OF URLS ---
if mode == "List of Video URLs":
    urls = st.text_area("Paste YouTube URLs (one per line):")
    
    if st.button("Extract Transcripts"):
        if not urls:
            st.error("Please paste some URLs first.")
        else:
            video_list = [url.strip() for url in urls.split('\n') if url.strip()]
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, url in enumerate(video_list):
                # Extract Video ID usually after v=
                if "v=" in url:
                    vid_id = url.split("v=")[1].split("&")[0]
                elif "youtu.be" in url:
                    vid_id = url.split("/")[-1]
                else:
                    vid_id = url # Assume user pasted ID
                
                status_text.text(f"Processing: {vid_id}...")
                transcript_text = get_transcript_data(vid_id)
                results.append({"Video ID": vid_id, "URL": url, "Transcript": transcript_text})
                
                # Update progress
                progress_bar.progress((i + 1) / len(video_list))
            
            st.success("Done!")
            df = pd.DataFrame(results)
            st.dataframe(df)
            
            # CSV Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="transcripts.csv", mime="text/csv")

# --- MODE 2: WHOLE CHANNEL ---
elif mode == "Whole Channel (Caution)":
    channel_id = st.text_input("Enter Channel ID (e.g., UCxxxxxxxx):")
    st.warning("⚠️ WARNING: Processing 2,000 videos at once will crash or timeout. Do this in batches of 50-100.")
    limit = st.number_input("How many videos to fetch?", min_value=1, max_value=2000, value=50)

    if st.button("Fetch Channel Videos"):
        st.info("Fetching video list... (This takes a moment)")
        videos = scrapetube.get_channel(channel_id, limit=limit)
        
        results = []
        video_list = list(videos)
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, video in enumerate(video_list):
            vid_id = video['videoId']
            title = video['title']['runs'][0]['text']
            
            status_text.text(f"Processing {i+1}/{len(video_list)}: {title}")
            transcript_text = get_transcript_data(vid_id)
            
            results.append({
                "Video ID": vid_id, 
                "Title": title, 
                "Transcript": transcript_text
            })
            progress_bar.progress((i + 1) / len(video_list))
            
        st.success("Batch Complete!")
        df = pd.DataFrame(results)
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Batch CSV", data=csv, file_name="channel_transcripts.csv", mime="text/csv")
