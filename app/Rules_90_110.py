from manim import *
from manim_slides import Slide
from CellularAutomatonGrid import CellularAutomatonGrid
from ElementaryCA import ElementaryCA


class Rules_90_110(Slide):
    def construct(self):
        height = 141
        width = 300
        self.make_rules(height, width, 0.9*config.frame_height/height)

    def make_rules(self, height, width, cell_size):
        # Create both grids using the helpers
        g90 = ElementaryCA(height, width, rule_n=90, cell_size=cell_size, stroke_opacity=0, stroke_width=0.0)
        g110 = ElementaryCA(height, width, rule_n=110, cell_size=cell_size, stroke_opacity=0, stroke_width=0.0)

        g90.set_primitive_configuration()
        g110.set_primitive_configuration(width//2-3)
        g110.to_edge(RIGHT, buff=3)

        gens = height - 1 if config.quality != "low_quality" else int(0.2*height)

        print("Running CAs")
        # Run the CA evolution
        for _ in range(gens):
            g90.step()
            g110.step()

        g90.render_cells_immediate()
        g110.render_cells_immediate()

        # Run Add the first row
        row = VGroup(*[c.copy() for c in g90.get_row(0)]).move_to(ORIGIN)
        self.add(row)
        self.wait(0.2)
        self.next_slide()
        self.remove(row)

        # Run g90 in 1d
        for r in range(gens):
            row = VGroup(*[c.copy() for c in g90.get_row(r)]).move_to(ORIGIN)
            self.add(row)
            self.wait(0.2)
            self.remove(row)
        self.next_slide()

        # Render g90
        self.play(
            Create(g90),
            run_time=4
        )
        self.wait(0.1)
        self.next_slide()

        # Render 110
        self.play(Uncreate(g90))
        self.wait(1)
        self.play(
            Create(g110),
            run_time=4
        )
        self.wait(0.1)
        self.next_slide()

        self.play(FadeOut(g110))
        self.wait(0.1)
