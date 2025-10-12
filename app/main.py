from manim import *
from manim_slides import Slide, ThreeDSlide
from title import play as title
from intro import play as intro


class Main(Slide):
    def construct(self):
        # ! Commented during work since it takes a long time to compile
        # title(self)
        intro(self)
        self.game_of_life()
        self.community_achievements()

    def game_of_life(self):
        pass

    def community_achievements(self):
        pass
