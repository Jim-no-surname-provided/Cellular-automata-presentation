import random

import numpy as np
from manim import *
from manim_slides.slide import Slide

from app.data import Boid, Credits
from app.paths import RES_DIR, SLIDES_DIR


class Boids(Slide):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("output_folder", SLIDES_DIR)
        super().__init__(*args, **kwargs)

    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        # Show the central boid and introduce the surrounding flock
        scale = 1.5
        c_boid = Boid(
            color=GREEN,
            stroke_width=scale,
            neighborhood_radius=scale,
            obstacle_radius=scale * 2,
            height=0.2 * scale,
        ).set_z_index(10)
        flock = VGroup(c_boid)
        self.add(flock)
        self.play(Create(c_boid))
        self.next_slide()

        positions = [
            (-1, 1.1),
            (-1.5, 0.5),
            (-1.12, -0.3),
            (-0.71, 0.09),
            (-0.15, -0.78),
            (-0.59, 0.59),
            (-0.11, 0.86),
            (1, 0.5),
        ]

        boids = [
            Boid(
                stroke_width=c_boid.body.stroke_width,
                neighborhood_radius=c_boid.neighborhood_radius,
                obstacle_radius=c_boid.neighborhood_radius,
                height=c_boid.height,
            )
            .move_to([scale * x, scale * y, 0])
            .set_z_index(10)
            for x, y in positions
        ]
        flock.add(*boids)

        # rotate
        original_rotations = [random.uniform(-60, 60) * DEGREES for _ in boids]
        for boid, angle in zip(boids, original_rotations):
            boid.rotate(angle, about_point=boid.position())
            boid.heading = angle

        self.play(
            LaggedStart(
                *[Create(boid, run_time=0.5) for boid in boids],
                lag_ratio=0.2,
            )
        )

        # Neighborhood circle
        circle = (
            Circle(
                radius=scale,
                color=GRAY,
                fill_opacity=0.7,
            )
            .move_to(c_boid.position())
            .set_z_index(-1)
        )
        flock.add(circle)
        self.play(Create(circle))

        # Make neighborhood
        neighbors = [
            boid
            for boid in boids
            if np.linalg.norm(boid.position() - c_boid.position())
            <= c_boid.neighborhood_radius
        ]
        self.next_slide()

        # Define rules
        rules = Paragraph(
            "Rules",
            "\tSeparation",
            "  \tAlignment",
            " \tCohesion",
            alignment="left",
            line_spacing=1.2,
        )
        rules[0].set(weight=BOLD).scale(1.2)
        rules.scale(0.6).move_to(RIGHT * 0.5, aligned_edge=LEFT)
        for rule in rules[1:]:
            rule.set_opacity(0.7)

        # Move flock and write first rule
        self.play(
            flock.animate.shift(LEFT * config.frame_width / 6),
            LaggedStart(Write(rules[0]), Write(rules[1]), lag_ratio=0.3),
        )

        # Lines from center boid to the rest
        seperation_lines = [
            Line(
                c_boid.position(),
                boid.position(),
                color=GREEN,
                stroke_width=1 * scale,
                buff=0.02,
            ).set_z_index(1)
            for boid in neighbors
        ]
        self.play(
            *[GrowFromPoint(line, c_boid.position()) for line in seperation_lines]
        )

        # Calc seperation vector
        separation_direction = np.zeros(3)
        for boid in neighbors:
            displacement = boid.position() - c_boid.position()
            distance = np.linalg.norm(displacement)
            if distance > 0:
                separation_direction -= displacement / (distance**2)
        separation_direction /= np.linalg.norm(separation_direction)

        # Make separation arrow
        separation_arrow = Arrow(
            c_boid.position(),
            c_boid.position() + separation_direction * 0.5,
            color=RED,
        ).set_z_index(1)
        self.play(GrowArrow(separation_arrow))

        self.next_slide()
        self.play(
            *[Uncreate(line) for line in seperation_lines],
            Write(rules[2]),
            GrowArrow(separation_arrow, reverse_rate_function=True, remover=True),
        )

        # Desired directions
        alignment_dir = 15 * DEGREES
        target_rotations = [
            alignment_dir + random.uniform(-10, 10) * DEGREES for _ in boids
        ]
        alignment_lines = []
        alignment_animations = []

        # Animate rotation and line growth
        lines_length = scale * 1 / 3
        for boid, target in zip(boids, target_rotations):
            line = Line(
                boid.position(),
                boid.nose() + boid.direction() * lines_length,
                color=boid.body.get_color(),
                stroke_width=1 * scale,
            ).set_z_index(1)
            boid.add(line)
            alignment_lines.append(line)
            alignment_animations.append(self.align_boid(boid, line, target))
        self.play(*alignment_animations)

        # dir lines of center boid
        c_dir = np.array([-np.sin(alignment_dir), np.cos(alignment_dir), 0])
        c_line_goal = Line(
            c_boid.position(),
            c_boid.position() + c_dir * lines_length,
            color=BLUE,
            stroke_width=1 * scale,
        ).set_z_index(1)
        c_line_current = Line(
            c_boid.position(),
            c_boid.position() + UP * lines_length,
            color=c_boid.body.get_color(),
            stroke_width=1 * scale,
        ).set_z_index(1)

        # arrow of center boid
        alignment_arrow = Arrow(
            c_boid.position(),
            c_boid.position() + LEFT * lines_length,
            color=RED,
            buff=0,
        ).set_z_index(1)
        alignment_lines.extend([c_line_goal, c_line_current])

        # Add arrow and line goal
        self.play(
            LaggedStart(
                GrowFromPoint(c_line_current, c_boid.position(), run_time=1),
                GrowFromPoint(c_line_goal, c_boid.position(), run_time=1),
                GrowArrow(alignment_arrow, run_time=1),
                lag_ratio=0.1,
            )
        )
        self.next_slide()
        self.play(
            *[Uncreate(line) for line in alignment_lines],
            GrowArrow(alignment_arrow, reverse_rate_function=True, remover=True),
        )

        # Restore the original headings and introduce cohesion
        for boid, line in zip(boids, alignment_lines):
            boid.remove(line)
        self.play(
            *[
                Rotate(boid, original - boid.heading, about_point=boid.position())
                for boid, original in zip(boids, original_rotations)
            ],
            Write(rules[3]),
        )
        for boid, original in zip(boids, original_rotations):
            boid.heading = original

        # Find cohesion center
        neighbor_center = np.mean([boid.position() for boid in neighbors], axis=0)
        cohesion_dot = Dot(neighbor_center).set_z_index(2)
        cohesion_lines = [
            Line(boid.position(), neighbor_center, color=GREEN_E) for boid in neighbors
        ]

        # Connect cohesion center with boids
        self.play(
            GrowFromCenter(cohesion_dot),
            *[
                GrowFromPoint(line, boid.position())
                for line, boid in zip(cohesion_lines, neighbors)
            ],
        )

        # Point towards direction cohesion center
        cohesion_arrow = Arrow(
            c_boid.position(),
            neighbor_center,
            color=RED_E,
            buff=0.1,
        ).set_z_index(1)
        self.play(GrowArrow(cohesion_arrow))
        self.next_slide()

        # Uncreate stuff
        self.play(
            *[Uncreate(line) for line in cohesion_lines],
            GrowArrow(cohesion_arrow, reverse_rate_function=True, remover=True),
            Uncreate(circle),
            Uncreate(cohesion_dot),
        )

        all_boids = [c_boid, *boids]
        for boid in all_boids:
            boid.set_tracking_list(all_boids)
            boid.set_obstacles(list(rules))

        self.play(*[boid.fly(duration=5) for boid in all_boids])

        # Add more boids
        extra_boids = [
            Boid(
                stroke_width=c_boid.body.stroke_width,
                neighborhood_radius=c_boid.neighborhood_radius,
                obstacle_radius=c_boid.neighborhood_radius,
                height=c_boid.height,
            )
            .move_to(
                2 * LEFT
                + random.gauss(mu=0, sigma=1.56) * UP
                + random.gauss(mu=0, sigma=1.56) * RIGHT
            )
            .set_z_index(10)
            for _ in range(45)
        ]

        # Add the new boids while old ones fly
        self.play(
            *[boid.fly(duration=0.5) for boid in all_boids],
            *[Create(boid, run_time=0.5) for boid in extra_boids],
        )

        # Update info on them and the rest
        all_boids.extend(extra_boids)
        for boid in all_boids:
            boid.set_tracking_list(all_boids)
            boid.set_obstacles(list(rules))
            
        self.play(
            *[boid.fly(duration=20) for boid in all_boids],
        )

        self.next_slide()

        # Me and the boids img and credits
        self.play(
            *[
                Uncreate(mobject) if isinstance(mobject, VMobject) else FadeOut(mobject)
                for mobject in list(self.mobjects)
            ]
        )
        photo = ImageMobject(str(RES_DIR / "Me and the boids" / "Me and the boids.png"))
        photo.set_height(4).move_to(ORIGIN)
        photo_credits = Credits("Florida Museum photo by Zachary Randall")
        self.play(FadeIn(photo), FadeIn(photo_credits))
        self.next_slide(auto_next=True)

        # Fade out and continue to the next scene
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

    def align_boid(self, boid, line, target):
        initial_heading = boid.heading

        def update(mobject, alpha):
            # Rotate the boid and grow its child line without competing animations
            heading = interpolate(initial_heading, target, alpha)
            mobject.rotate(heading - mobject.heading, about_point=mobject.position())
            mobject.heading = heading
            nose = mobject.nose()
            line.put_start_and_end_on(
                nose,
                nose + mobject.direction() * max(alpha, 1e-6) * 0.25,
            )

        return UpdateFromAlphaFunc(boid, update)
