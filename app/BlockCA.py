from manim import *
from CellularAutomatonGrid import CellularAutomatonGrid


class BlockCA(CellularAutomatonGrid):
    def __init__(
        self,
        rows,
        cols,
        cell_size=0.6,
        gap=0.15,             # spacing between cells (buff)
        stroke_color=WHITE,
        division_lines_stroke_color=YELLOW,
        dashed_lines_stroke_color=GREY_B,
        stroke_width=1.0,
        division_lines_stroke_width=2.0,
        dashed_lines_stroke_width=1.0,
        dash_length=0.1,
        **kwargs
    ):
        # Use buff=gap to create space between the cells
        super().__init__(
            rows=rows,
            cols=cols,
            cell_size=cell_size,
            buff=gap,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            **kwargs,
        )

        # Precompute geometry
        step = cell_size + gap
        top = self.cells[0].get_top()[1]+gap/2
        bottom = self.cells[-1].get_bottom()[1]-gap/2
        left = self.cells[0].get_left()[0]-gap/2
        right = self.cells[-1].get_right()[0]+gap/2

        lines = VGroup()

        # Helper to alternate dashed / solid
        def make_line(start, end, index):
            if index % 2 == 0:
                return Line(start,
                            end,
                            stroke_color=division_lines_stroke_color,
                            stroke_width=division_lines_stroke_width)
            else:
                return DashedLine(start,
                                  end,
                                  stroke_color=dashed_lines_stroke_color,
                                  stroke_width=dashed_lines_stroke_width,
                                  dash_length=dash_length)

        # Vertical grid lines — centered in vertical gaps
        for i in range(cols + 1):
            x = left + i * step
            lines.add(make_line([x, bottom, 0], [x, top, 0], i))

        # Horizontal grid lines — centered in horizontal gaps
        for j in range(rows + 1):
            y = top - j * step
            lines.add(make_line([left, y, 0], [right, y, 0], j))

        self.grid_lines = lines
        self.add(lines)
