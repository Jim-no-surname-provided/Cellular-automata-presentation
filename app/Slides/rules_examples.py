import random

from manim import *  # pyright: ignore[reportWildcardImportFromLibrary]
from manim_slides.slide import ThreeDSlide
from PIL import Image, ImageFilter

from app.CellularAutomatonGrid import CellularAutomatonGrid
from app.ElementaryCA import ElementaryCA


class RulesExamples(ThreeDSlide):
    @property
    def wait_time_between_slides(self) -> float:
        return 0.1

    def construct(self):
        height = 141
        width = 300
        self.make_rules(height, width, 0.9 * config.frame_height / height)

    def make_rules(self, height, width, cell_size):
        # Create both grids using the helpers
        print("Creating r90")
        r90 = ElementaryCA(
            height,
            width,
            rule_n=90,
            cell_size=cell_size,
            stroke_opacity=0,
            stroke_width=0.0,
        )
        print("Creating r110")
        r110 = ElementaryCA(
            height,
            width,
            rule_n=110,
            cell_size=cell_size,
        )
        print("Creating r110_ether")
        r110_ether = ElementaryCA(
            height,
            1271,
            rule_n=110,
            cell_size=cell_size,
        )
        print("Creating r110_collision")
        r110_collision = ElementaryCA(
            height,
            1347,
            rule_n=110,
            cell_size=cell_size,
        )
        print("Creating r30")
        r30 = ElementaryCA(
            height,
            width,
            rule_n=30,
            cell_size=cell_size,
        )
        print("Creating r30_random")
        r30_random = ElementaryCA(
            height,
            2 * width,
            rule_n=30,
            cell_size=cell_size,
        )
        print("Creating r30_shell")
        r30_shell = ElementaryCA(
            height,
            width,
            rule_n=30,
            cell_size=cell_size,
            on_color=ManimColor("#B5522D"),
            off_color=WHITE,
        )
        print("Creating r34")
        r34 = ElementaryCA(
            height,
            width,
            rule_n=34,
            cell_size=cell_size,
        )
        print("All ECAs created")
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
        r30_random.set_initial_configuration(
            "".join(random.choice("01") for _ in range(r30_random.cols))
        )
        r30_shell.set_initial_configuration(
            "".join(random.choice("01") for _ in range(r30_shell.cols))
        )

        cas = (r90, r110, r110_ether, r110_collision, r30, r30_random, r30_shell, r34)

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

        def render_ca(r: CellularAutomatonGrid, fade_out: bool = True):
            image = r.to_image()
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
        render_ca(r30_random)

        self.shell3d(r30_shell)

        render_ca(r34)

        self.wait(0.1)

    def shell3d(
        self, eca: ElementaryCA, turns=3.25, duration=8, length=3, visible_width=100
    ):
        width = min(visible_width, eca.cols)
        gens = eca.rows
        start_col = (eca.cols - width) // 2  # so the window is centered
        max_u = TAU * turns

        # Map CA coordinates onto a growing spiral shell
        def shell(u, v):
            base_radius = 0.01 * u

            amplitude = 1.7
            mean = -length/2
            sigma_left = 0.4
            sigma_right = 1.2

            sigma = sigma_left if v < mean else sigma_right
            gaussian = np.exp(-0.5 * ((v - mean) / sigma) ** 2)
            r = base_radius * (1 + amplitude * gaussian)

            return np.array(
                [
                    r * np.sin(u),
                    v * (1 - 0.01 * u),
                    r * np.cos(u),
                ]
            )

        # Create a parametric surface with one face per CA cell
        surface = Surface(
            shell,
            u_range=(0, max_u),
            v_range=(-2 * length / 3, length / 3),
            resolution=(gens, width),
            checkerboard_colors=False,
            stroke_width=0,
            fill_opacity=1,
        )

        # Color each face according to its corresponding CA cell
        # Reverse the row or column mapping if necessary
        for face in surface:
            row = face.u_index
            col = start_col + face.v_index

            cell = eca.cells[row * eca.cols + col]
            color = eca.on_color if cell.alive else eca.off_color

            face.set_fill(color, opacity=1)

        # Position the shell and configure the 3D camera
        surface.move_to(ORIGIN)

        self.set_camera_orientation(
            phi=65 * DEGREES,
            theta=-45 * DEGREES,
        )

        self.add(surface)

        # Prepare the growth animation
        # Group faces by generation, following the u direction
        rings = [VGroup() for _ in range(gens)]

        for face in surface:
            rings[face.u_index].add(face)

        # Hide all faces initially without changing their colors
        for ring in rings:
            ring.set_opacity(0)

        # Animate growth by revealing one generation at a time
        self.play(
            AnimationGroup(
                *(ring.animate.set_opacity(1) for ring in rings),
                lag_ratio=1,
                run_time=duration,
                rate_func=linear,
            )
        )

        # Finish the slide
        self.next_slide()

        # Fade out the shell
        self.play(FadeOut(surface), run_time=0.5)

        # Reset the camera for the following 2D slides
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

    def blur_image(self, image: ImageMobject, radius: float = 3) -> ImageMobject:
        blurred = Image.fromarray(image.pixel_array).filter(
            ImageFilter.GaussianBlur(radius)
        )

        result = ImageMobject(np.array(blurred))
        result.match_width(image)
        result.move_to(image)
        return result
