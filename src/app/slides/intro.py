from manim import *
from manim_slides.slide import Slide

from app.data import Credits, VideoMobject
from app.paths import ANTS_DIR, RES_DIR, SLIDES_DIR

MEDIA_HEIGHT = 3


class Intro(Slide):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("output_folder", SLIDES_DIR)
        super().__init__(*args, **kwargs)

    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        # Show the birds with their credits
        birds = (
            VideoMobject(
                str(RES_DIR / "Flock of Birds.mkv"),
                start_time=9,
                end_time=30,
            )
            .set_height(MEDIA_HEIGHT)
        )
        birds_credits = Credits("Youtube: The Pet Collective Too")
        birds.suspend_updating()
        self.play(FadeIn(birds))
        birds.suspend_updating()
        self.next_slide()

        # Start playback after the opening still frame
        birds.resume_updating()
        self.play(FadeIn(birds_credits))
        self.wait(birds.remaining_time())
        self.next_slide()

        # Move the birds aside and remove their credits
        self.play(
            birds.animate.move_to(LEFT / 2 + UP / 2, aligned_edge=DR),
            FadeOut(birds_credits),
        )

        # Show the multiple ants with the shared paper citation
        ants_credits = Credits(
            "Dreyer et al., Comparing cooperative geometric puzzle solving "
            "in ants versus humans, PNAS 122(1), e2414274121 (2025)"
        )

        # Replace the multiple ants with the single ant
        single_ant = (
            VideoMobject(
                str(ANTS_DIR / "single_ant.mov"),
                start_time=5,
                end_time=30,
            )
            .set_height(MEDIA_HEIGHT)
        )
        self.play(FadeIn(ants_credits), FadeIn(single_ant))
        self.wait(single_ant.remaining_time())
        self.next_slide()

        # Move the ants aside and remove their credits
        self.play(
            single_ant.animate.move_to(RIGHT / 2 + UP / 2, aligned_edge=DL),
            FadeOut(ants_credits),
        )

        # Show the shell photo with its attribution
        snail = ImageMobject(str(RES_DIR / "textile_cone.jpg"))
        snail.set_height(MEDIA_HEIGHT)
        snail_credits = Credits(
            "Richard Ling, Own work, Cod Hole, Great Barrier Reef, "
            "Australia, CC BY-SA 3.0"
        )
        self.play(FadeIn(snail), FadeIn(snail_credits))
        self.wait(5)

        # Move the photo to the bottom and remove its credits
        self.play(
            snail.animate.move_to(DOWN / 2, aligned_edge=UP),
            FadeOut(snail_credits),
        )
        self.next_slide()

        # Finish with the complete scene and fade everything out
        self.next_slide(auto_next=True)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)