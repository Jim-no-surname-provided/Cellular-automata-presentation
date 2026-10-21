import numpy as np
from manim import *
from manim_slides.slide import Slide
from PIL import Image

from app.paths import SLIDES_DIR

# --- tunables ---
CELL_SIZE = 0.03
ALIVE_COLOR = WHITE
DEAD_COLOR = BLACK
STEPS = 50
STEP_TIME = 0.15
FADE_STEPS = 10


class Title(Slide):
    def __init__(self, title: Text, subtitle: Paragraph | None = None, *args, **kwargs):
        self.title = title
        self.subtitle = subtitle
        kwargs.setdefault("output_folder", SLIDES_DIR)
        super().__init__(*args, **kwargs)

    def construct(self):
        """Plays the Cellular Automata title animation on the given Slide."""
        # Draw the title
        self.play(Write(self.title))
        self.next_slide()

        # If subtitle, draw it its own slide
        texts = self.title
        if self.subtitle is not None:
            or_txt = Text("or", weight=BOLD, color=GRAY_D, font_size=18)
            self.play(FadeIn(or_txt), Write(self.subtitle))
            self.next_slide(auto_next=True)
            texts = VGroup(self.title, or_txt, self.subtitle)

        # Rasterize the texts using a fixed cell size
        mask_width = max(1, round(texts.width / CELL_SIZE))
        mask_height = max(1, round(texts.height / CELL_SIZE))
        mask = self.rasterize_title_mask(
            texts, mask_height, mask_width, thresh=40, pad_px=0
        )

        # Create the grid with the fixed cell size
        grid = LifeGrid(mask, cell_size=CELL_SIZE)
        grid.move_to(texts.get_center())

        # Fade all three texts into the grid.
        self.play(FadeOut(texts), FadeIn(grid))

        # Run Game of Life
        fade_start = max(0, STEPS - FADE_STEPS)

        for i in range(STEPS):
            grid.step()
            if i >= fade_start:
                # progress from 0 → 1 over the last FADE_STEPS
                progress = (i - fade_start + 1) / FADE_STEPS
                grid.set_opacity(max(0.0, 1.0 - progress))
            self.wait(STEP_TIME)

    def rasterize_title_mask(self, mob, H, W, thresh=128, pad_px=4):
        """Rasterizes the *actual* rendered mob into a HxW binary mask."""
        frame = self.renderer.get_frame()
        cam = self.camera
        pw, ph = cam.pixel_width, cam.pixel_height
        fw, fh = cam.frame_width, cam.frame_height

        left, right = mob.get_left()[0], mob.get_right()[0]
        top, bottom = mob.get_top()[1], mob.get_bottom()[1]

        def x_to_px(x):
            return int((x + fw / 2) * pw / fw)

        def y_to_py(y):
            return int((fh / 2 - y) * ph / fh)

        x0 = max(0, x_to_px(left) - pad_px)
        x1 = min(pw, x_to_px(right) + pad_px)
        y0 = max(0, y_to_py(top) - pad_px)
        y1 = min(ph, y_to_py(bottom) + pad_px)

        crop = frame[y0:y1, x0:x1, :3]
        gray = (
            0.299 * crop[..., 0] + 0.587 * crop[..., 1] + 0.114 * crop[..., 2]
        ).astype("uint8")

        im = Image.fromarray(gray)
        ar = im.width / im.height if im.height else 1.0
        gar = W / H
        if ar >= gar:
            new_w, new_h = W, max(1, round(W / ar))
        else:
            new_h, new_w = H, max(1, round(H * ar))
        im_small = im.resize((new_w, new_h), resample=Image.Resampling.BILINEAR)

        canvas = Image.new("L", (W, H), color=0)
        off_x = (W - new_w) // 2
        off_y = (H - new_h) // 2
        canvas.paste(im_small, (off_x, off_y))

        arr = np.array(canvas)
        return (arr >= thresh).astype(np.uint8)


class LifeGrid(VGroup):
    def __init__(self, init_state, cell_size=CELL_SIZE, **kwargs):
        super().__init__(**kwargs)
        self.h, self.w = init_state.shape
        self.state = init_state.copy()
        for _ in range(self.h * self.w):
            sq = Square(side_length=cell_size).set_stroke(width=0)
            self.add(sq)
        self.arrange_in_grid(rows=self.h, cols=self.w, buff=0)
        self.update_colors()

    def update_colors(self):
        for sq, alive in zip(self.submobjects, self.state.flatten()):
            sq.set_fill(ALIVE_COLOR if alive else DEAD_COLOR, opacity=1)

    def step(self):
        self.state = self.life_step(self.state)
        self.update_colors()

    def life_step(self, state):
        s = state
        padded = np.pad(s, 1)
        nb = (
            padded[:-2, :-2]
            + padded[:-2, 1:-1]
            + padded[:-2, 2:]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
            + padded[2:, :-2]
            + padded[2:, 1:-1]
            + padded[2:, 2:]
        )
        born = (nb == 3) & (s == 0)
        survive = ((nb == 2) | (nb == 3)) & (s == 1)
        return (born | survive).astype(np.uint8)


class TitleSI(Title):
    def __init__(self, *args, **kwargs):
        title_str = "Swarm Intelligence"
        subtitle_str = "HOW TO GET A COOL\nTATOO IN YOUR SHELL\nIF YOU ARE A SEA SNAIL"

        title = Text(title_str, weight=BOLD)
        title.move_to(UP * config.frame_height / 6)

        subtitle = Paragraph(
            subtitle_str, alignment="center", weight=BOLD, color=GRAY_C, font_size=32
        )
        subtitle.move_to(DOWN * config.frame_height / 6)

        super().__init__(title, subtitle, *args, **kwargs)

class TitleCA(Title):
    def __init__(self, *args, **kwargs):
        title = Text("Cellular Automata", weight=BOLD)

        super().__init__(title, None, *args, **kwargs)
