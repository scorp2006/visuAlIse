
import subprocess
import os
import tempfile
import uuid
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def render_manim(code: str, job_id: str) -> str:
    """
    Renders a Manim script to video, uploads to Cloudinary.
    Returns the public video URL.
    Raises RuntimeError on failure.
    """
    print(f"[Manim] Starting render for job {job_id}")
    work_dir = tempfile.mkdtemp(prefix=f"manim_{job_id}_")
    script_path = os.path.join(work_dir, "scene.py")
    media_dir = os.path.join(work_dir, "media")
    
    print(f"[Manim] Work directory: {work_dir}")
    print(f"[Manim] Script path: {script_path}")

    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[Manim] Script written successfully ({len(code)} bytes)")
    except Exception as e:
        raise RuntimeError(f"Failed to write Manim script: {e}")

    cmd = [
        "manim",
        "-ql",                      # low quality (480p) — faster render
        "--media_dir", media_dir,
        "--disable_caching",
        script_path,
        "PhysicsScene",
    ]
    
    print(f"[Manim] Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        raise RuntimeError("Manim command not found. Is Manim installed? Try: pip install manim")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Manim rendering timed out after 120 seconds")
    except Exception as e:
        raise RuntimeError(f"Manim subprocess error: {e}")

    print(f"[Manim] Return code: {result.returncode}")
    if result.stdout:
        print(f"[Manim] STDOUT: {result.stdout[:500]}")
    if result.stderr:
        print(f"[Manim] STDERR: {result.stderr[:500]}")

    if result.returncode != 0:
        error_msg = result.stderr[-2000:] if result.stderr else "Unknown Manim error"
        raise RuntimeError(f"Manim rendering failed: {error_msg}")

    # Find the rendered MP4
    print(f"[Manim] Searching for video in {media_dir}")
    video_path = _find_video(media_dir)
    if not video_path:
        raise RuntimeError(f"Manim rendered but no MP4 file found in {media_dir}")
    
    print(f"[Manim] Found video: {video_path} ({os.path.getsize(video_path)} bytes)")

    # Upload to Cloudinary
    try:
        print(f"[Manim] Uploading to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            video_path,
            resource_type="video",
            public_id=f"physicsai/{job_id}",
            overwrite=True,
        )
        url = upload_result["secure_url"]
        print(f"[Manim] Upload successful: {url}")
        return url
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}")


def _find_video(media_dir: str) -> str | None:
    """Recursively find the first .mp4 in media_dir."""
    print(f"[Manim] Scanning directory: {media_dir}")
    for root, dirs, files in os.walk(media_dir):
        print(f"[Manim] Checking {root}: {len(files)} files")
        for f in files:
            if f.endswith(".mp4"):
                return os.path.join(root, f)
    return None
