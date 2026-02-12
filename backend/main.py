
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import json, os, uuid, traceback, time, asyncio
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

from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        headers={"Access-Control-Allow-Origin": "*"},
        content={"detail": str(exc), "type": type(exc).__name__, "trace": tb[-800:]},
    )

# In-memory job store
jobs: dict = {}

# Global model
gemini_model = None

def get_model():
    global gemini_model
    if gemini_model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        # Using gemini-2.5-pro as requested by user
        gemini_model = genai.GenerativeModel(
            model_name="gemini-2.5-pro",
            system_instruction=SYSTEM_PROMPT,
        )
    return gemini_model

# ─── Models ───────────────────────────────────────────────────────────────────

class PhysicsRequest(BaseModel):
    question: str

class FixRequest(BaseModel):
    code: str
    error: str
    code_type: str 

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

async def call_llm(messages: list, json_mode: bool = True, max_tokens: int = 8000, max_retries: int = 3) -> str:
    model = get_model()
    
    # Format prompts: concatenate user messages for simple one-shot
    prompt_text = "\n".join([m["content"] for m in messages if m["role"] == "user"])
    
    # Config
    config = genai.GenerationConfig(
        temperature=0.2,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if json_mode else "text/plain",
    )

    # Retry logic
    for attempt in range(max_retries):
        try:
            # Async call using the stable SDK
            response = await model.generate_content_async(
                prompt_text, 
                generation_config=config
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            # Fallback for 429/quota/rate
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time) 
                    continue
            # If the specific model name fails, we should NOT fallback automatically without user knowing,
            # but for reliability we could try 1.5-pro if 2.5-pro is not yet active.
            # However, user was very specific: "gemini-2.5-pro this is what you have to use"
            raise
    return ""

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
                try:
                    fix_prompt = build_manim_fix_prompt(code, error_msg)
                    fixed = await call_llm(
                        [{"role": "user", "content": fix_prompt}], 
                        json_mode=False, 
                        max_tokens=4000
                    )
                    if "```python" in fixed:
                        fixed = fixed.split("```python")[1].split("```")[0]
                    elif "```" in fixed:
                        fixed = fixed.split("```")[1].split("```")[0]
                    code = fixed.strip()
                except:
                    pass
            else:
                jobs[job_id] = {"status": "error", "error": error_msg[:500]}

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/api/simulate", response_model=PhysicsResponse)
async def simulate(req: PhysicsRequest, background_tasks: BackgroundTasks):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    raw = await call_llm([
        {"role": "user", "content": build_user_prompt(req.question)},
    ])

    data = extract_json(raw)
    
    # Validation
    required = ["problem_type", "parameters", "equations", "explanation", "key_results", "p5js_code", "manim_code"]
    missing = [f for f in required if f not in data]
    if missing:
         raise HTTPException(status_code=500, detail=f"LLM missing fields: {missing}")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending"}
    background_tasks.add_task(run_manim_job, job_id, data["manim_code"], req.question)

    return PhysicsResponse(**data, job_id=job_id)

@app.get("/api/video/{job_id}", response_model=JobStatus)
async def get_video(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return JobStatus(**job)

@app.post("/api/fix-p5js")
async def fix_p5js(req: FixRequest):
    fix_prompt = build_p5js_fix_prompt(req.code, req.error)
    fixed = await call_llm(
        [{"role": "user", "content": fix_prompt}], 
        json_mode=False
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
    return {
        "status": "ok",
        "model": "gemini-2.5-pro",
        "api": "GOOGLE_GENERATIVEAI",
        "key_set": bool(os.getenv("GEMINI_API_KEY")),
    }
