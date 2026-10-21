from manim import ORIGIN
from manim_slides.slide import Slide

from app.data import VideoMobject
from app.paths import RES_DIR, SLIDES_DIR
from app.slides.intro import MEDIA_HEIGHT


class Ants(Slide):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("output_folder", SLIDES_DIR)
        super().__init__(*args, **kwargs)

    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        single_ant: VideoMobject = (
            VideoMobject(
                str(RES_DIR / "single_ant.mov"),
                start_time=5,
                end_time=30,
            )
            .set_height(MEDIA_HEIGHT)
            .move_to(ORIGIN)
        )
        
        self.add(single_ant)
        self.wait(single_ant.remaining_time())
        
        self.next_slide()
        self.remove(single_ant)
        
        simulated_ants: VideoMobject = (
            VideoMobject(
                str(RES_DIR / "simulated_ants.mov"),
                start_time=5,
                end_time=30,
            )
            .set_height(MEDIA_HEIGHT)
            .move_to(ORIGIN)
        )
        self.add(simulated_ants)
        self.wait(simulated_ants.remaining_time())