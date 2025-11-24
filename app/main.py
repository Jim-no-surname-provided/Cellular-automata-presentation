from manim import *
from manim_slides import Slide
from intro import Intro
from title import Title 
from formal_definition import Formal_Def 


class Main(Slide):
    def construct(self):
        Title()
        Intro()
        Formal_Def()
        
