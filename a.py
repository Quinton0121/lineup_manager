from manim import *

class TenCircles(Scene):
    def construct(self):
        # Create a group of 10 circles
        circles = VGroup(*[Circle() for _ in range(10)])

        # Arrange the circles in a horizontal line
        circles.arrange_submobjects(RIGHT)

        # Add the circles to the scene
        self.play(*[Create(circle) for circle in circles])

        # Wait for a moment before ending the scene
        self.wait()

# Split the 10 circles into 5 groups
        circle_groups = [VGroup(*circles[i:i + 2]) for i in range(0, 10, 2)]

        # Animate the separation of the groups
        for group in circle_groups:
            self.play(group.animate.shift(UP * 0.5))