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
        self.wait(0.1)

    def make_rules(self, height, width, cell_size):
        # Reduce size if quality low, for testing purposes
        height = height if config.quality != "low_quality" else int(0.2 * height)

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
        gens = height - 1

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

        def render_and_then_blur(r: CellularAutomatonGrid):
            img = render_ca(r, False)
            blured = self.blur_image(img, radius=1)
            self.play(FadeTransform(img, blured))
            self.next_slide()
            self.play(FadeOut(blured))

        # Render CAs
        render_ca(r90)
        render_and_then_blur(r110)
        render_and_then_blur(r110_ether)
        render_and_then_blur(r110_collision)
        render_ca(r30)
        render_ca(r30_random)
        self.shell3d(r30_shell)
        render_ca(r34)

    def shell3d(
        self, eca: ElementaryCA, turns=3.25, duration=8, length=3, visible_width=100
    ):
        width = min(visible_width, eca.cols)
        gens = eca.rows
        start_col = (eca.cols - width) // 2  # so the window is centered
        max_u = TAU * turns

        # Map CA coordinates onto a growing spiral shell
        def shell(u, v):
            start_radius = 0.1
            growth_rate = 0.03
            base_radius = start_radius + growth_rate * u

            mean = -1.5

            A_L = (v + length) / (mean + length)
            A_R = 1/(1+np.exp(2.7*v-0.9))
            
            A = A_L if v < mean else A_R
            r = base_radius * A

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

        # Position the shell and configure the initial camera
        surface.move_to(ORIGIN)

        # Focus on the first generation
        first_ring_center = VGroup(
            *[face for face in surface if face.u_index == 0]
        ).get_center()

        self.set_camera_orientation(
            phi=0,
            theta=-90 * DEGREES,
            frame_center=first_ring_center,
            zoom=4,
        )

        self.add(surface)

        # Prepare the growth animation
        # Group faces by generation, following the u direction
        rings = [VGroup() for _ in range(gens)]

        for face in surface:
            rings[face.u_index].add(face)

        # Hide all faces initially
        for ring in rings:
            ring.set_opacity(0)

        # Show the first generation
        rings[0].set_opacity(1)
        self.wait(0.1)  # it doesn't make an animation otherwise
        self.next_slide()

        # Show the second generation
        rings[1].set_opacity(1)
        self.wait(0.1)  # it doesn't make an animation otherwise
        self.next_slide()

        # Show the second generation
        rings[2].set_opacity(1)
        self.wait(0.1)  # it doesn't make an animation otherwise
        self.next_slide()

        # Reveal the remaining generations instantly as the camera moves
        def grow(mob, alpha):
            visible_gens = 2 + int(alpha * (gens - 2))

            for i in range(2, visible_gens):
                rings[i].set_opacity(1)

        self.move_camera(
            phi=60 * DEGREES,
            theta=-28 * DEGREES,
            zoom=2,
            frame_center=ORIGIN,
            added_anims=[
                UpdateFromAlphaFunc(surface, grow),
            ],
            run_time=duration,
            rate_func=linear,
        )

        # Finish the slide
        self.next_slide()

        # Place the photo at the right third-divider of the screen
        snail = ImageMobject("res/textile_cone.jpg")
        snail.set_height(0.65 * config.frame_height)
        if snail.width > 0.4 * config.frame_width:
            snail.set_width(0.4 * config.frame_width)
        snail.move_to(RIGHT * config.frame_width / 6)
        snail.scale(0.9)

        # Keep the photo in screen coordinates despite the 3D camera
        self.add_fixed_in_frame_mobjects(snail)
        self.remove(snail)

        # Convert the left screen position into world coordinates
        screen_target = LEFT * config.frame_width / 6
        shell_target = (
            self.camera.frame_center
            + self.camera.get_rotation_matrix().T
            @ (screen_target / self.camera.get_zoom())
        )

        # Move the shell left while revealing the photo in place
        self.play(
            surface.animate.move_to(shell_target),
            FadeIn(snail),
            run_time=1.2,
        )
        self.next_slide()

        # Fade out both
        self.play(
            FadeOut(surface),
            FadeOut(snail),
            run_time=0.5,
        )
        self.remove_fixed_in_frame_mobjects(snail)

        # Reset the camera for the following 2D slides
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1)

    def blur_image(self, image: ImageMobject, radius: float = 3) -> ImageMobject:
        blurred = Image.fromarray(image.pixel_array).filter(
            ImageFilter.GaussianBlur(radius)
        )

        result = ImageMobject(np.array(blurred))
        result.match_width(image)
        result.move_to(image)
        return result
