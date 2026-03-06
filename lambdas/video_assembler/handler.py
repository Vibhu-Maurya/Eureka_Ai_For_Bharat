"""Video assembler Lambda function using FFmpeg."""
import json
import os
import subprocess
import tempfile
import uuid
from typing import Dict, Any, List
import boto3
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
CONTENT_BUCKET = os.environ.get('CONTENT_BUCKET', 'orchestrai-content')
SCENE_PLANS_TABLE = os.environ.get('SCENE_PLANS_TABLE', 'OrchestRAI-ScenePlans')

# FFmpeg binary path (will be in Lambda layer)
FFMPEG_PATH = os.environ.get('FFMPEG_PATH', '/opt/bin/ffmpeg')
FFPROBE_PATH = os.environ.get('FFPROBE_PATH', '/opt/bin/ffprobe')


def create_subtitle_file(script: Dict[str, Any], output_path: str) -> str:
    """Create SRT subtitle file from script."""
    srt_content = []
    subtitle_index = 1
    current_time = 0.0
    
    # Add hook
    if 'hook' in script:
        hook = script['hook']
        start_time = format_srt_time(current_time)
        end_time = format_srt_time(current_time + hook.get('duration', 3))
        srt_content.append(f"{subtitle_index}\n{start_time} --> {end_time}\n{hook['text']}\n")
        subtitle_index += 1
        current_time += hook.get('duration', 3)
    
    # Add scenes
    if 'scenes' in script:
        for scene in script['scenes']:
            start_time = format_srt_time(current_time)
            end_time = format_srt_time(current_time + scene.get('duration', 10))
            srt_content.append(f"{subtitle_index}\n{start_time} --> {end_time}\n{scene['text']}\n")
            subtitle_index += 1
            current_time += scene.get('duration', 10)
    
    # Add CTA
    if 'cta' in script:
        cta = script['cta']
        start_time = format_srt_time(current_time)
        end_time = format_srt_time(current_time + cta.get('duration', 3))
        srt_content.append(f"{subtitle_index}\n{start_time} --> {end_time}\n{cta['text']}\n")
    
    # Write to file
    srt_path = os.path.join(output_path, 'subtitles.srt')
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))
    
    return srt_path


def format_srt_time(seconds: float) -> str:
    """Format seconds to SRT time format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_text_overlay_video(text: str, duration: float, output_path: str, width: int = 1080, height: int = 1920) -> str:
    """Create a video with text overlay on colored background."""
    video_path = os.path.join(output_path, f'text_overlay_{uuid.uuid4().hex[:8]}.mp4')
    
    # Create a video with colored background and text
    # Using a simpler approach: create solid color with nullsrc + color filter
    # Escape text for FFmpeg - replace single quotes and special characters
    text_escaped = text.replace("'", "'\\''").replace(":", "\\:").replace("%", "\\%")
    
    # Use nullsrc with color overlay instead of lavfi color source
    cmd = [
        FFMPEG_PATH,
        '-f', 'lavfi',
        '-i', f'nullsrc=s={width}x{height}:d={duration}:r=30',
        '-vf', f"geq=r='26':g='26':b='46',drawtext=text='{text_escaped}':fontcolor=white:fontsize=60:box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-pix_fmt', 'yuv420p',
        '-r', '30',
        '-t', str(duration),
        '-y',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"FFmpeg error creating text overlay: {result.stderr}")
            raise Exception(f"Failed to create text overlay video: {result.stderr}")
        
        # Verify the file was created and has content
        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            raise Exception(f"Text overlay video was not created or is empty")
        
        print(f"Created text overlay video: {video_path} ({os.path.getsize(video_path)} bytes)")
        return video_path
    except subprocess.TimeoutExpired:
        raise Exception("FFmpeg timeout creating text overlay")


def combine_audio_video(video_path: str, audio_path: str, output_path: str) -> str:
    """Combine video and audio tracks."""
    output_file = os.path.join(output_path, f'combined_{uuid.uuid4().hex[:8]}.mp4')
    
    cmd = [
        FFMPEG_PATH,
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-y',
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"FFmpeg error combining audio/video: {result.stderr}")
            raise Exception(f"Failed to combine audio and video: {result.stderr}")
        
        # Verify output file
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise Exception("Combined video was not created or is empty")
        
        print(f"Combined video with audio: {output_file} ({os.path.getsize(output_file)} bytes)")
        return output_file
    except subprocess.TimeoutExpired:
        raise Exception("FFmpeg timeout combining audio/video")


def burn_subtitles(video_path: str, subtitle_path: str, output_path: str) -> str:
    """Burn subtitles into video."""
    output_file = os.path.join(output_path, f'subtitled_{uuid.uuid4().hex[:8]}.mp4')
    
    # Escape the subtitle path for FFmpeg
    subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')
    
    cmd = [
        FFMPEG_PATH,
        '-i', video_path,
        '-vf', f"subtitles='{subtitle_path_escaped}':force_style='FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Bold=1,MarginV=50'",
        '-c:a', 'copy',
        '-y',
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            print(f"FFmpeg error burning subtitles: {result.stderr}")
            # If subtitle burning fails, return original video
            print("Subtitle burning failed, returning video without subtitles")
            return video_path
        return output_file
    except subprocess.TimeoutExpired:
        print("FFmpeg timeout burning subtitles, returning video without subtitles")
        return video_path


def concatenate_videos(video_paths: List[str], output_path: str) -> str:
    """Concatenate multiple video files."""
    if len(video_paths) == 1:
        return video_paths[0]
    
    # Create concat file
    concat_file = os.path.join(output_path, 'concat_list.txt')
    with open(concat_file, 'w') as f:
        for video_path in video_paths:
            f.write(f"file '{video_path}'\n")
    
    output_file = os.path.join(output_path, f'concatenated_{uuid.uuid4().hex[:8]}.mp4')
    
    # Use re-encoding instead of copy to ensure compatibility
    cmd = [
        FFMPEG_PATH,
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-pix_fmt', 'yuv420p',
        '-r', '30',
        '-y',
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"FFmpeg error concatenating videos: {result.stderr}")
            raise Exception(f"Failed to concatenate videos: {result.stderr}")
        
        # Verify output file
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise Exception("Concatenated video was not created or is empty")
        
        print(f"Concatenated {len(video_paths)} videos into {output_file} ({os.path.getsize(output_file)} bytes)")
        return output_file
    except subprocess.TimeoutExpired:
        raise Exception("FFmpeg timeout concatenating videos")


def get_video_duration(video_path: str) -> float:
    """Get duration of video file using ffprobe."""
    cmd = [
        FFPROBE_PATH,
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0.0
    except Exception as e:
        print(f"Error getting video duration: {str(e)}")
        return 0.0


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Assemble final video from scenes, audio, and subtitles."""
    try:
        content_id = event['contentId']
        script = event.get('script', {})
        audio_files = event.get('audioFiles', {})
        scenes = event.get('scenes', [])
        language = event.get('language', 'en')
        
        print(f"Starting video assembly for content {content_id}, language {language}")
        
        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Working directory: {temp_dir}")
            
            # Get audio file for the language
            if language not in audio_files:
                # Use first available language
                language = list(audio_files.keys())[0] if audio_files else 'en'
            
            audio_info = audio_files.get(language, {})
            audio_s3_key = audio_info.get('s3Key')
            
            if not audio_s3_key:
                raise Exception(f"No audio file found for language {language}")
            
            # Download audio file
            audio_path = os.path.join(temp_dir, 'audio.mp3')
            print(f"Downloading audio from s3://{CONTENT_BUCKET}/{audio_s3_key}")
            s3_client.download_file(CONTENT_BUCKET, audio_s3_key, audio_path)
            
            # Create subtitle file
            print("Creating subtitle file")
            subtitle_path = create_subtitle_file(script, temp_dir)
            
            # Create video segments for each scene
            video_segments = []
            
            # Hook
            if 'hook' in script:
                print("Creating hook video")
                hook = script['hook']
                hook_video = create_text_overlay_video(
                    hook['text'],
                    hook.get('duration', 3),
                    temp_dir
                )
                video_segments.append(hook_video)
            
            # Scenes
            if 'scenes' in script:
                for i, scene in enumerate(script['scenes']):
                    print(f"Creating scene {i+1} video")
                    scene_video = create_text_overlay_video(
                        scene['text'],
                        scene.get('duration', 10),
                        temp_dir
                    )
                    video_segments.append(scene_video)
            
            # CTA
            if 'cta' in script:
                print("Creating CTA video")
                cta = script['cta']
                cta_video = create_text_overlay_video(
                    cta['text'],
                    cta.get('duration', 3),
                    temp_dir
                )
                video_segments.append(cta_video)
            
            # Concatenate all video segments
            print(f"Concatenating {len(video_segments)} video segments")
            concatenated_video = concatenate_videos(video_segments, temp_dir)
            
            # Combine with audio
            print("Combining video with audio")
            video_with_audio = combine_audio_video(concatenated_video, audio_path, temp_dir)
            
            # Burn subtitles
            print("Burning subtitles")
            final_video = burn_subtitles(video_with_audio, subtitle_path, temp_dir)
            
            # Get video duration
            duration = get_video_duration(final_video)
            print(f"Final video duration: {duration} seconds")
            
            # Upload final video to S3
            draft_video_key = f"drafts/{content_id}/{language}_v1_draft.mp4"
            print(f"Uploading final video to s3://{CONTENT_BUCKET}/{draft_video_key}")
            s3_client.upload_file(
                final_video,
                CONTENT_BUCKET,
                draft_video_key,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            
            # Upload subtitle file to S3
            subtitle_key = f"drafts/{content_id}/{language}_v1_subtitles.srt"
            print(f"Uploading subtitles to s3://{CONTENT_BUCKET}/{subtitle_key}")
            s3_client.upload_file(
                subtitle_path,
                CONTENT_BUCKET,
                subtitle_key,
                ExtraArgs={'ContentType': 'text/plain'}
            )
            
            print("Video assembly completed successfully")
            
            return {
                'contentId': content_id,
                'draftVideoS3Key': draft_video_key,
                'subtitlesS3Key': subtitle_key,
                'duration': duration,
                'resolution': {'width': 1080, 'height': 1920},
                'format': 'mp4',
                'codec': 'h264',
                'language': language,
                **event
            }
        
    except Exception as e:
        print(f"Error in video assembler: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
