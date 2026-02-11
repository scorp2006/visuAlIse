
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
    work_dir = tempfile.mkdtemp(prefix=f"manim_{job_id}_")
    script_path = os.path.join(work_dir, "scene.py")
    media_dir = os.path.join(work_dir, "media")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    cmd = [
        "manim",
        "-ql",                      # low quality (480p) — faster render
        "--media_dir", media_dir,
        "--disable_caching",
        script_path,
        "PhysicsScene",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:] if result.stderr else "Unknown Manim error")

    # Find the rendered MP4
    video_path = _find_video(media_dir)
    if not video_path:
        raise RuntimeError("Manim rendered but no MP4 file found")

    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(
        video_path,
        resource_type="video",
        public_id=f"physicsai/{job_id}",
        overwrite=True,
    )

    return upload_result["secure_url"]


def _find_video(media_dir: str) -> str | None:
    """Recursively find the first .mp4 in media_dir."""
    for root, dirs, files in os.walk(media_dir):
        for f in files:
            if f.endswith(".mp4"):
                return os.path.join(root, f)
    return None
