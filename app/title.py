# part_title.py
from manim import *
import numpy as np
from PIL import Image

# --- tunables ---
TITLE = "Cellular Automata"
GRID_H, GRID_W = 105, 300
ALIVE_COLOR = WHITE
DEAD_COLOR = BLACK
STEPS = 50
STEP_TIME = 0.15
FADE_STEPS = 10


def life_step(state):
    s = state
    padded = np.pad(s, 1)
    nb = (
        padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
        padded[1:-1, :-2] + padded[1:-1, 2:] +
        padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
    )
    born = (nb == 3) & (s == 0)
    survive = ((nb == 2) | (nb == 3)) & (s == 1)
    return (born | survive).astype(np.uint8)


class LifeGrid(VGroup):
    def __init__(self, init_state, **kwargs):
        super().__init__(**kwargs)
        self.h, self.w = init_state.shape
        self.state = init_state.copy()
        for _ in range(self.h * self.w):
            sq = Square(side_length=1).set_stroke(width=0)
            self.add(sq)
        self.arrange_in_grid(rows=self.h, cols=self.w, buff=0)
        self.update_colors()

    def update_colors(self):
        for sq, alive in zip(self.submobjects, self.state.flatten()):
            sq.set_fill(ALIVE_COLOR if alive else DEAD_COLOR, opacity=1)

    def step(self):
        self.state = life_step(self.state)
        self.update_colors()


def rasterize_title_mask(scene, mob, H, W, thresh=128, pad_px=4):
    """Rasterizes the *actual* rendered mob into a HxW binary mask."""
    frame = scene.renderer.get_frame()
    cam = scene.camera
    pw, ph = cam.pixel_width, cam.pixel_height
    fw, fh = cam.frame_width, cam.frame_height

    left, right = mob.get_left()[0], mob.get_right()[0]
    top, bottom = mob.get_top()[1], mob.get_bottom()[1]

    def x_to_px(x): return int((x + fw/2) * pw / fw)
    def y_to_py(y): return int((fh/2 - y) * ph / fh)

    x0 = max(0, x_to_px(left) - pad_px)
    x1 = min(pw, x_to_px(right) + pad_px)
    y0 = max(0, y_to_py(top) - pad_px)
    y1 = min(ph, y_to_py(bottom) + pad_px)

    crop = frame[y0:y1, x0:x1, :3]
    gray = (0.299*crop[..., 0] + 0.587*crop[..., 1] + 0.114*crop[..., 2]).astype("uint8")

    im = Image.fromarray(gray)
    ar = im.width / im.height if im.height else 1.0
    gar = W / H
    if ar >= gar:
        new_w, new_h = W, max(1, round(W / ar))
    else:
        new_h, new_w = H, max(1, round(H * ar))
    im_small = im.resize((new_w, new_h), resample=Image.BILINEAR)

    canvas = Image.new("L", (W, H), color=0)
    off_x = (W - new_w) // 2
    off_y = (H - new_h) // 2
    canvas.paste(im_small, (off_x, off_y))

    arr = np.array(canvas)
    return (arr >= thresh).astype(np.uint8)


def play_cellular_automata_title(slide):
    """Plays the Cellular Automata title animation on the given Slide."""
    # Step 1: Draw the title
    title = Text(TITLE, weight=BOLD)
    slide.play(Write(title))
    slide.wait(0.5)

    # Step 2: Rasterize title into a binary mask
    mask = rasterize_title_mask(slide, title, GRID_H, GRID_W)

    # Step 3: Create Life grid from mask
    grid = LifeGrid(mask)
    grid.set_width(title.width)
    grid.move_to(title.get_center())

    # Step 4: Fade from title to pixel grid
    slide.next_slide()
    slide.play(FadeOut(title), FadeIn(grid))

    # Step 5: Run Game of Life
    # Run first steps normally
    fade_start = max(0, STEPS - FADE_STEPS)

    for i in range(STEPS):
        grid.step()
        if i >= fade_start:
            # progress from 0 → 1 over the last FADE_STEPS
            progress = (i - fade_start + 1) / FADE_STEPS
            grid.set_opacity(max(0.0, 1.0 - progress))
        slide.wait(STEP_TIME)
