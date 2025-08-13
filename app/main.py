from manim import *
from manim_slides import Slide, ThreeDSlide
from title import play_cellular_automata_title


class Main(Slide):
    def construct(self):
        self.title()
        self.intro()
        self.game_of_life()
        self.community_achievements()

    def title(self):
        play_cellular_automata_title(self)

    def intro(self):
        pass

    def game_of_life(self):
        pass

    def community_achievements(self):
        pass
