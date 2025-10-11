from manim import *
from typing import Callable


class CellularAutomatonGrid(VGroup):
    def __init__(
        self,
        rows: int,
        cols: int,
        cell_size: float = 0.6,
        buff: float = 0.0,                    # tight lattice by default
        stroke_color=WHITE,
        stroke_width: float = 1.0,
        off_color=BLACK,
        on_color=YELLOW,
        neighborhood: tuple[tuple[int, int], ...] | None = None,
        rule: "Callable[[tuple[bool, ...]], bool] | None" = None,
    ):
        """
        neighborhood: tuple of tuples with RELATIVE coordinates to each cell.
          - Order matters: the tuple order is exactly the order passed to the rule.
          - Example (identity / doNothing rule):
              neighborhood = ((0, 0),)
              def rule(bits: tuple[bool, ...]) -> bool:
                  # bits[0] corresponds to (0,0) relative to the current cell
                  return bits[0]
        """
        super().__init__()
        self.rows, self.cols = rows, cols
        self.cell_size = cell_size
        self.buff = buff
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.off_color = off_color
        self.on_color = on_color

        self._neighborhood: tuple[tuple[int, int], ...] | None = neighborhood
        self._rule = rule

        # Build grid
        self.cells = VGroup(*[Square(side_length=cell_size) for _ in range(rows * cols)])
        self.cells.set_stroke(stroke_color, stroke_width).set_fill(off_color, 0.0)
        self.cells.arrange_in_grid(rows=rows, cols=cols, buff=buff, center=True)
        self.add(self.cells)

        # Memory flags (per cell)
        for cell in self.cells:
            cell.alive = False

    # --- indexing ---
    def idx(self, r: int, c: int) -> int:
        return r * self.cols + c

    # --- state accessors ---
    def is_alive(self, r: int, c: int) -> bool:
        return bool(getattr(self.cells[self.idx(r, c)], "alive", False))

    def set_alive(self, *args, **kwargs):
        """
        Flexible setter:
          - set_alive(r, c, alive=True)       -> set a single cell
          - set_alive({(r,c), ...})           -> set many via a set of coords
        """
        if len(args) == 1 and isinstance(args[0], (set, frozenset)):
            alive_coords = args[0]
            for r in range(self.rows):
                for c in range(self.cols):
                    self.cells[self.idx(r, c)].alive = ((r, c) in alive_coords)
            return self

        if len(args) >= 2:
            r, c = int(args[0]), int(args[1])
            alive = kwargs.get("alive", args[2] if len(args) >= 3 else True)
            self.cells[self.idx(r, c)].alive = bool(alive)
            return self

        raise TypeError("set_alive expects either (r, c, alive=True) or a set of (r,c) tuples.")

    # --- rendering ---
    def render_cells(self):
        """Return animations that paint visuals to match each cell's .alive flag."""
        anims = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[self.idx(r, c)]
                if getattr(cell, "alive", False):
                    anims.append(cell.animate.set_fill(self.on_color, 1.0)
                                 .set_stroke(self.stroke_color, self.stroke_width))
                else:
                    anims.append(cell.animate.set_fill(self.off_color, 0.0)
                                 .set_stroke(self.stroke_color, self.stroke_width))
        return anims

    def render_cells_immediate(self):
        """Apply visuals immediately (no animation)."""
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[self.idx(r, c)]
                if getattr(cell, "alive", False):
                    cell.set_fill(self.on_color, 1.0).set_stroke(self.stroke_color, self.stroke_width)
                else:
                    cell.set_fill(self.off_color, 0.0).set_stroke(self.stroke_color, self.stroke_width)
        return self

    # --- rules ---
    def set_rule(
        self,
        neighborhood: tuple[tuple[int, int], ...],
        rule: "Callable[[tuple[bool, ...]], bool]",
    ):
        """
        Set the local update rule.

        neighborhood: tuple of relative (dr, dc) offsets. Order is preserved.
        rule: function that receives a tuple[bool,...] with the neighborhood
              states in the SAME ORDER and returns True (alive) / False (dead).
        """
        self._neighborhood = tuple(tuple(p) for p in neighborhood)
        self._rule = rule
        return self

    def _alive_in_bounds(self, r: int, c: int) -> bool:
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return False
        return bool(getattr(self.cells[self.idx(r, c)], "alive", False))

    def _neighborhood_bits(self, r: int, c: int) -> tuple[bool, ...]:
        if not self._neighborhood:
            return tuple()
        bits: list[bool] = []
        for dr, dc in self._neighborhood:
            bits.append(self._alive_in_bounds(r + dr, c + dc))
        return tuple(bits)

    def step(self):
        """
        Apply the stored rule once to ALL cells, mutating only the per-cell flags.
        Visuals are NOT updated here; call render_cells()/render_cells_immediate() after.
        If no rule is set, this is a no-op.
        """
        if not (self._neighborhood and self._rule):
            return self

        new_flags = [[False] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                bits = self._neighborhood_bits(r, c)
                new_flags[r][c] = bool(self._rule(bits))

        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[self.idx(r, c)].alive = new_flags[r][c]

        return self

    def set_life_rule(self):
        """
        Convenience: Conway's Game of Life (B3/S23) with the Moore neighborhood.
        Neighborhood order (tuples are RELATIVE to each cell, order defines rule input):
            (0, 0),          # center (the cell itself)
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),         ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)

        The rule receives a tuple[bool,...] in that order:
          bits[0] = current cell alive?
          sum(bits[1:]) = number of alive neighbors
        """
        neighborhood = (
            (0, 0),
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        )

        def life(bits: tuple[bool, ...]) -> bool:
            current = bits[0]
            n = sum(bits[1:])
            return (current and (n in (2, 3))) or ((not current) and (n == 3))

        return self.set_rule(neighborhood, life)
