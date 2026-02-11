import os

# ─── prompt.py ────────────────────────────────────────────────────────────────
prompt_py = '''
PHYSICS_KNOWLEDGE_BASE = """
=== KINEMATICS ===
Projectile Motion:
  x(t) = v0*cos(θ)*t
  y(t) = v0*sin(θ)*t - 0.5*g*t²
  Time of flight: T = 2*v0*sin(θ)/g
  Max height: H = (v0*sin(θ))²/(2g)
  Range: R = v0²*sin(2θ)/g
  At max height: vy = 0

Relative Velocity (River-Boat):
  v_resultant = √(v_boat² + v_river²)
  θ_drift = arctan(v_river/v_boat)
  Time to cross: t = d/v_boat
  Drift = v_river * t

=== DYNAMICS ===
Newton's Laws:
  F = ma
  Normal force on incline: N = mg*cos(θ)
  Component along incline: F_parallel = mg*sin(θ)
  Friction: f = μ*N
  Net force on incline: F_net = mg*sin(θ) - μ*mg*cos(θ)
  Acceleration on incline: a = g*(sin(θ) - μ*cos(θ))

Atwood Machine:
  a = (m1 - m2)*g / (m1 + m2)
  T = 2*m1*m2*g / (m1 + m2)

=== OSCILLATIONS ===
Simple Pendulum:
  Period: T = 2π*√(L/g)
  Angular frequency: ω = √(g/L)
  θ(t) = θ0 * cos(ω*t)  [small angle approximation]
  x(t) = L*sin(θ(t))

Spring-Mass (SHM):
  Period: T = 2π*√(m/k)
  Angular frequency: ω = √(k/m)
  x(t) = A*cos(ω*t + φ)
  v(t) = -A*ω*sin(ω*t + φ)
  a(t) = -A*ω²*cos(ω*t + φ)
  Max velocity: v_max = A*ω
  Restoring force: F = -kx

=== ENERGY ===
  KE = 0.5*m*v²
  PE (gravity) = mgh
  PE (spring) = 0.5*k*x²
  Work-Energy: W_net = ΔKE
  Conservation: KE + PE = constant (no friction)

=== CIRCULAR MOTION ===
  Centripetal acceleration: ac = v²/r = ω²*r
  Centripetal force: Fc = mv²/r
  Period: T = 2πr/v
  Angular velocity: ω = 2π/T = v/r

=== COLLISIONS ===
  Momentum: p = mv
  Conservation: m1*v1 + m2*v2 = m1*v1\' + m2*v2\'
  Elastic: KE conserved, v1\' = (m1-m2)v1/(m1+m2) + 2m2*v2/(m1+m2)
  Perfectly inelastic: v_final = (m1*v1 + m2*v2)/(m1+m2)

=== CONSTANTS ===
  g = 9.81 m/s²
  π = 3.14159
"""

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are PhysicsAI — an expert physics teacher with 20 years of teaching experience AND a professional programmer skilled in Manim and p5.js.

Your mission: analyze any physics problem and generate:
1. A rigorous physics breakdown (parameters, equations, step-by-step reasoning)
2. A working p5.js interactive simulation
3. A working Manim animation script

""" + PHYSICS_KNOWLEDGE_BASE + """

═══════════════════════════════════════════════════════
P5.JS SIMULATION RULES (MUST FOLLOW EXACTLY)
═══════════════════════════════════════════════════════
- Canvas: always createCanvas(800, 500)
- Background: always background(0) — pure black
- ALL visuals in WHITE or GRAY tones only (fill(255), stroke(255), fill(180), etc.)
- The simulation MUST animate — objects move, time progresses
- Use deltaTime for frame-rate independent animation: t += deltaTime / 1000
- Reset time when animation completes: if (t >= totalTime) t = 0
- Include createSlider() for at least 2 key parameters
- Place sliders BELOW the canvas (they appear outside canvas automatically)
- Label each slider with createP() BEFORE creating the slider
- Add a Reset button with createButton("Reset")
- Draw coordinate axes as gray lines (stroke(60))
- Show live calculated values as white text on canvas (textSize(13), fill(255))
- Scale physics to canvas: use map() to convert real-world units to pixels
- Draw velocity vectors as white arrows
- Draw trajectory/path as white dotted line where applicable
- ALL variables must be declared at top with let
- NEVER use class syntax — use only global functions
- p5.js global functions available: setup, draw, createSlider, createButton, createP, map, dist, sin, cos, tan, atan2, sqrt, PI, TWO_PI, abs, min, max, constrain, lerp, noise, random, millis, deltaTime, width, height, frameRate, nf, text, textSize, textAlign, fill, stroke, noFill, noStroke, background, ellipse, rect, line, triangle, arc, point, beginShape, endShape, vertex, translate, rotate, push, pop, scale

COMMON MISTAKES TO AVOID:
- Never use arrow functions for setup/draw
- Never reference variables before declaring them
- Always reset t when animation loops (prevents NaN)
- Use nf(value, 1, 2) to format numbers in text()
- Use push()/pop() around transformed coordinate systems
- For inclined planes: use rotate() with push()/pop()
- For vectors/arrows: draw line then triangle at tip

═══════════════════════════════════════════════════════
MANIM ANIMATION RULES (MUST FOLLOW EXACTLY)
═══════════════════════════════════════════════════════
- ALWAYS start with: from manim import *
- Class name MUST be exactly: PhysicsScene
- ALWAYS inherit from Scene: class PhysicsScene(Scene):
- ALWAYS have: def construct(self):
- Background is BLACK by default — do not change it
- Use WHITE, GRAY, LIGHT_GRAY for all objects
- Use self.play() for all animations
- Use self.wait(n) for pauses between steps
- Total animation: 20-40 seconds

MANIM OBJECTS TO USE:
  Text("string", font_size=32, color=WHITE)  — for labels
  MathTex(r"equation", color=WHITE)  — for math equations
  Arrow(start, end, color=WHITE)  — for vectors
  Line(start, end, color=WHITE)  — for lines
  Dot(point, color=WHITE)  — for point objects
  Circle(radius=r, color=WHITE)  — for circular objects
  Rectangle(width=w, height=h, color=WHITE)  — for blocks
  NumberPlane(background_line_style={"stroke_opacity": 0.3})  — for grid
  VGroup(*objects)  — to group objects
  always_redraw(lambda: ...)  — for live-updating objects

MANIM ANIMATIONS TO USE:
  Create(obj)  — draw object
  Write(text_obj)  — write text
  FadeIn(obj)  — fade in
  FadeOut(obj)  — fade out
  Transform(obj1, obj2)  — morph
  obj.animate.move_to(point)  — move
  obj.animate.shift(direction)  — shift
  obj.animate.rotate(angle)  — rotate
  obj.animate.scale(factor)  — scale
  MoveAlongPath(obj, path)  — animate along curve

MANIM COORDINATES:
  Origin = ORIGIN = [0, 0, 0]
  Right = RIGHT = [1, 0, 0],  Left = LEFT = [-1, 0, 0]
  Up = UP = [0, 1, 0],  Down = DOWN = [0, -1, 0]
  Screen: x from -7 to 7, y from -4 to 4
  Positions: UL, UR, DL, DR, UP, DOWN, LEFT, RIGHT

MANIM STRUCTURE (follow this pattern):
  def construct(self):
      # 1. Title
      title = Text("Problem Title", font_size=40, color=WHITE)
      self.play(Write(title))
      self.wait(1)
      self.play(title.animate.scale(0.5).to_corner(UL))

      # 2. Setup scene (draw environment)

      # 3. Show equations

      # 4. Animate the physics

      # 5. Show results/conclusion
      self.wait(2)

MANIM MISTAKES TO AVOID:
- Never use deprecated: ShowCreation (use Create), GrowArrow (use Create)
- Never import specific items — always use: from manim import *
- Don\\'t use complex LaTeX that might fail — keep MathTex simple
- Use np.array([x, y, 0]) for custom positions (import numpy as np)
- Always add self.wait() between major animation steps
- ValueTracker for animated values: t = ValueTracker(0)

═══════════════════════════════════════════════════════
OUTPUT FORMAT — Respond ONLY with valid JSON
═══════════════════════════════════════════════════════
{
  "problem_type": "<concise problem category>",
  "parameters": {
    "<name>": {"value": <number>, "unit": "<unit>", "symbol": "<symbol>"}
  },
  "equations": [
    {"label": "<equation name>", "formula": "<equation>"}
  ],
  "explanation": [
    {"step": 1, "text": "<detailed physics reasoning step>"},
    {"step": 2, "text": "<...>"}
  ],
  "key_results": {
    "<result_name>": {"value": <number>, "unit": "<unit>"}
  },
  "p5js_code": "<complete p5.js code as single string, use \\n for newlines>",
  "manim_code": "<complete Manim Python script as single string, use \\n for newlines>"
}"""


def build_user_prompt(question: str) -> str:
    return f"""Physics Problem: "{question}"

Think through this step by step like an expert physics teacher:
1. Identify the problem type and relevant physics principles
2. Extract all given parameters with units
3. Write down the governing equations
4. Solve step by step showing all calculations
5. State the key results

Then generate:
- A p5.js simulation that animates the phenomenon with interactive sliders
- A Manim script that creates a beautiful educational animation

Both must be mathematically accurate and visually clear.
Output only the JSON response."""


def build_p5js_fix_prompt(original_code: str, error: str) -> str:
    return f"""The following p5.js code threw this error:
ERROR: {error}

BROKEN CODE:
{original_code}

Fix the code. Common fixes:
- Check all variables are declared before use
- Ensure map() arguments are in correct order: map(value, start1, stop1, start2, stop2)
- Ensure deltaTime is used correctly (divide by 1000 for seconds)
- Check for division by zero
- Ensure all p5.js function names are correct
- Fix any syntax errors

Return ONLY the fixed p5.js code as a plain string, no JSON, no markdown."""


def build_manim_fix_prompt(original_code: str, error: str) -> str:
    return f"""The following Manim code threw this error:
ERROR: {error}

BROKEN CODE:
{original_code}

Fix the code. Common Manim fixes:
- Replace ShowCreation with Create
- Replace GrowArrow with Create
- Fix coordinate arrays to have 3 elements: np.array([x, y, 0])
- Fix MathTex syntax — keep LaTeX simple
- Add missing self.play() wrappers
- Fix deprecated method names
- Ensure class is named exactly PhysicsScene

Return ONLY the fixed Python Manim code as a plain string, no JSON, no markdown."""
'''

# ─── manim_runner.py ──────────────────────────────────────────────────────────
manim_runner_py = '''
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
'''

# ─── main.py ──────────────────────────────────────────────────────────────────
main_py = '''
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import json, os, uuid
from dotenv import load_dotenv
from prompt import SYSTEM_PROMPT, build_user_prompt, build_p5js_fix_prompt, build_manim_fix_prompt
from manim_runner import render_manim

load_dotenv()

app = FastAPI(title="PhysicsAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store  { job_id: {"status": "pending"|"done"|"error", "url": "...", "error": "..."} }
jobs: dict = {}

groq_client: Groq | None = None


def get_groq():
    global groq_client
    if groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")
        groq_client = Groq(api_key=api_key)
    return groq_client


# ─── Models ───────────────────────────────────────────────────────────────────

class PhysicsRequest(BaseModel):
    question: str


class FixRequest(BaseModel):
    code: str
    error: str
    code_type: str  # "p5js" or "manim"


class PhysicsResponse(BaseModel):
    problem_type: str
    parameters: dict
    equations: list
    explanation: list
    key_results: dict
    p5js_code: str
    manim_code: str
    job_id: str


class JobStatus(BaseModel):
    status: str
    url: str | None = None
    error: str | None = None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def call_groq(messages: list, json_mode: bool = True, max_tokens: int = 8000) -> str:
    groq = get_groq()
    kwargs = dict(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    completion = groq.chat.completions.create(**kwargs)
    return completion.choices[0].message.content


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = [l for l in text.split("\\n") if not l.startswith("```")]
        text = "\\n".join(lines)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON in response")
    return json.loads(text[start:end])


async def run_manim_job(job_id: str, manim_code: str, question: str):
    """Background task: render Manim, retry once on failure."""
    jobs[job_id] = {"status": "pending"}
    code = manim_code

    for attempt in range(3):
        try:
            url = render_manim(code, job_id)
            jobs[job_id] = {"status": "done", "url": url}
            return
        except RuntimeError as e:
            error_msg = str(e)
            if attempt < 2:
                # Ask LLM to fix the code
                try:
                    fix_prompt = build_manim_fix_prompt(code, error_msg)
                    fixed = call_groq(
                        [{"role": "user", "content": fix_prompt}],
                        json_mode=False,
                        max_tokens=4000,
                    )
                    # Extract code block if wrapped in markdown
                    if "```python" in fixed:
                        fixed = fixed.split("```python")[1].split("```")[0]
                    elif "```" in fixed:
                        fixed = fixed.split("```")[1].split("```")[0]
                    code = fixed.strip()
                except Exception:
                    pass  # Use same code for next attempt
            else:
                jobs[job_id] = {"status": "error", "error": error_msg[:500]}


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/api/simulate", response_model=PhysicsResponse)
async def simulate(req: PhysicsRequest, background_tasks: BackgroundTasks):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    raw = call_groq([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": build_user_prompt(req.question)},
    ])

    data = extract_json(raw)

    required = ["problem_type", "parameters", "equations", "explanation",
                "key_results", "p5js_code", "manim_code"]
    missing = [f for f in required if f not in data]
    if missing:
        raise HTTPException(status_code=500, detail=f"LLM missing fields: {missing}")

    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_manim_job, job_id, data["manim_code"], req.question)

    return PhysicsResponse(**data, job_id=job_id)


@app.get("/api/video/{job_id}", response_model=JobStatus)
async def get_video(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return JobStatus(
        status=job["status"],
        url=job.get("url"),
        error=job.get("error"),
    )


@app.post("/api/fix-p5js")
async def fix_p5js(req: FixRequest):
    """Auto-fix broken p5.js code — called by frontend when iframe errors."""
    fix_prompt = build_p5js_fix_prompt(req.code, req.error)
    fixed = call_groq(
        [{"role": "user", "content": fix_prompt}],
        json_mode=False,
        max_tokens=4000,
    )
    if "```javascript" in fixed:
        fixed = fixed.split("```javascript")[1].split("```")[0]
    elif "```js" in fixed:
        fixed = fixed.split("```js")[1].split("```")[0]
    elif "```" in fixed:
        fixed = fixed.split("```")[1].split("```")[0]
    return {"p5js_code": fixed.strip()}


@app.get("/health")
async def health():
    return {"status": "ok", "model": "llama-3.3-70b-versatile"}
'''

# ─── requirements.txt ─────────────────────────────────────────────────────────
requirements_txt = """fastapi==0.128.8
uvicorn==0.40.0
groq==1.0.0
python-dotenv==1.0.1
pydantic==2.12.5
cloudinary==1.41.0
manim==0.18.1
"""

# ─── nixpacks.toml (Railway deployment) ───────────────────────────────────────
nixpacks_toml = """[phases.setup]
nixPkgs = ["python311", "ffmpeg", "cairo", "pkg-config", "pango", "glib"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
"""

# ─── .env template ────────────────────────────────────────────────────────────
env_template = """GROQ_API_KEY=your_groq_key_here
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
"""

# Write all files
files = {
    "D:/Phyai/backend/prompt.py":        prompt_py,
    "D:/Phyai/backend/manim_runner.py":  manim_runner_py,
    "D:/Phyai/backend/main.py":          main_py,
    "D:/Phyai/backend/requirements.txt": requirements_txt,
    "D:/Phyai/backend/nixpacks.toml":    nixpacks_toml,
    "D:/Phyai/backend/.env.example":     env_template,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {path}")

print("\nAll backend files written.")
