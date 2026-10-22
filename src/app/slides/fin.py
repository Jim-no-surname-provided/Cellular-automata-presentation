from io import BytesIO

import numpy as np
from cairosvg import svg2png
from manim import (
    DOWN,
    RIGHT,
    FadeIn,
    Group,
    ImageMobject,
    Text,
    config,
)
from manim_slides.slide import Slide
from PIL import Image

from app.paths import RES_DIR, SLIDES_DIR


def svg_image(path, height=0.5):
    # Render at twice the displayed pixel height
    pixel_height = max(
        1,
        int(np.ceil(
            3 * height * config.pixel_height / config.frame_height
        )),
    )
    png_bytes = svg2png(
        url=str(path),
        output_height=pixel_height,
    )

    # Remove transparent padding before setting the displayed height
    with Image.open(BytesIO(png_bytes)) as image:
        rgba = image.convert("RGBA")
        bounds = rgba.getchannel("A").getbbox()
        if bounds is not None:
            rgba = rgba.crop(bounds)
        pixels = np.array(rgba)

    return ImageMobject(pixels).set_height(height)


class Fin(Slide):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("output_folder", SLIDES_DIR)
        super().__init__(*args, **kwargs)

    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        # Make the contact rows with their icons
        def contact_row(icon_file):
            icon = svg_image(
                RES_DIR / "icons" / icon_file,
                height=0.5,
            )
            username = Text("JimberryDev", font_size=32)
            return Group(icon, username).arrange(RIGHT, buff=0.3)

        contacts = Group(
            contact_row("DC.svg"),
            contact_row("YT.svg"),
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.4)

        # Credit the software
        manim_logo = svg_image(
            RES_DIR / "icons" / "manim.svg",
            height=0.8,
        )
        software = Group(
            manim_logo,
            Text("Made with Manim + Manim Slides", font_size=24),
        ).arrange(RIGHT, buff=0)

        # Arrange the contacts and software credit in the middle
        content = Group(
            contacts,
            software,
        ).arrange(DOWN, buff=1)

        # Point to the full credits and references on Moodle
        footer = Text(
            "References, media credits, and source code on Moodle",
            font_size=18,
        ).to_edge(DOWN, buff=0.5)

        # Show the closing slide and leave it visible
        self.next_slide(auto_next=True)
        self.play(FadeIn(content), FadeIn(footer))
