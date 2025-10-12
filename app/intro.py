from manim import *
from manim_slides import Slide
from CellularAutomatonGrid import CellularAutomatonGrid


def play(slide: Slide):

    # Form 5x5 grid in the middle
    grid = CellularAutomatonGrid(7, 7)
    grid.set_life_rule()
    slide.play(LaggedStart(*[Create(c) for c in grid.cells], lag_ratio=0.05))
    slide.next_slide()

    # Make some of them be alive (middle cell should be alive)
    grid.set_alive({(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, -2)})  # configuration
    slide.play(*grid.render_cells(), run_time=0.4)
    slide.next_slide()

    # Update (middle cell should die)
    grid.step()
    slide.play(*grid.render_cells(), run_time=0.4)
    slide.next_slide()

    # Move to the left and
    # write "Rule as a title on the right"
    
    slide.next_slide()

    # Add the rule "Dead cells with 3 cells become alive" and
    slide.next_slide()

    # Count neighbors around middle cell
    slide.next_slide()

    # Update (middle cell should come to life)
    slide.next_slide()

    # Add the rule "Alive cells with 2 or 3 cells stay alive" and
    # Count neighbors around middle cell
    slide.next_slide()

    # Update (middle cell should survive)
    slide.next_slide()

    # Count neighbors around middle cell
    slide.next_slide()

    # Update (middle cell should die)
    slide.next_slide()

    # Let run
    slide.next_slide()
    # Fade out
    slide.next_slide()

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
