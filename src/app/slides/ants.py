from math import sqrt

from manim import (
    DL,
    DOWN,
    DR,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    FadeIn,
    FadeOut,
    RoundedRectangle,
    Text,
    VGroup,
    Write,
    config,
)
from manim_slides.slide import Slide

from app.data import VideoMobject
from app.paths import ANTS_DIR, SLIDES_DIR
from app.slides.intro import MEDIA_HEIGHT


class Ants(Slide):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("output_folder", SLIDES_DIR)
        super().__init__(*args, **kwargs)

    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        # Single individual comparison
        single_ant = VideoMobject(
            str(ANTS_DIR / "single_ant.mov"),
            start_time=5,
            end_time=30,
        ).set_height(MEDIA_HEIGHT)
        single_human = VideoMobject(
            str(ANTS_DIR / "single_human.mov"),
        ).set_height(MEDIA_HEIGHT)

        # Leave equal gaps around and between the videos
        gap = (config.frame_width - 2 * single_ant.width) / 3
        offset = (single_ant.width + gap) / 2
        single_ant.move_to(LEFT * offset)
        single_human.move_to(RIGHT * offset)

        # Play them
        self.play(FadeIn(single_ant), FadeIn(single_human))
        self.wait(
            max(
                single_human.remaining_time(),
                single_ant.remaining_time(),
            )
        )
        self.next_slide()

        # Multiple individuals comparison
        multiple_ants = VideoMobject(
            str(ANTS_DIR / "multiple_ants.mov"),
        ).set_height(MEDIA_HEIGHT)
        multiple_humans = VideoMobject(
            str(ANTS_DIR / "multiple_humans.mov"),
        ).set_height(MEDIA_HEIGHT)

        # Leave equal gaps around and between the videos
        gap = (config.frame_width - 2 * multiple_ants.width) / 3
        offset = (multiple_ants.width + gap) / 2
        multiple_ants.move_to(LEFT * offset)
        multiple_humans.move_to(RIGHT * offset)

        # Play them
        self.remove(single_ant, single_human)
        self.add(multiple_ants, multiple_humans)
        self.wait(
            max(
                multiple_humans.remaining_time(),
                multiple_ants.remaining_time(),
            )
        )
        self.next_slide()
        self.play(FadeOut(multiple_ants), FadeOut(multiple_humans))
        
        simulated_ants = VideoMobject(
            str(ANTS_DIR / "simulated_ants.mov"),
        ).set_height(MEDIA_HEIGHT).move_to(LEFT * config.frame_width / 4)
        self.play(FadeIn(simulated_ants))

        # Show the individual rules beside the simulation
        diagram = self.make_state_diagram()
        diagram.scale(0.85)
        diagram.move_to(RIGHT * config.frame_width / 4)
        self.play(Write(diagram, run_time=0.5))

        # Finish playing the simulation with the rules visible
        self.wait(simulated_ants.remaining_time())
        self.next_slide()

    def make_state_diagram(self):
        # Make each state with its description inside the rectangle
        def make_state(title, subtitle):
            labels = VGroup(
                Text(title, font_size=22),
                Text(subtitle, font_size=16),
            ).arrange(DOWN, buff=0.12)

            box = RoundedRectangle(
                width=2.6,
                height=1.1,
                corner_radius=0.18,
                stroke_width=2,
            )

            return VGroup(box, labels)

        informed = make_state("Informed", "Pull towards goal")
        uninformed = make_state("Uninformed", "Follow the vibe")
        detached = make_state("Detached", "Roam around")

        # Make an equilateral triangle between the inner corners and top midpoint
        side = 1.4
        triangle_height = sqrt(3) * side / 2

        informed.move_to(
            [-side / 2, triangle_height / 3, 0],
            aligned_edge=DR,
        )
        uninformed.move_to(
            [side / 2, triangle_height / 3, 0],
            aligned_edge=DL,
        )
        detached.move_to(
            [0, -2 * triangle_height / 3, 0],
            aligned_edge=UP,
        )

        # Connect the middle of the edges with straight arrows
        def connect(start, end):
            return Arrow(
                start,
                end,
                buff=0.1,
                stroke_width=2,
                tip_length=0.15,
                max_tip_length_to_length_ratio=1,
            )

        forgetting = connect(
            informed[0].get_right(),
            uninformed[0].get_left(),
        )
        detachment = connect(
            uninformed[0].get_bottom(),
            detached[0].get_top(),
        )

        # Separate the opposite arrows along the absolute horizontal axis
        arrow_offset = RIGHT * 0.3
        attachment = connect(
            detached[0].get_top() + arrow_offset,
            informed[0].get_bottom() + arrow_offset,
        )
        informed_detachment = connect(
            informed[0].get_bottom() - arrow_offset,
            detached[0].get_top() - arrow_offset,
        )

        # Label only the loss of directional information
        forgetting_label = Text(
            "after ~10s",
            font_size=16,
        ).next_to(forgetting, DOWN, buff=0.12)

        return VGroup(
            informed,
            uninformed,
            detached,
            attachment,
            forgetting,
            detachment,
            informed_detachment,
            forgetting_label,
        )
