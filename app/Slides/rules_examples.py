from ElementaryCA import ElementaryCA
from manim import *  # pyright: ignore[reportWildcardImportFromLibrary]
from manim_slides.slide import Slide
from PIL import Image, ImageFilter


class RulesExamples(Slide):
    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        height = 141
        width = 300
        self.make_rules(height, width, 0.9 * config.frame_height / height)

    def make_rules(self, height, width, cell_size):
        # Create both grids using the helpers
        r90 = ElementaryCA(
            height,
            width,
            rule_n=90,
            cell_size=cell_size,
            stroke_opacity=0,
            stroke_width=0.0,
        )
        r110 = ElementaryCA(
            height,
            width,
            rule_n=110,
            cell_size=cell_size,
        )
        r110_ether = ElementaryCA(
            height,
            1271,
            rule_n=110,
            cell_size=cell_size,
        )
        r110_collision = ElementaryCA(
            height,
            1347,
            rule_n=110,
            cell_size=cell_size,
        )
        r30 = ElementaryCA(
            height,
            width,
            rule_n=30,
            cell_size=cell_size,
        )
        r34 = ElementaryCA(
            height,
            width,
            rule_n=34,
            cell_size=cell_size,
        )
        r110.to_edge(RIGHT, buff=3)

        # Set initial states
        r90.set_primitive_configuration()
        r30.set_primitive_configuration()
        r34.set_primitive_configuration()
        r110.set_primitive_configuration(width // 2 - 3)

        ether = "11111000100110"
        glider_D1 = "11111000010"
        glider_A = "111110"
        glider_Bhat = "111110000100011001011010110011000100110"

        r110_ether.set_initial_configuration(ether * 45 + glider_D1 + ether * 45)
        r110_collision.set_initial_configuration(
            ether * 45 + glider_A + ether * 3 + glider_Bhat + ether * 45
        )

        cas = (r90, r110, r110_ether, r110_collision, r30, r34)

        # For low quality, make it smaller
        gens = height - 1 if config.quality != "low_quality" else int(0.2 * height)

        print("Running CAs")
        # Run the CA evolution
        for _ in range(gens):
            for g in cas:
                g.step()

        r90.update_cell_colors()

        # Run Add the first row
        row = VGroup(*[c.copy() for c in r90.get_row(0)]).move_to(ORIGIN)
        self.add(row)
        self.next_slide()
        self.remove(row)

        # Run g90 in 1d
        for r in range(gens):
            row = VGroup(*[c.copy() for c in r90.get_row(r)]).move_to(ORIGIN)
            self.add(row)
            self.wait(0.2)
            self.remove(row)
        self.next_slide()

        def render_ca(g, fade_out: bool = True):
            image = g.to_image()

            cover = Rectangle(
                width=image.width,
                height=image.height,
                stroke_width=0,
                fill_color=BLACK,
                fill_opacity=1,
            ).move_to(image)

            self.add(image, cover)
            self.play(
                cover.animate.shift(DOWN * image.height),
                run_time=4,
                rate_func=linear,
            )

            self.remove(cover)
            self.next_slide()
            if fade_out:
                self.play(FadeOut(image), run_time=0.4)
            return image

        # Render CAs
        render_ca(r90)
        img_r110 = render_ca(r110, False)
        img_r110_blurred = self.blur_image(img_r110, radius=1)
        
        self.play(FadeTransform(img_r110, img_r110_blurred))
        self.next_slide()
        self.play(FadeOut(img_r110_blurred))

        render_ca(r110_ether)
        img_r110_collision = render_ca(r110_collision, False)
        img_r110_col_blurred = self.blur_image(img_r110_collision, radius=1)
        
        self.play(FadeTransform(img_r110_collision, img_r110_col_blurred))
        self.next_slide()
        self.play(FadeOut(img_r110_col_blurred))

        render_ca(r30)
        render_ca(r34)

        self.wait(0.1)

    def blur_image(self, image: ImageMobject, radius: float = 3) -> ImageMobject:
        blurred = Image.fromarray(image.pixel_array).filter(
            ImageFilter.GaussianBlur(radius)
        )

        result = ImageMobject(np.array(blurred))
        result.match_width(image)
        result.move_to(image)
        return result
