import os
import re
import yt_dlp
import json
from pathlib import Path

def get_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:be\/)([0-9A-Za-z_-]{11}).*'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_video(video_url, output_dir, cookies_path=None):
    video_id = get_video_id(video_url)
    if not video_id:
        return None, "Invalid URL"

    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, f"{video_id}.%(ext)s")
    
    # Check if exists
    for f in os.listdir(output_dir):
        if f.startswith(video_id):
            return os.path.join(output_dir, f), "Cached"

    ydl_opts = {
        'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'concurrent_fragment_downloads': 5,
        'retries': 5,
        'nocheckcertificate': True,
    }
    
    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = str(cookies_path)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        # Find the downloaded file
        for f in os.listdir(output_dir):
            if f.startswith(video_id):
                return os.path.join(output_dir, f), "Downloaded"
        return None, "Download Failed"
    except Exception as e:
        return None, str(e)

def fetch_metrics(video_urls, output_file=None):
    metrics = {}
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in video_urls:
            vid = get_video_id(url)
            if not vid: continue
            try:
                info = ydl.extract_info(url, download=False)
                if info:
                    metrics[vid] = {
                        "title": info.get('title', 'Unknown'),
                        "url": url,
                        "view_count": info.get('view_count', 0),
                        "like_count": info.get('like_count', 0),
                        "comment_count": info.get('comment_count', 0)
                    }
            except Exception as e:
                print(f"Failed metrics for {vid}: {e}")
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=4)
            
    return metrics
