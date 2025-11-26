from manim import *
from CellularAutomatonGrid import CellularAutomatonGrid


class ElementaryCA(CellularAutomatonGrid):

    def __init__(self, rows, cols, rule_n=None, cell_size=0.1, **kwargs):
        super().__init__(rows, cols, cell_size=cell_size, **kwargs)

        # Default elementary neighborhood (3-cell window from the row above)
        self.neighborhood = (
            (-1, +1),
            (0, +1),
            (1, +1),
        )

        self._rule = None
        if rule_n is not None:
            self.set_rule_number(rule_n)

        self._top_y = rows // 2
        self._bottom_y = -rows // 2
        self._current_y = self._top_y - 1  # second to top

    def set_elementary_rule(self, func):
        """
        func must have signature: func(bits, cell, *params)
        where:
            bits = (L_above, C_above, R_above)
            cell = the cell being updated (with .x, .y, .alive stored)
        """
        self._rule = func
        super().set_rule(self.neighborhood, func)

    def set_primitive_configuration(self, x=0):
        """Place a single live cell at the center or x of the top row."""
        init = {(x, self._top_y)}
        self.set_alive(init)

    def step(self):
        """
        Override of CellularAutomatonGrid.step():
        Keeps the top row frozen, because that is the initial state.
        Only calculates a row each time to avoid unnecesary computations
        """

        if self._current_y <= -self.rows/2:
            return self

        # compute next flags
        for x in range(-self.cols//2, self.cols//2):
            cell = self.get_cell(x, self._current_y)
            bits = self._neighborhood_bits(x, self._current_y)
            cell.alive = bool(self._rule(bits, cell))

        self._current_y -= 1

        return self

    def set_rule_number(self, n):
        """
        Set the Elementary CA rule using a Wolfram rule number (0-255).
        Converts the number into an 8-entry lookup table for (L,C,R).
        """

        if not (0 <= n <= 255):
            raise ValueError("Rule number must be between 0 and 255")

        # Build lookup table: for patterns 111, 110, ..., 000
        self._rule_table = {}
        for pattern in range(8):
            # the output bit is at position `pattern`
            # because Wolfram numbers encode the table with:
            # bit 7 = f(111), bit 6 = f(110), ..., bit 0 = f(000)
            out_bit = (n >> pattern) & 1

            # The pattern bits are: L, C, R
            L = (pattern >> 2) & 1
            C = (pattern >> 1) & 1
            R = (pattern >> 0) & 1

            self._rule_table[(L, C, R)] = out_bit

        # The actual rule function
        def rule(bits, cell, *params):
            pattern = tuple(int(b) for b in bits)
            return bool(self._rule_table[pattern])

        # Install the rule
        self._rule_number = n
        self.set_elementary_rule(rule)

    def get_row(self, r):
        """Return row r (0 -> top)."""
        start = r * self.cols
        end = start + self.cols
        return self.cells[start:end]
