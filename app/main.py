from manim import *
from manim_slides import Slide, ThreeDSlide
from title import play as title


class Main(Slide):
    def construct(self):
        title()
        self.intro()
        self.game_of_life()
        self.community_achievements()

    def intro(self):
        pass

    def game_of_life(self):
        pass

    def community_achievements(self):
        pass
