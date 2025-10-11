from manim import *

def play(slide):
    conway_group = conway(0.5)

    # Animate
    slide.play(FadeIn(conway_group))
    slide.next_slide()
    slide.play(conway_group.animate.scale(0.4).to_corner(UL, buff=0.4))



def conway(target_width_percentage):
    img = ImageMobject("src/Conway picture.jpg")
    img.set_height(target_width_percentage * config.frame_height)

    caption = Paragraph(
        "John Conway",
        "(26 December 1937 - 11 April 2020)",
        alignment="center",
    ).set_width(img.get_width()).next_to(img, DOWN)

    # Group image and caption
    conway_group = Group(img, caption)
    return conway_group
