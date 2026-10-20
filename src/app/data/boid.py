import numpy as np
from manim import (
    BLUE,
    DEGREES,
    ORIGIN,
    Animation,
    Mobject,
    Polygon,
    UpdateFromAlphaFunc,
    VectorizedPoint,
    VGroup,
    config,
    linear,
)


class Boid(VGroup):
    def __init__(
        self,
        height=0.2,
        stroke_width=1,
        neighborhood_radius=1,
        obstacle_radius=1,
        color=BLUE,
        **kwargs,
    ):
        super().__init__(**kwargs)
        half_base = height / 4
        self.body = Polygon(
            [0, height / 2, 0],
            [-half_base, -height / 2, 0],
            [half_base, -height / 2, 0],
            color=color,
            fill_opacity=0.7,
            stroke_width=stroke_width,
        )
        self.height = height
        self.neighborhood_radius = neighborhood_radius
        self.obstacle_radius = obstacle_radius
        self.anchor = VectorizedPoint(ORIGIN)
        self.add(self.body, self.anchor)
        self.move_to(ORIGIN)
        self.heading = 0.0
        self.tracking_list = []
        self.obstacles: list[Mobject] = []
        # Manim units per second
        self.speed = 2
        # Radians per second, initially 90 degrees per second
        self.max_angular_speed = 120 * DEGREES
        self.goal_dir = self.direction()

    def position(self):
        return self.anchor.get_center()

    def nose(self):
        return self.body.get_vertices()[0]

    def direction(self):
        return np.array([-np.sin(self.heading), np.cos(self.heading), 0])

    def set_tracking_list(self, boids):
        # Store references to the other boids to check during flight
        self.tracking_list = [boid for boid in boids if boid is not self]
        return self

    def set_obstacles(self, obstacles: list[Mobject]):
        # Store references to the obstacles to avoid
        self.obstacles = obstacles
        return self

    def fly(self, duration: float = 5) -> Animation:
        # Reset the clock for this flight
        self._flight_elapsed = 0.0
        # Start with the current heading as the desired direction
        self.goal_dir = self.direction()

        # Let Manim drive the flight through animation progress
        return UpdateFromAlphaFunc(
            self,
            lambda boid, alpha: boid.update_flight(alpha, duration),
            run_time=duration,
            rate_func=linear,
        )

    def update_flight(self, alpha: float, duration: float):
        # Calculate the time since the previous update
        elapsed = alpha * duration
        dt = elapsed - self._flight_elapsed
        self._flight_elapsed = elapsed
        if dt <= 0:
            return

        neighborhood = [
            boid
            for boid in self.tracking_list
            if np.linalg.norm(boid.position() - self.position())
            <= self.neighborhood_radius
        ]

        obstacles_a = self.obstacles_avoidance_vec()
        separation = self.separation_vec(neighborhood)
        alignment = self.alignment_vec(neighborhood)
        cohesion = self.cohesion_vec(neighborhood)
        # TODO: test weights
        self.goal_dir = 3 * obstacles_a + separation + alignment + cohesion

        # Turn toward the goal using the shortest angular difference
        # 0 means no change
        if np.linalg.norm(self.goal_dir[:2]) > 0:
            # Calc rotation this frame
            goal_heading = np.arctan2(-self.goal_dir[0], self.goal_dir[1])
            angle_difference = (goal_heading - self.heading + np.pi) % (
                2 * np.pi
            ) - np.pi
            max_turn = self.max_angular_speed * dt

            # Rotate
            turn = np.clip(angle_difference, -max_turn, max_turn)
            self.rotate(turn, about_point=self.position())
            self.heading += turn

        # Move in the current heading at the configured speed
        self.shift(self.direction() * self.speed * dt)

    def obstacles_avoidance_vec(self):
        position = self.position()
        radius = self.obstacle_radius
        avoidance = np.zeros(3)
        if radius <= 0:
            return avoidance

        # Account for the boid's size in every direction
        body_radius = max(
            np.linalg.norm(vertex[:2] - position[:2])
            for vertex in self.body.get_vertices()
        )

        # Weight each push by how far it enters the neighborhood
        def add_push(direction, clearance):
            if clearance >= radius:
                return
            weight = np.clip(1 - clearance / radius, 0, 1)
            avoidance[:] += direction * weight

        # Push inward from the screen edges
        left = -config.frame_width / 2 + body_radius
        right = config.frame_width / 2 - body_radius
        bottom = -config.frame_height / 2 + body_radius
        top = config.frame_height / 2 - body_radius

        add_push(np.array([1, 0, 0]), position[0] - left)
        add_push(np.array([-1, 0, 0]), right - position[0])
        add_push(np.array([0, 1, 0]), position[1] - bottom)
        add_push(np.array([0, -1, 0]), top - position[1])

        # Find the closest point on each expanded obstacle rectangle
        for obstacle in self.obstacles:
            left = obstacle.get_left()[0] - body_radius
            right = obstacle.get_right()[0] + body_radius
            bottom = obstacle.get_bottom()[1] - body_radius
            top = obstacle.get_top()[1] + body_radius

            closest = np.array(
                [
                    np.clip(position[0], left, right),
                    np.clip(position[1], bottom, top),
                    position[2],
                ]
            )
            away = position - closest
            distance = np.linalg.norm(away)

            if distance > 0:
                add_push(away / distance, distance)
                continue

            # Inside or touching the rectangle, push toward the nearest exit
            exits = [
                (position[0] - left, np.array([-1, 0, 0])),
                (right - position[0], np.array([1, 0, 0])),
                (position[1] - bottom, np.array([0, -1, 0])),
                (top - position[1], np.array([0, 1, 0])),
            ]
            _, direction = min(exits, key=lambda exit: exit[0])
            add_push(direction, 0)

        return avoidance

    def separation_vec(self, neighborhood):
        # Push away from neighbors with a distance-based weight
        separation = np.zeros(3)
        radius = self.neighborhood_radius
        if radius <= 0:
            return separation

        position = self.position()
        for boid in neighborhood:
            away = position - boid.position()
            distance = np.linalg.norm(away)
            if 0 < distance < radius:
                weight = 1 - distance / radius
                separation += away / distance * weight

        return separation

    def alignment_vec(self, neighborhood):
        # Average the neighbors' heading vectors
        if not neighborhood:
            return np.zeros(3)

        return np.mean(
            [boid.direction() for boid in neighborhood],
            axis=0,
        )

    def cohesion_vec(self, neighborhood):
        # Find the direction toward the neighbors' average position
        if not neighborhood:
            return np.zeros(3)

        center = np.mean(
            [boid.position() for boid in neighborhood],
            axis=0,
        )
        toward_center = center - self.position()
        distance = np.linalg.norm(toward_center)
        if distance == 0:
            return np.zeros(3)

        return toward_center / distance
