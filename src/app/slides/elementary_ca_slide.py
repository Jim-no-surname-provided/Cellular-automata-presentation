from manim import *
from manim_slides.slide import Slide

from app.paths import SLIDES_DIR


class Elementary_CA_Slide(Slide):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("output_folder", SLIDES_DIR)
        super().__init__(*args, **kwargs)


    FIRST_THIRD = UP*config.frame_height*(1/6)
    SECOND_THIRD = DOWN*config.frame_height*(1/6)
    TOP = (config.frame_height/2)*UP
    LEFT_EDGE = (config.frame_width/2)*LEFT

    def construct(self):
        self.elementary_def()

        table = self.truth_table()
        self.next_slide()
        self.animate_sigma_randomization(table.S_col, 25)
        self.next_slide()
        self.transform_to_wolfram_number(table)
        self.play(
            *[FadeOut(mob) for mob in self.mobjects]
        )

    def truth_table(self):
        # Columns
        N_col = self.make_col([f"{i:03b}" for i in range(8)])
        S_col = self.make_col(["0"] * 8)
        S_90_col = self.make_col("01011010")
        S_110_col = self.make_col("01110110")

        # Titles
        N_title = MathTex("N", font_size=40)
        S_title = MathTex(r"\sigma", font_size=40)
        S_90_title = MathTex(r"\sigma_{90}", font_size=40)
        S_110_title = MathTex(r"\sigma_{110}", font_size=40)

        # Column groups with titles
        N_full = VGroup(N_title, N_col).arrange(DOWN, buff=0.25)
        S_full = VGroup(S_title, S_col).arrange(DOWN, buff=0.25)
        S_90_full = VGroup(S_90_title, S_90_col).arrange(DOWN, buff=0.25)
        S_110_full = VGroup(S_110_title, S_110_col).arrange(DOWN, buff=0.25)

        # Combine columns
        table = VGroup(N_full, S_full, S_90_full, S_110_full).arrange(RIGHT, buff=0.5)
        table.N = N_full
        table.S = S_full
        table.S_col = S_col
        table.S_90 = S_90_full
        table.S_110 = S_110_full

        # Align cols at the bottom
        S_full.align_to(N_full, DOWN)
        S_90_full.align_to(N_full, DOWN)
        S_110_full.align_to(N_full, DOWN)

        #  Set size and position
        table.set_height(0.5 * self.available_height)
        table_y = (self.TOP + DOWN*self.available_height/2)[1]
        table_x = (self.LEFT_EDGE + RIGHT*config.frame_width/4)[0]
        table.move_to([table_x, table_y, 0])

        # Draw vertical and header lines
        left = table.get_left()[0] - 0.1
        # right = S_full.get_right()[0] + 0.1
        top = table.get_top()[1] + 0.1
        bottom = table.get_bottom()[1] - 0.1

        # Mid points between cols
        vertical_lines = []
        for i in range(1, len(table)):
            x = (table[i-1].get_right()[0] + table[i].get_left()[0])/2
            vertical_lines.append(Line(
                [x, top, 0],
                [x, bottom, 0],
                stroke_color=WHITE,
                stroke_width=2
            ))

        # Right below titles
        header_y = N_title.get_bottom()[1] - 0.1
        header_lines = [Line(
            [left,  header_y, 0],
            [table[i].get_right()[0] + 0.1, header_y, 0],
            stroke_color=WHITE,
            stroke_width=2
        ) for i in range(1, len(table))]

        table.add(vertical_lines)
        table.add(header_lines)
        table.vertical_lines = vertical_lines
        table.header_lines = header_lines

        self.play(Create(vertical_lines[0]), Create(header_lines[0]), run_time=1)
        self.play(
            Write(S_full),
            Write(N_full),
            run_time=1)

        return table

    def elementary_def(self):
        self.expr = (
            MathTex(
                r"(\mathbb{B}, \mathbb{Z}^1, Scope 3, \_)"
            )
            .scale(0.8)
            .to_corner(DL, buff=0.3)
        )
        self.add(self.expr)

        self.available_height = config.frame_height - self.expr.get_height()*1.4

    def animate_sigma_randomization(self, S_col, n):
        import random
        for _ in range(n):   # jitter σ a bit
            new_col = self.make_col([
                str(random.randint(0, 1))
                for _ in range(8)
            ])
            new_col.match_height(S_col)
            new_col.move_to(S_col)

            self.play(Transform(S_col, new_col), run_time=0.3)
            self.wait(0.1)

        # set to abcdefgh
        new_col = self.make_col("abcdefgh")
        new_col.match_height(S_col)
        new_col.move_to(S_col)
        self.play(Transform(S_col, new_col), run_time=0.7)

    def make_col(self, values):
        return VGroup(*[
            MathTex(v, font_size=32)
            for v in values
        ]).arrange(DOWN, buff=0.15)

    def arcCenter(self, A, B, theta):
        """
        A, B: np.array([x, y, 0]) style points.
        theta: central angle in radians (positive = CCW).
        Returns: center C (np.array)
        """
        A = np.array(A)
        B = np.array(B)

        # chord vector and length
        v = A - B
        d = np.linalg.norm(v)

        # radius
        R = d / (2 * np.sin(theta / 2))

        # midpoint of chord
        M = (A + B) / 2

        # perpendicular unit vector (CCW)
        vx, vy, _ = v
        n = np.array([-vy, vx, 0.0])
        n /= np.linalg.norm(n)

        # distance from midpoint to center
        h = np.sqrt(R**2 - (d/2)**2)

        # final center
        C = M + h * n

        return C

    def transform_to_wolfram_number(self, table):
        scheme_y = (self.TOP + DOWN*self.available_height/3)[1]
        scheme_x = (self.LEFT_EDGE + RIGHT*config.frame_width*2/3)[0]

        scheme_tex = (
            MathTex(
                "h", "g", "f", "e", "d", "c", "b", "a",
                r" \rightarrow \text{Wolfram Scheme}",
                arg_separator="",
                font_size=32,
            )
            .move_to([scheme_x, scheme_y, 0])
        )
        scheme_90 = (
            MathTex(r"0101 1010 \rightarrow 90", font_size=32)
            .next_to(scheme_tex, DOWN)
            .align_to(scheme_tex, LEFT)
        )
        scheme_110 = (
            MathTex(r"0110 1110 \rightarrow 110", font_size=32)
            .next_to(scheme_90, DOWN)
            .align_to(scheme_tex, LEFT)
        )

        angle = -60*DEGREES
        anims = []
        S_copies = []
        for i in range(len(table.S_col)):
            l = table.S_col[-i-1].copy()
            pivot = Dot(l.get_center(), radius=0.001, color=BLACK)
            pivot.set_opacity(0)  # invisible
            self.add(pivot)

            S_copies.append(l)
            anims.append(
                Rotate(
                    pivot,
                    angle,
                    about_point=self
                    .arcCenter(
                        pivot.get_center(),
                        scheme_tex[i].get_center(),
                        angle
                    )
                )
            )
            anims.append(MaintainPositionRelativeTo(l, pivot))

        self.play(
            *anims
        )
        self.next_slide()
        self.play(
            Write(scheme_tex[-1]),
            *[
                Transform(l, scheme_tex[i])
                for i, l in enumerate(S_copies)
            ],
            run_time=0.6
        )
        self.add(scheme_tex[:-1])
        self.remove(*S_copies)

        self.next_slide()
        self.play(
            Write(scheme_90),
            Write(table.S_90),
            Write(table.vertical_lines[1]),
            Transform(table.header_lines[0], table.header_lines[1]),
            run_time=0.4
        )
        self.next_slide()

        self.play(
            Write(scheme_110),
            Write(table.S_110),
            Write(table.vertical_lines[2]),
            Transform(table.header_lines[0], table.header_lines[2]),
            run_time=0.4
        )
        self.next_slide(auto_next=True)
