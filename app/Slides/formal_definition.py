import random

from BlockCA import BlockCA
from CellularAutomatonGrid import CellularAutomatonGrid
from manim import *
from manim_slides.slide import Slide

from app.VideoMobject import VideoMobject


class Formal_Def(Slide):

    THIRD_UP = UP*config.frame_height*(1/6)
    THIRD_DOWN = DOWN*config.frame_height*(1/6)
    TOP = (config.frame_height/2)*UP
    EINSTEIN_HAT_FILE = r"src\CA examples\Quick einstein hat GoL.mp4"

    FOCUS_LETTER_SCALE = 1.4

    def construct(self):
        self.intro()

        self.state_alphabet()

        self.cell_array()

        self.neighborhood_index()

        self.global_map()
        self.wait(1e-9)

    def intro(self):
        expr = MathTex(
            r"(A, \mathbb{Z}^d, X, \tau)",
            substrings_to_isolate=["A", "\\mathbb{Z}^d", "X", "\\tau"]
        ).scale(1.3)

        expr.move_to(self.THIRD_UP)

        self.play(Write(expr))

        example = MathTex(
            r"(\mathbb{B}, \_, \_, \_)"
        )
        self.expr = expr
        self.example = example
        self.example.scale(1.3).to_corner(DL, buff=0.6)
        self.next_slide()

    def focus_letter_animation(self, L):
        return L.animate.scale(
            self.FOCUS_LETTER_SCALE,
            about_point=L.get_bottom()
        ).set_color(YELLOW)

    def unfocus_letter_animation(self, L):
        return L.animate.scale(
            1/self.FOCUS_LETTER_SCALE,
            about_point=L.get_bottom()
        ).set_color(WHITE)

    def update_example(self, A, Zd, X, tau):
        tex = fr"({A}, {Zd}, {X}, {tau})"
        new = MathTex(tex).scale(1.3)
        new.to_corner(DL, buff=0.6)
        self.play(Transform(self.example, new), run_time=0.4)

    def state_alphabet(self):
        A = self.expr.get_part_by_tex("A")
        self.play(
            self.focus_letter_animation(A),
            run_time=0.4
        )
        self.next_slide()

        self.play(
            self.expr.animate.to_corner(DR, buff=0.6).scale(0.8),
            run_time=0.4
        )

        self.neural_CA()
        block_ca = self.block_ca()

        self.play(Write(self.example))
        self.next_slide()
        self.play(
            Uncreate(block_ca),
            self.unfocus_letter_animation(A),
            run_time=0.4)

    def neural_CA(self):
        # Add neural CA video
        neural_ca = VideoMobject(
            r"src\CA examples\Growing Neural Cellular Automata.mp4"
        ).scale(0.5)

        neural_ca_g = Group(neural_ca, SurroundingRectangle(neural_ca))

        self.add(neural_ca_g)
        credits_tex = MathTex(
            r"\text{Growing NCA (Mordvintsev et al., 2020, Distill)}",
            font_size=10,
            color=GREY_B,
        ).to_corner(UR, buff=0.1).set_z_index(9999)
        self.play(FadeIn(credits_tex))
        self.wait(24)
        self.next_slide()

        # Left: A = R^16
        A_scale = 0.6
        A_gap = 3
        A_eq = MathTex(r"A = \mathbb{R}^{16}").scale(A_scale*2)
        A_eq.move_to(ORIGIN).shift(LEFT * A_gap/2)

        self.play(neural_ca_g.animate.scale(0.5).to_corner(UL, buff=1))
        self.play(Write(A_eq))
        self.next_slide()

        # Right side: the 16-dim vector
        entries = ["r", "g", "b", "a"] + [f"h_{{{i}}}" for i in range(12)]

        vec = MathTex(
            r"\left[ \begin{array}{c}"
            + r"\\ ".join(entries)
            + r"\end{array} \right]"
        ).scale(A_scale)

        vec.next_to(A_eq, RIGHT, buff=A_gap)

        self.play(
            Write(vec),
            run_time=0.4
        )

        # arrows: from A_eq to each row
        arrows = []
        # Hard coded positions of each element in the vector
        element_indexes = [
            *range(28, 32),
            *range(32, 54, 2),
            55
        ]

        col_x = vec[0][28].get_center()[0]
        for i in element_indexes:
            row_y = vec[0][i].get_center_of_mass()[1]
            arrow = Arrow(
                start=A_eq.get_right() + RIGHT*0.2,
                end=[col_x - 0.8, row_y, 0],
                stroke_width=1,
                tip_length=0.1,
                buff=0.01
            )
            arrows.append(arrow)

        self.play(
            LaggedStart(*[GrowArrow(arr) for arr in arrows], lag_ratio=0.25),
            run_time=0.4
        )

        self.next_slide()
        self.play(
            Uncreate(A_eq),
            *[arr.animate.scale(0.01, about_point=arr.get_start())
              for arr in arrows
              ],
            Uncreate(vec),
            FadeOut(neural_ca_g),
            FadeOut(credits_tex),
            run_time=0.5
        )
        self.remove(*arrows)

    def block_ca(self):
        # 16×16 Block CA
        grid = BlockCA(
            rows=16,
            cols=16,
            cell_size=0.4,   # adjust if needed
            gap=0.4
        ).scale(0.5)

        # Random alive/dead initialization
        alive_coords = {
            (x, y)
            for x in range(-8, 8)
            for y in range(-8, 8)
            if random.random() < 0.5
        }

        grid.set_alive(alive_coords)
        grid.update_cell_colors()

        # Position it at THIRD_UP
        grid.move_to(self.THIRD_UP*0.5)

        self.play(
            Create(grid),
            run_time=0.4)
        self.next_slide()
        h0 = grid.cells[0].get_height()
        gap = 0.2
        scale_factor = (h0 + gap) / h0
        self.play(
            *[line.animate.set_color(WHITE) for line in grid.grid_lines],
            *[cell.animate.scale(scale_factor) for cell in grid.cells],
            run_time=0.4,
        )
        return grid

    def cell_array(self):
        self.Zd = self.expr.get_part_by_tex(r"\mathbb{Z}^d")
        self.play(
            self.focus_letter_animation(self.Zd),
            run_time=0.4
        )

        self.next_slide()
        self.update_example(r"\mathbb{B}", r"\mathbb{Z}^1", r"\_", r"\_")
        self.next_slide()
        self.snowflake()
        self.einstein_hat()

    def snowflake(self):
        snowflake_growth = VideoMobject(
            r"src\CA examples\Hexagonal CA for snowflake growth.mp4"
        ).set_height(2*config.frame_height/3 - 0.5).move_to(self.THIRD_UP)

        self.add(snowflake_growth)
        credits_tex = MathTex(
            r"\text{Yan Huck at ITP, Frankfurt}",
            font_size=10,
            color=GREY_B,
        ).to_corner(UR, buff=0.1).set_z_index(9999)
        self.play(FadeIn(credits_tex))

        self.wait(30)
        self.next_slide()

        cube = Cube(side_length=1,
                    fill_opacity=0.1,
                    fill_color=WHITE,
                    stroke_width=2).move_to(DOWN*config.frame_height/3)
        first_view_matrix = (
            rotation_matrix(-29.5988 * DEGREES, UP)
            @ rotation_matrix(9.32143 * DEGREES, IN)
            @ rotation_matrix(15.9149 * DEGREES, RIGHT)
        )
        # Define the target orientation
        hexagon_view_matrix = (
            rotation_matrix(35.2643897 * DEGREES, RIGHT)
            @ rotation_matrix(45 * DEGREES, UP)
        )

        # Apply the first orientation
        cube.apply_matrix(first_view_matrix)
        self.play(Create(cube))
        self.next_slide()

        # Compute relative transform: undo C, apply H
        relative = hexagon_view_matrix @ np.linalg.inv(first_view_matrix)
        axis, angle = self.axis_angle_from_matrix(relative)
        # Apply the transition
        self.play(
            Rotate(cube,
                   axis=axis,
                   angle=angle),
            run_time=0.4
        )
        self.next_slide()

        self.play(
            FadeOut(snowflake_growth),
            FadeOut(credits_tex),
            Uncreate(cube), run_time=0.4
        )

    def axis_angle_from_matrix(self, M):
        angle = np.arccos((np.trace(M) - 1) / 2)

        if abs(angle) < 1e-6:
            return np.array([0, 0, 1]), 0   # no rotation

        axis = np.array([
            M[2, 1] - M[1, 2],
            M[0, 2] - M[2, 0],
            M[1, 0] - M[0, 1],
        ]) / (2 * np.sin(angle))

        return axis, angle

    def einstein_hat(self):
        einstein_hat = VideoMobject(
            self.EINSTEIN_HAT_FILE
        ).set_height(2*config.frame_height/3 - 0.5).move_to(self.THIRD_UP)

        einstein_hat_g = Group(einstein_hat, SurroundingRectangle(einstein_hat))

        credits_tex = MathTex(
            r"\text{@henrypdonahue on Github}",
            font_size=10,
            color=GREY_B,
        ).to_corner(UR, buff=0.1).set_z_index(9999)
        self.play(FadeIn(credits_tex))
        self.add(einstein_hat_g)
        self.next_slide()
        self.wait(30)
        self.next_slide()
        self.remove(einstein_hat_g)

        einstein_hat_oscillator = VideoMobject(
            r"src\CA examples\Oscillator einstein hat.mp4"
        ).set_height(2*config.frame_height/3 - 0.5).move_to(self.THIRD_UP)
        einstein_hat_oscillator_g = Group(einstein_hat_oscillator, SurroundingRectangle(einstein_hat_oscillator))
        self.add(einstein_hat_oscillator_g)
        self.next_slide()
        self.wait(10)
        self.next_slide()
        self.remove(einstein_hat_oscillator_g)
        self.play(FadeOut(credits_tex), run_time=0.4)

    def neighborhood_index(self):
        self.X = self.expr.get_part_by_tex("X")
        self.play(
            self.unfocus_letter_animation(self.Zd),
            self.focus_letter_animation(self.X),
            run_time=0.4
        )

        self.show_3x3_ca_vectors()

        self.scopes()

        self.update_example(r"\mathbb{B}", r"\mathbb{Z}^1", r"Scope 3", r"\_")

    def show_3x3_ca_vectors(self):

        # GRID + SMILE + "X ="
        grid, cell_h = self._grid_3x3()
        center = grid.get_cell(0, 0)

        smile = (
            SVGMobject(r"res/smile.svg",
                       stroke_color=WHITE,
                       fill_color=BLACK,
                       fill_opacity=1,
                       ).
            set_height(0.3 * cell_h).
            move_to(center.get_center()).
            set_z_index(1)
        )

        x_y = UP * (config.frame_height / 3)
        X = MathTex("X =").move_to(x_y)

        self.play(Create(grid), GrowFromCenter(smile), Write(X), run_time=0.6)

        # First arrows
        arrows = self._arrows_from_center(grid)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.12), run_time=0.4)

        self.next_slide()

        # Replace "X =" → "X = ( _ , ... , _ )" and move arrows to underscores
        X2 = MathTex(
            r"X = ( \_, \_, \_, \_, \_, \_, \_, \_ )",
            substrings_to_isolate=[r"\_"],
        ).move_to(x_y)

        underscores = X2.get_parts_by_tex(r"\_")

        arrows_y = (X.get_top()[1] + underscores[0].get_top()[1])/2

        targets1 = self._arrow_targets(
            arrows,
            underscores,
            target_y=arrows_y,
            scale=0.6 * X.height / cell_h,
        )

        self.play(
            Transform(X, X2),
            LaggedStart(
                *[
                    Transform(arrows[i], targets1[i])
                    for i in range(len(arrows))
                ],
                lag_ratio=0.05,
            ),
            run_time=0.6,
        )

        self.next_slide()

        # Add one more underscore
        X3 = MathTex(
            r"X = ( \_, \_, \_, \_, \_, \_, \_, \_, \_ )",
            substrings_to_isolate=[r"\_"],
        ).move_to(x_y)

        underscores2 = X3.get_parts_by_tex(r"\_")

        # Targets for 8 arrows → 8 first underscores
        targets2 = self._arrow_targets(
            arrows,
            underscores2[:-1],
            target_y=arrows_y
        )

        # Emoji clone goes to final underscore
        last_pos_x = underscores2[-1].get_center()[0]
        smile_copy = (
            smile.
            copy().
            set_stroke(color=YELLOW).
            set_fill_transparency(0).
            set_height(0.4 * X3.height).
            move_to([last_pos_x, arrows_y, 0])
        )

        self.play(
            Transform(X, X3),
            *[
                Transform(arrows[i], targets2[i])
                for i in range(len(arrows))
            ],
            TransformFromCopy(smile, smile_copy),
            run_time=0.7,
        )

        self.next_slide()
        # Uncreate it all
        self.play(
            Uncreate(X),
            Uncreate(smile),
            Uncreate(smile_copy),
            Uncreate(grid),
            *[Uncreate(arr) for arr in arrows],
            run_time=0.4
        )

    def _grid_3x3(self):
        """3x3 CA grid centered on screen, sized to 1/3 of frame height."""
        grid_h = config.frame_height / 3
        cell_size = grid_h / 3

        grid = CellularAutomatonGrid(
            rows=3, cols=3,
            cell_size=cell_size,
            buff=0.0,
            stroke_color=WHITE,
            stroke_width=1.0,
            off_color=BLACK,
            on_color=YELLOW,
        )
        grid.move_to(ORIGIN)
        return grid, cell_size

    def _arrows_from_center(self, grid):
        """Arrows from center cell to all 8 neighbors."""
        arrows = VGroup()
        center = grid.get_cell(0, 0).get_center()  # (0,0) is center

        for (x, y) in [
            (-1, 1), (0, 1),   (1, 1),
            (-1, 0),           (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]:
            c = grid.get_cell(x, y).get_center()
            arrows.add(
                Arrow(
                    start=center,
                    end=c,
                    buff=0.07*grid.cell_size,
                    stroke_color=YELLOW,
                    stroke_width=2,
                    tip_length=0.08,
                )
            )
        return arrows

    def _arrow_targets(self, arrows, underscores, target_y, scale=1.0):
        """Arrow targets for moving arrows to the underscore positions."""
        targets = VGroup()

        for arrow, u in zip(arrows, underscores):
            targets.add(
                arrow.copy().
                scale(scale).
                move_to([u.get_center()[0], target_y, 0])
            )

        return targets

    def scopes(self):
        # First tape
        g1 = self.tape(1)
        g1.grid.get_cell(0, 0).set_stroke(color=WHITE).set_z_index(0).set_fill(BLACK, 0.0)

        # Create only grid
        self.play(Create(g1.grid), run_time=0.4)
        self.next_slide()

        # animate text + smile
        self.play(
            Create(g1.smile),
            Write(g1.label),
            g1.grid
            .get_cell(0, 0)
            .set_z_index(1)
            .animate
            .set_fill(YELLOW, 0.3)
            .set_stroke(color=YELLOW),
            run_time=0.4,
        )
        self.next_slide()

        tapes = [g1] + [self.tape(i) for i in range(2, 5)]

        self.play(
            *[Create(m)
              for t in tapes[1:]
              for m in t.submobjects],
            run_time=0.4
        )
        self.next_slide()

        self.play(
            *[Uncreate(m)
              for t in tapes
              for m in t.submobjects],
            run_time=0.4
        )

    def tape(self, N):
        cell_size = config.frame_height / 12
        grid = CellularAutomatonGrid(
            rows=1, cols=9,
            cell_size=cell_size
        )

        # Scope _ text
        scope_tex = (
            MathTex(f"\\text{{Scope }} {N}").
            scale(1/2).
            next_to(grid, UP, buff=0.2, aligned_edge=LEFT)
        )

        # White smiley in origin cell
        smile = (
            SVGMobject("res/smile.svg")
            .set_color(WHITE)
            .set_height(cell_size / 3)
            .move_to(grid.get_cell(0, 0).get_center())
            .set_z_index(2)
        )

        # Color yellow and index 1
        start = -1 if N != 1 else 0
        end = start + N
        for i in range(start, end):
            (grid
             .get_cell(i, 0)
             .set_stroke(color=YELLOW)
             .set_fill(YELLOW, 0.3)
             .set_z_index(1))

        # Group everything
        group = VGroup(grid, scope_tex, smile)
        group.grid = grid
        group.label = scope_tex
        group.smile = smile

        # Move
        y = interpolate(config.frame_height/2, -config.frame_height/2, N*1/6)
        group.move_to([0, y, 0])

        return group

    def global_map(self):
        tau = self.expr.get_part_by_tex(r"\tau")
        self.play(
            self.unfocus_letter_animation(self.X),
            self.focus_letter_animation(tau),
            run_time=0.4
        )
        self.next_slide(auto_next=True)

        useable_space = config.frame_height - self.expr.get_height()*1.4

        sigma = self.sigma(useable_space)

        tau, arrow, blob = self.tau(useable_space, sigma)

        # Prepare for next slide
        self.play(
            Uncreate(sigma),
            Uncreate(tau),
            Uncreate(self.expr),
            Uncreate(arrow),
            Uncreate(blob),
            Transform(
                self.example,
                MathTex(
                    r"(\mathbb{B}, \mathbb{Z}^1, Scope 3, \_)"
                )
                .scale(0.8)
                .to_corner(DL, buff=0.3)
            )
        )

    def sigma(self, useable_space):
        # sigma : A^|X| -> A
        sigma = (
            MathTex(
                r"\sigma: A^{|X|}\to A",
            )
            .scale(1.3)
            .move_to(self.TOP + DOWN*useable_space/3)
        )
        self.play(Write(sigma))
        self.next_slide()

        # tapes with arrows
        tape_0 = self.tape(3)
        tape_1 = self.tape(1).next_to(tape_0, direction=DOWN, buff=MED_LARGE_BUFF)
        VGroup(tape_0, tape_1).move_to(self.TOP + DOWN*useable_space*2/3)

        self.play(
            Create(tape_0.grid),
            Create(tape_1.grid),
            run_time=0.4
        )

        arrows = [
            Arrow(
                start=tape_0.grid.get_cell(i, 0).get_bottom(),
                end=tape_1.grid.get_cell(0,  0).get_top(),
                buff=0.07*tape_0.grid.cell_size,
                stroke_color=YELLOW,
                stroke_width=2,
                tip_length=0.08,
            )
            for i in [-1, 0, 1]
        ]

        self.play(
            *[GrowArrow(arr) for arr in arrows]
        )

        self.next_slide()
        self.play(
            *[Uncreate(arr) for arr in arrows],
            Uncreate(tape_0.grid),
            Uncreate(tape_1.grid),
            run_time=0.4)
        return sigma

    def tau(self, useable_space, sigma):
        # tau : A^Z^d -> A^Z^d
        tau = (
            MathTex(
                r"\tau : A^{\mathbb{Z}^d} \to A^{\mathbb{Z}^d",
            )
            .scale(1.3)
            .next_to(sigma, DOWN)
        )
        sigma_copy = sigma.copy()
        VGroup(sigma_copy, tau).move_to(self.TOP + DOWN*useable_space/3)

        self.play(
            sigma.animate.move_to(sigma_copy.get_center()),
            Write(tau),
        )

        self.next_slide()

        # tau : C -> C
        tau_C = (
            MathTex(
                r"\tau : C \to C",
            )
            .scale(1.3)
            .align_to(tau, DOWN)
        )

        self.play(Transform(tau, tau_C))

        blob = (
            SVGMobject(r"res/amorphous blob.svg",
                       stroke_color=WHITE,
                       fill_color=WHITE,
                       fill_opacity=0.1,
                       )
            .set_height(useable_space/3)
            .move_to(self.TOP + DOWN*useable_space*2/3)
        )

        start = blob.get_edge_center(LEFT)
        end = blob.get_edge_center(RIGHT)

        arrow = CurvedArrow(
            start_point=start + RIGHT*0.75,
            end_point=end + LEFT*0.75,
            angle=45 * DEGREES,    # how much it bends
            tip_length=0.15,
            color=YELLOW
        )

        self.play(
            Create(blob),
            run_time=0.4
        )
        self.play(
            Create(arrow),
            run_time=0.4
        )
        self.next_slide()

        return tau, arrow, blob


class Formal_Def_Mai(Formal_Def):
    EINSTEIN_HAT_FILE = r"src\CA examples\Mai einstein hat GoL.mp4"