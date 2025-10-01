import streamlit as st 
import yt_dlp
import os


st.set_page_config(page_title="Playlist Downloader", page_icon="🎶", layout="wide")

path = "Downloads"

# Create Downloads folder if it doesn't exist
if not os.path.exists(path):
    os.makedirs(path)

def get_playlist_info(url):
    """Get playlist information"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Get only the playlist info, don't download videos
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            return None

def safe_filename(filename):
    """Create a safe file name"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()

st.title("🎶 YouTube Playlist Downloader")
st.write("Download multiple YouTube video URLs in bulk (powered by yt-dlp)")

# Settings
col1, col2 = st.columns(2)

with col1:
    format_choice = st.selectbox(
        "📄 Format:",
        ["MP4 (Video)", "MP3 (Audio)"]
    )

with col2:
    if format_choice == "MP4 (Video)":
        quality_choice = st.selectbox(
            "🎯 Quality:",
            ["Highest Quality", "720p", "480p", "360p"]
        )
    else:
        quality_choice = "Audio"

st.info(f"📁 Files will be saved to: `{os.path.abspath(path)}`")

# Video URLs input
video_urls = st.text_area(
    "🔗 Video URLs (one URL per line):",
    placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...",
    help="Enter one video URL per line"
)

if video_urls:
    urls = [url.strip() for url in video_urls.splitlines() if url.strip()]
    if urls:
        st.info(f"🔍 Found {len(urls)} video URLs.")
        
        if st.button("🚀 Download Videos", type="primary", use_container_width=True):
            # Download statistics
            success_count = 0
            error_count = 0
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Container for results
            results_container = st.container()
            
            total_videos = len(urls)
            
            # Download settings
            if format_choice == "MP4 (Video)":
                if quality_choice == "Highest Quality":
                    format_selector = 'best[ext=mp4]'
                elif quality_choice == "720p":
                    format_selector = 'best[height<=720][ext=mp4]/best[ext=mp4]'
                elif quality_choice == "480p":
                    format_selector = 'best[height<=480][ext=mp4]/best[ext=mp4]'
                else:  # 360p
                    format_selector = 'best[height<=360][ext=mp4]/worst[ext=mp4]'
            else:  # MP3
                format_selector = 'bestaudio/best'
            
            for i, video_url in enumerate(urls):
                current_video = i + 1
                progress = current_video / total_videos
                
                try:
                    status_text.text(f"🔄 Processing video {current_video}/{total_videos}: {video_url[:50]}...")
                    progress_bar.progress(progress)
                    
                    # Safe file name
                    output_template = os.path.join(path, f"%(title)s.%(ext)s")
                    
                    ydl_opts = {
                        'format': format_selector,
                        'outtmpl': output_template,
                        'quiet': True,
                        'no_warnings': True,
                    }
                    
                    # Audio conversion for MP3
                    if format_choice == "MP3 (Audio)":
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                    
                    # Download
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    
                    success_count += 1
                    
                    with results_container:
                        st.success(f"✅ {current_video}. **{video_url}** - Downloaded")
                        
                except Exception as e:
                    error_count += 1
                    with results_container:
                        st.error(f"❌ {current_video}. **{video_url}** - Error: {str(e)}")
            
            # Final status
            progress_bar.progress(1.0)
            status_text.text("✅ All tasks completed!")
            
            # Summary
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Successful", success_count)
            with col2:
                st.metric("❌ Errored", error_count)
            with col3:
                st.metric("📊 Total", total_videos)
            
            if success_count > 0:
                st.balloons()
                st.success(f"🎉 Download completed! {success_count} videos were successfully downloaded.")
    else:
        st.warning("⚠️ No valid video URL was entered.")

# Usage information
with st.expander("ℹ️ Usage Information"):
    st.markdown("""
    ### Playlist Download Guide:
    
    1. **Copy the Playlist URL:**
       - Go to the playlist you want on YouTube
       - Copy the URL from the browser's address bar
       - The URL should look like: `https://www.youtube.com/playlist?list=...`
    
    2. **Select format and quality:**
       - Choose MP4 for video, MP3 for audio
       - Set the video quality according to your preference
    
    3. **Set the download range:**
       - You can choose the entire playlist or a specific range
       - It's recommended to use a range for large playlists
    
    4. **Start the download process:**
       - Click the "Download Playlist" button
       - Wait for the process to complete
    
    ### ⚠️ Important Notes:
    - FFmpeg installation is required for MP3 conversion
    - Large playlists may take a long time
    - Age-restricted videos will be skipped
    - The process will stop if the internet connection is interrupted
    - Files are saved in the Downloads folder
    
    ### 🚀 yt-dlp Advantages:
    - Faster and more reliable
    - Supports more sites
    - Regular updates
    - Advanced error handling
    """)

# FFmpeg installation guide
with st.expander("🔧 FFmpeg Installation Guide"):
    st.markdown("""
    ### FFmpeg Installation (Required for MP3):
    
    **Windows:**
    ```bash
    # With Chocolatey
    choco install ffmpeg
    
    # With Winget  
    winget install ffmpeg
    ```
    
    **Linux:**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```
    
    **macOS:**
    ```bash
    brew install ffmpeg
    ```
    
    ### Check Installation:
    ```bash
    ffmpeg -version
    ```
    """)