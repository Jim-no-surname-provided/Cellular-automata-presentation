import cv2
from manim import *
from manim_slides.slide import Slide

from app.VideoMobject import VideoMobject

MEDIA_HEIGHT = 3

class Intro(Slide):
    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        # Show the birds with their credits
        birds, birds_end = self.load_clip(
            "res/Flock of Birds.mkv", start=8, end=30
        )
        birds_credits = self.make_credits("Youtube: The Pet Collective Too")
        birds.suspend_updating()
        self.play(FadeIn(birds))
        self.next_slide()

        # Start playback after the opening still frame
        birds.resume_updating()
        self.play(FadeIn(birds_credits))
        self.finish_clip(birds, birds_end)
        self.next_slide()

        # Move the birds aside and remove their credits
        self.play(
            birds.animate.move_to(LEFT/2 + UP/2, aligned_edge=DR),
            FadeOut(birds_credits),
        )

        # Show the multiple ants with the shared paper citation
        ants_credits = self.make_credits(
            "Dreyer et al., Comparing cooperative geometric puzzle solving "
            "in ants versus humans, PNAS 122(1), e2414274121 (2025)"
        )
        multiple_ants, multiple_ants_end = self.load_clip(
            "res/multiple_ants.mov", start=2, end=None
        )
        self.add(multiple_ants)
        self.play(FadeIn(ants_credits))
        self.finish_clip(multiple_ants, multiple_ants_end)

        # Replace the multiple ants with the single ant
        single_ant, single_ant_end = self.load_clip(
            "res/single_ant.mov", start=5, end=30
        )
        self.remove(multiple_ants)
        self.add(single_ant)
        self.finish_clip(single_ant, single_ant_end)
        self.next_slide()

        # Move the ants aside and remove their credits
        self.play(
            single_ant.animate.move_to(RIGHT/2 + UP/2, aligned_edge=DL),
            FadeOut(ants_credits),
        )

        # Show the shell photo with its attribution
        snail = ImageMobject("res/textile_cone.jpg")
        snail.set_height(MEDIA_HEIGHT).move_to(ORIGIN)
        snail_credits = self.make_credits(
            "Richard Ling, Own work, Cod Hole, Great Barrier Reef, "
            "Australia, CC BY-SA 3.0"
        )
        self.play(FadeIn(snail), FadeIn(snail_credits))
        self.wait(5)

        # Move the photo to the bottom and remove its credits
        self.play(
            snail.animate.move_to(DOWN/2, aligned_edge=UP),
            FadeOut(snail_credits),
        )
        self.next_slide()

        # Finish with the complete scene and fade everything out
        self.next_slide(auto_next=True)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

    def make_credits(self, text):
        return MathTex(
            r"\text{" + text + "}",
            font_size=10,
            color=GREY_B,
        ).to_corner(UR, buff=0.1).set_z_index(9999)

    def load_clip(self, filename, start, end):
        # Read the duration and validate the selected interval
        video = VideoMobject(filename)
        capture = video.status.videoObject
        fps = capture.get(cv2.CAP_PROP_FPS)
        frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        if not capture.isOpened() or fps <= 0 or frames <= 0:
            raise ValueError(f"Cannot read video duration: {filename}")
        duration = frames / fps
        end = duration if end is None else end
        if not 0 <= start < end <= duration:
            raise ValueError(
                f"Choose 0 <= start < end <= {duration:.3f} for {filename}"
            )

        # Seek to the start and keep playback within the chosen interval
        video.clear_updaters()
        video.status.time = start * 1000
        video.videoUpdater(video, 1e-9)

        def update_clip(mobject, dt):
            remaining = end - mobject.status.time / 1000
            if remaining > 0 and dt > 0:
                mobject.videoUpdater(mobject, min(dt, remaining))

        video.add_updater(update_clip)
        video.set_height(MEDIA_HEIGHT).move_to(ORIGIN)
        return video, end

    def finish_clip(self, video, end):
        # Wait for the remaining playback and freeze the final frame
        remaining = end - video.status.time / 1000
        if remaining > 0:
            self.wait(remaining, frozen_frame=False)
        video.clear_updaters()
