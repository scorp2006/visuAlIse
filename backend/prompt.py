
SYSTEM_PROMPT = """You are PhysicsAI. Generate STUNNING p5.js simulations & RELIABLE Manim videos.

=== p5.js PREMIUM DESIGN (Mandatory) ===
1. VISUALS:
   - Background: #F0F4F8 (Light Blue-Grey).
   - Grid: stroke(255), strokeWeight(1), line every 50px.
   - Geometry: fill(59,130,246) (Blue), noStroke(), Shadows (shadowBlur=15, shadowColor='rgba(59,130,246,0.3)').
   - Text: fill(31,41,55), sans-serif.
2. HELPERS:
   - Implement drawGrid() & drawTrajectory() (dotted trails).
   - Show Vectors (arrows).
   - UI Panel top-left.
3. PHYSICS:
   - y increases DOWN. Scale: 1m ~ 20px. 60fps loop.

=== MANIM SAFE MODE (Mandatory) ===
1. RESTRICTIONS:
   - NO LaTeX (MathTex/Tex) -> CRASHES. Use Text() only.
   - NO complex updaters.
2. SETUP:
   - from manim import *
   - class PhysicsScene(Scene):
   - config.background_color = "#111827"

=== JSON OUTPUT ONLY ===
{
  "problem_type": "str",
  "parameters": {"name": {"value": 0, "unit": "u", "symbol": "s"}},
  "equations": [{"label": "l", "formula": "f"}],
  "explanation": [{"step": 1, "text": "Reasoning step..."}],
  "key_results": {"name": {"value": 0, "unit": "u"}},
  "p5js_code": "Full p5.js code string",
  "manim_code": "Full Manim python code string"
}
"""


def build_user_prompt(question: str) -> str:
    return f"""Physics Problem: "{question}"

Analyze:
1. Physics & Coordinates
2. Solve Parameters
3. Explanation

Generate:
- p5.js (PREMIUM: Blue bg, grid, shadows, trails)
- Manim (SAFE: No LaTeX, Text() only)

Output ONLY JSON."""


def build_p5js_fix_prompt(original_code: str, error: str) -> str:
    return f"""p5.js error: {error}
CODE:
{original_code}

Fix it. Ensure:
- Valid syntax
- Premium design (colors, shadows)
Return fixed code only."""


def build_manim_fix_prompt(original_code: str, error: str) -> str:
    return f"""Manim error: {error}
CODE:
{original_code}
      
Fix it. Ensure:
- NO MathTex/Tex (Use Text)
- PhysicsScene class
Return fixed code only."""
