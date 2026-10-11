from collections.abc import Callable

import numpy as np
from manim import *

# pyright: reportAttributeAccessIssue=false


class CellularAutomatonGrid(VGroup):
    def __init__(
        self,
        rows: int,
        cols: int,
        cell_size: float = 0.6,
        buff: float = 0.0,  # tight lattice by default
        stroke_color=WHITE,
        stroke_opacity=1,
        stroke_width: float = 1.0,
        off_color=BLACK,
        on_color=WHITE,
        neighborhood: tuple[tuple[int, int], ...] | None = None,
        rule: Callable[[tuple[bool, ...], VMobject], bool] | None = None,
    ):
        """
        neighborhood: tuple of tuples with RELATIVE coordinates (dx, dy) to each cell.
          - Coordinate convention: x right is positive, y up is positive, (0,0) is the center cell.
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
        self._rule: Callable[[tuple[bool, ...], VMobject], bool] | None = rule

        # Build grid (stored flat, row-major, top-to-bottom)
        self.cells = VGroup(
            *[Square(side_length=cell_size) for _ in range(rows * cols)]
        )
        self.cells.set_stroke(
            stroke_color, stroke_width, opacity=stroke_opacity
        ).set_fill(off_color, 0.0)
        self.cells.arrange_in_grid(rows=rows, cols=cols, buff=buff, center=True)
        self.add(self.cells)

        # Memory flags (per cell)
        for i, cell in enumerate(self.cells):
            x, y = self.index_to_xy(i)
            cell.x = x
            cell.y = y
            cell.alive = False

    # --- coordinate conversion (centered x,y) ---
    def xy_to_index(self, x: int, y: int) -> int:
        """Convert centered (x,y) to list index. x right+, y up+, (0,0) at center."""
        row = (self.rows // 2) - y
        col = (self.cols // 2) + x
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return -1  # out of bounds
        return row * self.cols + col

    def index_to_xy(self, index: int) -> tuple[int, int]:
        """Inverse of xy_to_index: return centered (x,y)."""
        row = index // self.cols
        col = index % self.cols
        y = (self.rows // 2) - row
        x = col - (self.cols // 2)
        return (x, y)

    # -- normal getters --
    def get_cell(self, x, y):
        return self.cells[self.xy_to_index(x, y)]

    # --- state accessors ---
    def is_alive(self, x: int, y: int) -> bool:
        idx = self.xy_to_index(x, y)
        if idx == -1:
            return False
        return bool(getattr(self.cells[idx], "alive", False))

    def set_alive(self, *args, **kwargs):
        """
        Flexible setter:
          - set_alive(x, y, alive=True)       -> set a single cell
          - set_alive({(x,y), ...})           -> set many via a set of coords
        """
        if len(args) == 1 and isinstance(args[0], (set, frozenset)):
            alive_coords = args[0]
            for i in range(self.rows * self.cols):
                x, y = self.index_to_xy(i)
                self.cells[i].alive = (x, y) in alive_coords
            return self

        if len(args) >= 2:
            x, y = int(args[0]), int(args[1])
            alive = kwargs.get("alive", args[2] if len(args) >= 3 else True)
            idx = self.xy_to_index(x, y)
            if idx != -1:
                self.cells[idx].alive = bool(alive)
            return self

        raise TypeError(
            "set_alive expects either (x, y, alive=True) or a set of (x,y) tuples."
        )

    # --- rendering ---
    def render_cells(self):
        """Return animations that paint visuals to match each cell's .alive flag."""
        anims = []
        for i in range(self.rows * self.cols):
            cell = self.cells[i]
            if getattr(cell, "alive", False):
                anims.append(
                    cell.animate.set_fill(self.on_color, 1.0).set_stroke(
                        self.stroke_color, self.stroke_width
                    )
                )
            else:
                anims.append(
                    cell.animate.set_fill(self.off_color, 0.0).set_stroke(
                        self.stroke_color, self.stroke_width
                    )
                )
        return anims

    def update_cell_colors(self):
        """Apply visuals immediately (no animation)."""
        for i in range(self.rows * self.cols):
            cell = self.cells[i]
            if getattr(cell, "alive", False):
                cell.set_fill(self.on_color, 1.0).set_stroke(
                    self.stroke_color, self.stroke_width
                )
            else:
                cell.set_fill(self.off_color, 0.0).set_stroke(
                    self.stroke_color, self.stroke_width
                )
        return self

    def to_image(self) -> ImageMobject:
        pixels = np.fromiter(
            (255 if cell.alive else 0 for cell in self.cells),
            dtype=np.uint8,
            count=self.rows * self.cols,
        ).reshape(self.rows, self.cols)

        image = ImageMobject(np.repeat(pixels[:, :, None], 3, axis=2))
        image.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])

        image.set_width(self.width)
        image.move_to(self.get_center())
        return image

    # --- rules ---
    def set_rule(
        self,
        neighborhood: tuple[tuple[int, int], ...],
        rule: Callable[[tuple[bool, ...], VMobject], bool],
    ):
        """
        Set the local update rule.

        neighborhood: tuple of relative (dx, dy) offsets. Order is preserved.
        rule: function that receives a tuple[bool,...] with the neighborhood
              states in the SAME ORDER and returns True (alive) / False (dead).
        """
        self._neighborhood = tuple(tuple(p) for p in neighborhood)
        self._rule = rule
        return self

    def _alive_in_bounds(self, x: int, y: int) -> bool:
        idx = self.xy_to_index(x, y)
        if idx == -1:
            return False
        return bool(getattr(self.cells[idx], "alive", False))

    def _neighborhood_bits(self, x: int, y: int) -> tuple[bool, ...]:
        if not self._neighborhood:
            return ()
        bits: list[bool] = []
        for dx, dy in self._neighborhood:
            bits.append(self._alive_in_bounds(x + dx, y + dy))
        return tuple(bits)

    # --- neighbors APIs ---
    def neighbor_coords_of(
        self,
        x: int,
        y: int,
        *,
        include_center: bool = False,
        in_bounds_only: bool = True,
    ) -> list[tuple[int, int]]:
        """
        Return neighbor coordinates translated from (x, y) using the current neighborhood.

        include_center: if False, (0,0) offset is excluded (common for CA rules).
        in_bounds_only: if True, clips to grid; if False, returns off-grid coords too.
        """
        if not self._neighborhood:
            return []

        coords: list[tuple[int, int]] = []
        for dx, dy in self._neighborhood:
            if not include_center and dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if in_bounds_only:
                if self.xy_to_index(nx, ny) >= 0:
                    coords.append((nx, ny))
            else:
                coords.append((nx, ny))
        return coords

    def neighbors_of(
        self,
        x: int,
        y: int,
        *,
        include_center: bool = False,
    ) -> list[Mobject]:
        """
        Return the *cell objects* for neighbors of (x, y), filtered to in-bounds cells.
        By default excludes the center (0,0) offset.
        """
        coords = self.neighbor_coords_of(
            x, y, include_center=include_center, in_bounds_only=True
        )
        return [self.cells[self.xy_to_index(nx, ny)] for (nx, ny) in coords]

    def step(self):
        """
        Apply the stored rule once to ALL cells, mutating only the per-cell flags.
        Visuals are NOT updated here; call render_cells()/render_cells_immediate() after.
        If no rule is set, this is a no-op.
        """
        if not (self._neighborhood and self._rule):
            return self

        total = self.rows * self.cols
        new_flags = [False] * total

        # compute next flags
        for i in range(total):
            x, y = self.index_to_xy(i)
            bits = self._neighborhood_bits(x, y)
            new_flags[i] = bool(self._rule(bits, self.get_cell(x, y)))

        # commit
        for i in range(total):
            self.cells[i].alive = new_flags[i]

        return self
