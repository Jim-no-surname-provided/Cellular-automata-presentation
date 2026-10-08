from manim import * # pyright: ignore[reportWildcardImportFromLibrary]
from manim_slides.slide import Slide
from CellularAutomatonGrid import CellularAutomatonGrid
from ElementaryCA import ElementaryCA


class RulesExamples(Slide):
    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        height = 141
        width = 300
        self.make_rules(height, width, 0.9*config.frame_height/height)

    def make_rules(self, height, width, cell_size):
        # Create both grids using the helpers
        g90 = ElementaryCA(height, width, rule_n=90, cell_size=cell_size, stroke_opacity=0, stroke_width=0.0)
        g110 = ElementaryCA(height, width, rule_n=110, cell_size=cell_size, stroke_opacity=0, stroke_width=0.0)
        g30 = ElementaryCA(height, width, rule_n=30, cell_size=cell_size, stroke_opacity=0, stroke_width=0.0)
        g34 = ElementaryCA(height, width, rule_n=34, cell_size=cell_size, stroke_opacity=0, stroke_width=0.0)
        g34_2 = ElementaryCA(height, width, rule_n=34, cell_size=cell_size, stroke_opacity=0, stroke_width=0.0)

        g90.set_primitive_configuration()
        g110.set_primitive_configuration(width//2-3)
        g30.set_primitive_configuration()
        g34.set_primitive_configuration()
        g34_2.set_alive({(-1, g34_2._top_y, 1, g34_2._top_y)})
        g110.to_edge(RIGHT, buff=3)

        # For low quality, make it smaller
        gens = height - 1 if config.quality != "low_quality" else int(0.2*height)

        print("Running CAs")
        # Run the CA evolution
        for _ in range(gens):
            g90.step()
            g110.step()
            g30.step()
            g34.step()
            g34_2.step()

        g90.render_cells_immediate()
        g110.render_cells_immediate()
        g30.render_cells_immediate()
        g34.render_cells_immediate()
        g34_2.render_cells_immediate()

        # Run Add the first row
        row = VGroup(*[c.copy() for c in g90.get_row(0)]).move_to(ORIGIN)
        self.add(row)
        self.wait(1)
        self.next_slide()
        self.remove(row)

        # Run g90 in 1d
        for r in range(gens):
            row = VGroup(*[c.copy() for c in g90.get_row(r)]).move_to(ORIGIN)
            self.add(row)
            self.wait(0.2)
            self.remove(row)
        self.next_slide()

        def renderECA(g):
            self.play(Create(g),run_time=4)
            self.next_slide()
            self.play(Uncreate(g, run_time=0.1))

        renderECA(g90)

        renderECA(g30)
        renderECA(g34)
        renderECA(g34_2)


        self.wait(0.1)