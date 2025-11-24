import random
from manim import *
from manim_slides import Slide
from video_mobject_opencv import VideoMobject
from BlockCA import BlockCA


class Formal_Def(Slide):

    THIRD_UP = UP*config.frame_height*(1/6)
    THIRD_DOWN = DOWN*config.frame_height*(1/6)

    FOCUS_LETTER_SCALE = 1.4

    def construct(self):
        self.intro()

        self.state_alphabet()

        self.cell_array()
        self.next_slide()

        self.neighborhood_index()
        self.next_slide()

        self.global_map()
        self.next_slide()

        self.play(FadeOut(Group(*self.mobjects)))

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
        self.example.match_height(self.expr).scale(1/self.FOCUS_LETTER_SCALE).to_corner(DL, buff=0.6)
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
        new = MathTex(tex).match_height(self.example)
        new.to_corner(DL, buff=0.6)
        self.play(Transform(self.example, new), run_time=0.4)
        self.remove(self.example)
        self.example = new   # keep reference up to date

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
            r"src\CA examples\Growing Neural Cellular Automata.mp4",
            loop=True
        ).scale(0.5)

        neural_ca_g = Group(neural_ca, SurroundingRectangle(neural_ca))

        self.add(neural_ca_g)
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
                tip_length=0.05,
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
        grid.render_cells_immediate()

        # Position it at THIRD_UP
        grid.move_to(self.THIRD_UP*0.5)

        self.play(
            Create(grid),
            run_time=0.4)
        self.wait(1e-9)
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
        Zd = self.expr.get_part_by_tex(r"\mathbb{Z}^d")
        self.play(
            self.focus_letter_animation(Zd),
            run_time=0.4
        )

        self.next_slide()
        self.update_example(r"\mathbb{B}", r"\mathbb{Z}^1", r"\_", r"\_")

    def neighborhood_index(self):
        self.update_example(r"\mathbb{B}", r"\mathbb{Z}^1", r"Scope 3", r"\_")

    def global_map(self):
        self.update_example(r"\mathbb{B}", r"\mathbb{Z}^1", r"Scope 3", r"\tau")
