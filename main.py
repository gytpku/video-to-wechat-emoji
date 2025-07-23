
import os
import shutil
import time
import uuid
import socket
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess

import google.generativeai as genai
import json
import re

from dotenv import load_dotenv

# --- Configuration ---
load_dotenv() # Load variables from .env file

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # Default to flash

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    raise ValueError("GOOGLE_API_KEY not found or not set in .env file. Please set it.")

genai.configure(api_key=API_KEY)

UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

app = FastAPI()

# --- Static Files ---
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/results", StaticFiles(directory=RESULT_DIR), name="results")


# --- Helper Functions ---
def run_ffmpeg_command(command):
    """Runs an FFmpeg command and raises an exception if it fails."""
    try:
        print(f"Running FFmpeg command: {command}")
        subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"FFmpeg processing failed: {e.stderr}")

def get_video_dimensions(video_path):
    """Gets the video dimensions (width, height) using ffprobe."""
    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0",
            video_path
        ]
        print(f"Running ffprobe command: {command}")
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
        width, height = map(int, result.stdout.strip().split('x'))
        return width, height
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"ffprobe Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get video dimensions.")

def generate_ai_instructions(video_path, prompt, width, height):
    """Calls the Gemini AI model to get processing instructions."""
    print(f"Uploading video to Gemini: {video_path}")
    video_file = genai.upload_file(path=video_path, mime_type="video/mp4")
    print(f"Video uploaded successfully. File URI: {video_file.uri}")

    # Wait for the video to be processed
    while video_file.state.name == "PROCESSING":
        print("Waiting for video processing...")
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise HTTPException(status_code=500, detail="Google AI API: Video processing failed.")

    system_prompt = f"""
    You are an expert video editor specializing in creating viral WeChat emojis.
    Your task is to analyze a silent video and a user's prompt to suggest 2-5 engaging emoji options.
    The final emoji must be a square video, between 400x400 and 500x500 pixels, and under 5 seconds.

    The original video dimensions are {width}x{height} pixels.

    IMPORTANT GUIDELINES FOR CROPPING AND SCALING:
    1. PRIORITIZE SCALING over cropping to preserve content
    2. Use minimal cropping - crop only small edges or unnecessary borders
    3. Focus on the main subject/action in the video when deciding crop area
    4. The crop should retain at least 70% of the original content area
    5. If the original video is already close to square, use minimal cropping

    For scaling strategy:
    - If original is wider than tall ({width}x{height}): scale down to fit height, then crop minimal width
    - If original is taller than wide: scale down to fit width, then crop minimal height
    - Calculate scale_factor to make the smaller dimension close to your target size (400-500px)

    Analyze the video for key moments, funny faces, or interesting actions that align with the user's prompt: '{prompt}'.

    For each suggested emoji, you must provide the following parameters in a strict JSON format:

    1.  `start_time`: The ideal start time of the clip (format: HH:MM:SS.mmm, example: 00:00:15.500).
    2.  `end_time`: The ideal end time of the clip (format: HH:MM:SS.mmm, example: 00:00:18.500). The duration must not exceed 5 seconds.
    3.  `scale_factor`: A float value for scaling the video BEFORE cropping. Calculate this to make the video approximately 400-500px on the smaller dimension.
    4.  `crop_box`: A JSON object with `x`, `y`, `width`, and `height`.
        - The `width` and `height` must be equal and between 400 and 500.
        - CRITICAL: After scaling, crop minimally from the center or focus area
        - Ensure crop coordinates fit within scaled dimensions: scaled_width = {width} * scale_factor, scaled_height = {height} * scale_factor
        - x + width ≤ scaled_width, y + height ≤ scaled_height
    5.  `text_overlay`: A short, impactful Chinese text (2-4 characters) to overlay on the video.

    EXAMPLE CALCULATION for {width}x{height}:
    - Target: 450x450 square
    - Smaller dimension is {min(width, height)}
    - Suggested scale_factor: {450/min(width, height):.2f}
    - After scaling: {int(width * 450/min(width, height))}x{int(height * 450/min(width, height))}
    - Crop from center, removing minimal edges

    IMPORTANT: Time format must be exactly HH:MM:SS.mmm (hours:minutes:seconds.milliseconds)
    Example: 00:00:15.500 for 15.5 seconds, 00:01:23.250 for 1 minute 23.25 seconds

    Respond ONLY with a JSON object that has a single key, "options", whose value is a list of the suggested emoji options.
    """

    model = genai.GenerativeModel(model_name=MODEL_NAME)
    print("Sending request to Gemini API...")
    response = model.generate_content([system_prompt, video_file])
    
    # Clean up the file from Google's storage
    genai.delete_file(video_file.name)
    print(f"Cleaned up file {video_file.name} from Google AI.")

    try:
        # Use regex to find the JSON block.
        # This is more robust against surrounding text or markdown.
        json_match = re.search(r"```json\n(.*?)```", response.text, re.DOTALL)
        if not json_match:
            # Try without markdown formatting
            json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in the AI response.")
        
        cleaned_json_text = json_match.group(1) if "```json" in response.text else json_match.group(0)
        ai_response = json.loads(cleaned_json_text)
        
        # Validate and fix time format if needed
        for option in ai_response.get("options", []):
            start_time = option.get("start_time", "")
            end_time = option.get("end_time", "")
            
            # Fix time format if it's wrong (e.g., 00:18:000 -> 00:00:18.000)
            option["start_time"] = fix_time_format(start_time)
            option["end_time"] = fix_time_format(end_time)
            
            # Validate crop box to prevent excessive cropping
            crop = option.get("crop_box", {})
            scale = option.get("scale_factor", 1.0)
            
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)
            
            # Ensure crop box is valid
            if crop.get("x", 0) + crop.get("width", 0) > scaled_width:
                print(f"Warning: Crop box exceeds scaled width, adjusting...")
                crop["x"] = max(0, scaled_width - crop.get("width", 400))
            
            if crop.get("y", 0) + crop.get("height", 0) > scaled_height:
                print(f"Warning: Crop box exceeds scaled height, adjusting...")
                crop["y"] = max(0, scaled_height - crop.get("height", 400))
        
        return ai_response
    except (json.JSONDecodeError, AttributeError, ValueError) as e:
        print(f"Error decoding AI response: {e}")
        print(f"Raw AI response: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response.")

def fix_time_format(time_str):
    """Fix common time format issues"""
    if not time_str:
        return "00:00:00.000"
    
    # Remove any extra spaces
    time_str = time_str.strip()
    
    # Pattern: HH:MM:SSS (wrong format) -> HH:MM:SS.SSS
    # Example: 00:18:000 -> 00:00:18.000
    if re.match(r'^\d{2}:\d{2}:\d{3}$', time_str):
        parts = time_str.split(':')
        hours = parts[0]
        minutes = parts[1]
        seconds_and_ms = parts[2]
        # Convert seconds from SSS format to SS.S format
        if len(seconds_and_ms) == 3:
            seconds = seconds_and_ms[:2]
            milliseconds = seconds_and_ms[2:]
            return f"{hours}:{minutes}:{seconds}.{milliseconds}00"
    
    # Pattern: MM:SS -> 00:MM:SS.000
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        parts = time_str.split(':')
        minutes = parts[0].zfill(2)
        seconds = parts[1]
        return f"00:{minutes}:{seconds}.000"
    
    # Pattern: SS.mmm -> 00:00:SS.mmm
    if re.match(r'^\d{1,2}\.\d{3}$', time_str):
        return f"00:00:{time_str.zfill(6)}"
    
    # Pattern: SS -> 00:00:SS.000
    if re.match(r'^\d{1,2}$', time_str):
        return f"00:00:{time_str.zfill(2)}.000"
    
    # If already in correct format HH:MM:SS.mmm, return as is
    if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}$', time_str):
        return time_str
    
    # Default fallback
    print(f"Warning: Unrecognized time format '{time_str}', using default")
    return "00:00:00.000"

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serves the main HTML page."""
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/create-emoji/")
async def create_emoji(video: UploadFile = File(...), prompt: str = Form(...)):
    """
    The main endpoint to create emojis.
    """
    # Helper to clean strings for filenames
    def clean_filename(text):
        # Allow Unicode letters, numbers, underscores, hyphens, and periods
        cleaned_text = re.sub(r'[^\w.-]', '_', text, flags=re.UNICODE)
        return cleaned_text[:50].strip() # Limit to 50 chars to avoid very long filenames

    # 1. Save the uploaded video
    video_id = str(uuid.uuid4())
    original_video_path = os.path.join(UPLOAD_DIR, f"{video_id}_{video.filename}")

    with open(original_video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    no_audio_video_path = None # Initialize to None for finally block

    try:
        # 2. Pre-process: Create a video without audio
        no_audio_video_path = os.path.join(UPLOAD_DIR, f"{video_id}_no_audio.mp4")
        ffmpeg_command_no_audio = [
            "ffmpeg",
            "-i", original_video_path,
            "-an",  # No audio
            "-y",   # Overwrite output file if it exists
            no_audio_video_path
        ]
        run_ffmpeg_command(ffmpeg_command_no_audio)
        print(f"Created video without audio at: {no_audio_video_path}")

        # 3. Get Video Dimensions
        width, height = get_video_dimensions(no_audio_video_path)
        print(f"Video dimensions: {width}x{height}")

        # 4. Call AI to get processing instructions
        ai_instructions = generate_ai_instructions(no_audio_video_path, prompt, width, height)
        
        results = []
        for i, option in enumerate(ai_instructions["options"]):
            # 5. Process video based on one option
            text = option["text_overlay"]
            print(f"Original text_overlay from AI: {text}")
            cleaned_text = clean_filename(text)
            
            processed_video_path = os.path.join(RESULT_DIR, f"{video_id}_option_{i}_{cleaned_text}.mp4")
            
            start = option["start_time"]
            end = option["end_time"]
            scale = option["scale_factor"]
            crop = option["crop_box"]
            
            # Build the complex filter string for scaling, cropping, and adding text
            video_filter = f"scale=iw*{scale}:ih*{scale},crop={crop['width']}:{crop['height']}:{crop['x']}:{crop['y']},drawtext=text='{text}':x=(w-text_w)/2:y=h-th-10:fontsize=24:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2"

            ffmpeg_process_command = [
                "ffmpeg",
                "-i", no_audio_video_path,
                "-ss", start,
                "-to", end,
                "-vf", video_filter,
                "-y",
                processed_video_path
            ]
            run_ffmpeg_command(ffmpeg_process_command)

            # 6. Compress video to be under 1MB
            compressed_video_path = os.path.join(RESULT_DIR, f"{cleaned_text}.mp4")
            ffmpeg_compress_command = [
                "ffmpeg",
                "-i", processed_video_path,
                "-b:v", "1M",
                "-c:v", "libx264",
                "-preset", "medium",
                "-y",
                compressed_video_path
            ]
            run_ffmpeg_command(ffmpeg_compress_command)

            # 7. Create a thumbnail image
            thumbnail_path = os.path.join(RESULT_DIR, f"{cleaned_text}.jpg")
            ffmpeg_thumbnail_command = [
                "ffmpeg",
                "-i", compressed_video_path,
                "-ss", "00:00:00.500", # Capture frame at 0.5s
                "-vframes", "1",
                "-y",
                thumbnail_path
            ]
            run_ffmpeg_command(ffmpeg_thumbnail_command)

            results.append({
                "video_url": f"/results/{os.path.basename(compressed_video_path)}",
                "image_url": f"/results/{os.path.basename(thumbnail_path)}"
            })

    finally:
        # 8. Clean up intermediate files
        if os.path.exists(original_video_path):
            os.remove(original_video_path)
        if no_audio_video_path and os.path.exists(no_audio_video_path):
            os.remove(no_audio_video_path)
        # Clean up uncompressed processed videos
        for i, option in enumerate(ai_instructions["options"]):
            cleaned_text = clean_filename(option["text_overlay"])
            uncompressed_path = os.path.join(RESULT_DIR, f"{video_id}_option_{i}_{cleaned_text}.mp4")
            if os.path.exists(uncompressed_path):
                os.remove(uncompressed_path)
    
    return {"options": results}

    return {"options": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

