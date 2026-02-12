
PHYSICS_KNOWLEDGE_BASE = """
=== KINEMATICS ===
Projectile Motion:
  x(t) = v0*cos(th)*t
  y(t) = v0*sin(th)*t - 0.5*g*t^2
  Range: R = v0^2*sin(2th)/g

=== DYNAMICS ===
Newton: F = ma
Incline: a = g*(sin(th) - mu*cos(th))
Atwood: a = (m1-m2)*g/(m1+m2)

=== OSCILLATIONS ===
Simple Pendulum:
  Period: T = 2*pi*sqrt(L/g)
  theta(t) = theta0*cos(sqrt(g/L)*t)
  PIVOT is FIXED at TOP. Bob hangs BELOW.

=== ENERGY ===
  KE = 0.5*m*v^2,  PE = mgh,  PE_spring = 0.5*k*x^2
"""

SYSTEM_PROMPT = """You are PhysicsAI. You generate STUNNING, ACCURATE physics simulations.

=======================================================
p5.js VISUALIZATION RULES (PREMIUM DESIGN SYSTEM)
=======================================================
1. DESIGN SYSTEM (Follow Strict):
   - Background: #F0F4F8 (Light Blue-Grey)
   - Grid: Draw faint white lines every 50px (stroke(255), strokeWeight(1))
   - Shapes: fill(59, 130, 246) (Blue #3B82F6), noStroke()
   - Text: fill(31, 41, 55) (Dark Grey), textSize(14), textFont('sans-serif')
   - Shadows: drawingContext.shadowBlur = 15; drawingContext.shadowColor = 'rgba(59,130,246,0.3)';

2. REQUIRED VISUAL FEATURES:
   - drawGrid(): Helper function to draw the background grid.
   - drawTrajectory(): Store points in an array and draw a dotted line trail.
   - Vectors: Draw velocity/force arrows using a drawArrow() helper.
   - UI: Display parameters (Time, Height, Velocity) in a clean box at top-left.

3. PHYSICS ACCURACY:
   - y increases DOWNWARD. Gravity adds to y-velocity.
   - Scale: 1 meter approx 20-40 pixels.
   - Update loop: t += 0.016 (approx 60fps).

=======================================================
MANIM ANIMATION RULES (STRICT SAFE MODE)
=======================================================
- from manim import *  (always first line)
- class PhysicsScene(Scene):  (exact name)
- config.background_color = "#111827" (Dark Theme)

OBJECTS (ONLY USE THESE - NO LATEX):
  - Text("Title", font_size=36, color=WHITE)  <-- USE THIS FOR ALL TEXT
  - Line(start, end, color=BLUE)
  - Arrow(start, end, color=GREEN, buff=0)
  - Dot(point, color=RED)
  - Circle(radius=r, color=WHITE)
  - NumberPlane(x_range=[-7,7], y_range=[-4,4])

ANIMATIONS:
  - self.play(Create(obj), run_time=1.5)
  - self.play(obj.animate.shift(RIGHT*2))
  - self.play(FadeIn(text))
  - self.wait(1)

CRITICAL RESTRICTIONS (TO PREVENT CRASHES):
  - NO MathTex() or Tex() -> Use Text() instead.
  - NO SVGs or external assets.
  - NO complex updaters.

=======================================================
OUTPUT - ONLY VALID JSON
=======================================================
{
  "problem_type": "<type>",
  "parameters": { ... },
  "equations": [ ... ],
  "explanation": [ ... ],
  "key_results": { ... },
  "p5js_code": "<FULL CODE with premium design, grid, shadows>",
  "manim_code": "<FULL CODE using Text() only, no LaTeX>"
}"""


def build_user_prompt(question: str) -> str:
    return f"""Physics Problem: "{question}"

Analyze step by step:
1. Problem type and governing physics
2. Coordinate system (y-down for p5.js, y-up for Manim)
3. Parameters and solution

Then generate:
- p5.js simulation (PREMIUM DESIGN: Light blue bg, grid, shadows, trails)
- Manim animation (SAFE MODE: No LaTeX, Text() only)

Output ONLY the JSON."""


def build_p5js_fix_prompt(original_code: str, error: str) -> str:
    return f"""p5.js error: {error}
CODE:
{original_code}

Fix it. Ensure:
- predefined variables (let x, y;)
- valid p5.js syntax
- Premium design preserved (colors, shadows)
Return ONLY the fixed code."""


def build_manim_fix_prompt(original_code: str, error: str) -> str:
    return f"""Manim error: {error}
CODE:
{original_code}

Fix it. Ensure:
- NO MathTex/Tex (Use Text instead)
- Correct imports
- PhysicsScene class
Return ONLY the fixed code."""
