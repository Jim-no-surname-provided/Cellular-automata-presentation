from manim import *

from app.CellularAutomatonGrid import CellularAutomatonGrid


class GameOfLifeGrid(CellularAutomatonGrid):
    """Conway's Game of Life (B3/S23) on a Moore 3x3 neighborhood."""

    # Center-first Moore neighborhood:
    MOORE_9: tuple[tuple[int, int], ...] = (
        (0, 0),
        (-1,  1), (0,  1), (1,  1),
        (-1,  0),          (1,  0),
        (-1, -1), (0, -1), (1, -1),
    )

    def __init__(
        self,
        rows: int,
        cols: int,
        cell_size: float = 0.6,
        buff: float = 0.0,
        stroke_color=WHITE,
        stroke_width: float = 1.0,
        off_color=BLACK,
        on_color=YELLOW_E,
    ):
        super().__init__(
            rows=rows,
            cols=cols,
            cell_size=cell_size,
            buff=buff,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            off_color=off_color,
            on_color=on_color,
        )
        # Install Life rule immediately
        self.set_rule(self.MOORE_9, self._life_rule)

    @staticmethod
    def _life_rule(bits: tuple[bool, ...], *params) -> bool:
        """B3/S23: survive with 2 or 3, birth with exactly 3."""
        current = bits[0]
        n = sum(bits[1:])
        return (current and (n in (2, 3))) or ((not current) and (n == 3))
