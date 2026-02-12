
SYSTEM_PROMPT = """You are PhysicsAI, a high-precision physics engine. Generate MONOCHROME (Black & White) p5.js simulations.

=== p5.js MONOCHROME ENGINE (Priority) ===
1. AESTHETICS (Strict B&W):
   - Background: #FFFFFF (Pure White).
   - Grid: stroke(240), strokeWeight(1), line every 40px.
   - Primary Objects: fill(0), noStroke().
   - Secondary/Shadows: fill(200), stroke(150), dashed lines (setLineDash).
   - Dynamic Feedback: Use black dotted trails. Force vectors as black arrows. Velocity vectors as gray thick lines.
2. INTERACTIVE CONTROLS (Mandatory):
   - Use createSlider() for physical parameters.
   - Design a HUD panel: drawing rect(20, height-100, 250, 80) in #FFF with stroke(0).
   - Sliders must have black text labels inside the HUD.
3. PHYSICS:
   - Scale: 1m = 40px. y increases DOWN. 60 FPS.

=== MANIM SUMMARY (Legacy) ===
- Strict B&W (Black background, White shapes/text). No LaTeX.

=== JSON OUTPUT ===
{
  "problem_type": "str",
  "parameters": {"name": {"value": 0, "unit": "u", "symbol": "s"}},
  "equations": [{"label": "Var", "formula": "LaTeX string"}],
  "explanation": [{"step": 1, "text": "Step description..."}],
  "key_results": {"Name": {"value": 0, "unit": "u"}},
  "p5js_code": "Complete p5.js code",
  "manim_code": "Complete Manim code"
}
"""


def build_user_prompt(question: str) -> str:
    return f"""Physics Problem: "{question}"

Instructions:
1. Generate an interactive MONOCHROME p5.js simulation (B&W only).
2. Include sliders for key parameters.
3. Show vectors and trails clearly in black/gray on white.
4. Simple Manim video (B&W).

Output ONLY JSON."""


def build_p5js_fix_prompt(original_code: str, error: str) -> str:
    return f"""The following p5.js code threw this error:
ERROR: {error}

BROKEN CODE:
{original_code}

Fix the code. Return ONLY the fixed p5.js code, no JSON, no markdown."""


def build_manim_fix_prompt(original_code: str, error: str) -> str:
    return f"""The following Manim code threw this error:
ERROR: {error}

BROKEN CODE:
{original_code}

Fix the code. Common fixes:
- Replace ShowCreation with Create, GrowArrow with Create
- Replace MathTex/Tex with Text()
- Fix coordinate arrays to 3 elements: np.array([x, y, 0])
- Ensure class is named exactly PhysicsScene

Return ONLY the fixed Python Manim code, no JSON, no markdown."""
