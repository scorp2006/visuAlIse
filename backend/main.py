
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
        lines = [l for l in text.split("\n") if not l.startswith("```")]
        text = "\n".join(lines)
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
