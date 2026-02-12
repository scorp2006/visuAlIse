from manim import *

class PhysicsScene(Scene):
    def construct(self):
        # Simple test - just text and a circle
        title = Text("Test Physics Scene", font_size=40, color=WHITE)
        self.play(Write(title))
        self.wait(1)
        
        circle = Circle(radius=1, color=WHITE)
        circle.shift(DOWN)
        self.play(Create(circle))
        self.wait(1)
