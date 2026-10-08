from manim_slides.slide import Slide
from manim import * # pyright: ignore[reportWildcardImportFromLibrary]
from GameOfLifeGrid import GameOfLifeGrid
from video_mobject_opencv import VideoMobject

ICONS_Z_INDEX = 1

class Intro(Slide):
    def construct(self):
        self.rules_explanation()

    def rules_explanation(self):

        # Form 5x5 grid in the middle
        grid = GameOfLifeGrid(7, 7)
        self.play(LaggedStart(*[Create(c) for c in grid.cells], lag_ratio=0.01))
        self.next_slide()

        def update_grid():
            grid.step()
            self.play(*grid.render_cells(), run_time=0.4)

        # Make some of them be alive (middle cell should be alive)
        grid.set_alive({(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, -2)})  # configuration
        self.play(*grid.render_cells(), run_time=0.4)
        self.next_slide()

        # Update (middle cell should die)
        update_grid()
        self.next_slide()

        # Move to the left and
        # write "Rule as a title on the right"
        rules = Paragraph(
            "Rules",
            "  1. Any dead cell with\nthree alive neighbors becomes alive",
            "  2. Any alive cell with\ntwo or three neighbors survives",
            alignment="left",
            line_spacing=0.6,
            t2c={
                "dead": RED,
                "alive": GREEN,
                "survives": GREEN,
            },
        )

        rules[0].set(weight=BOLD).scale(1.2)
        rules.scale(0.6).move_to(RIGHT * 0.5, aligned_edge=LEFT)

        for rule in rules[1:]:
            rule.set_opacity(0.7)

        self.play(
            grid.animate.move_to(LEFT * (config.frame_width / (6))),
            Write(rules[0]),
            run_time=1
        )
        self.next_slide()

        # Add the rule "Dead cells with 3 cells become alive" and
        # Count neighbors around middle cell
        anims, labels = self.label_alive_neighbors(grid)

        # Declare skull and smile svgs and actual icon that will appear on screen
        skull = (
            SVGMobject("src/skull.svg")
            .set_fill(WHITE)
            .set_height(grid.get_cell(0, 0).get_height() * 0.6)
            .move_to(grid.get_cell(0, 0).get_center())
            .set_z_index(ICONS_Z_INDEX)
        )
        smile = (
            SVGMobject("src/smile.svg")
            .set_fill(BLACK)
            .set_height(grid.get_cell(0, 0).get_height() * 0.6)
            .move_to(grid.get_cell(0, 0).get_center())
            .set_z_index(ICONS_Z_INDEX)
        )
        icon = skull.copy()

        self.play(
            Write(rules[1]),
            Write(rules[2]),
            Indicate(grid.get_cell(0, 0), color=BLUE_A),
            FadeIn(icon, scale=0.3),
            *anims,
            run_time=0.5
        )
        self.next_slide()

        # Update (middle cell should come to life)
        grid.step()
        self.play(
            *self.disappear_labels_to_center(grid, labels),
            *grid.render_cells(),
            Transform(icon, smile),
            run_time=0.4)
        self.play(icon.animate.set_opacity(icon.get_opacity()))

        labels = []
        self.next_slide()

        # Add the rule "Alive cells with 2 or 3 cells stay alive" and
        # Count neighbors around middle cell
        anims, labels = self.label_alive_neighbors(grid)
        self.play(
            Write(rules[3]),
            Write(rules[4]),
            *anims,
            run_time=0.5
        )
        self.next_slide()

        # Update (middle cell should survive)
        grid.step()
        self.play(
            *self.disappear_labels_to_center(grid, labels),
            *grid.render_cells(),
            Indicate(icon),
            run_time=0.4)
        self.next_slide()

        # Count neighbors around middle cell
        anims, labels = self.label_alive_neighbors(grid)
        self.play(
            *anims,
            run_time=0.5
        )
        self.next_slide()

        # Update (middle cell should die)
        grid.step()
        self.play(
            *self.disappear_labels_to_center(grid, labels),
            *grid.render_cells(),
            Transform(icon, skull),
            run_time=0.4)
        self.next_slide()

        # Let run and fade out
        self.play(FadeOut(Group(*self.mobjects)), run_time=.2)
        self.community_achievements()

    def community_achievements(self):
        cpu = VideoMobject(r"src\cpu recordings\sine_cpu.mp4")
        display = VideoMobject(r"src\cpu recordings\sine_display.mp4")
        gliders = VideoMobject(r"src\cpu recordings\gliders.mp4", loop=True)
        cpu_credits = MathTex(
            r"\text{@nicolasloizeau on github}",
            font_size=10,
            color=GREY_B,
        ).to_corner(UR, buff=0.1).set_z_index(9999)

        cpu.move_to(np.array([0.1, 0.0, 0.0])).set_height(8.0)
        display.move_to(np.array([4.0, -2.6, 0.0])).set_height(1.0).set_opacity(0)

        cpu.set_z_index(0)
        display.set_z_index(1)

        self.play(FadeIn(cpu), FadeIn(display), FadeIn(cpu_credits))
        self.wait(30)
        self.next_slide()

        gliders.move_to(np.array([-6.0, -2.6, 0.0])).set_height(2.0)

        self.play(
            display.animate.set_opacity(1),
            cpu.animate.move_to(np.array([-2.4, 0.0, 0.0])).set_height(8.0),
            display.animate.move_to(np.array([4.2, 1.2, 0.0])).set_height(5.3),
            FadeIn(gliders),
            run_time=1.2,
            rate_func=smooth
        )
        if config.quality == "low_quality":
            self.wait(2)
        else:
            self.wait(240)

        self.next_slide()
        self.play(
            FadeOut(cpu),
            FadeOut(display),
            FadeOut(gliders),
            FadeOut(cpu_credits),
        )
        self.remove(gliders)
        self.wait(1e-9)

    def disappear_labels_to_center(self, grid, labels):
        return [
            label.animate
            .move_to(grid.get_cell(0, 0).get_center())
            .scale(0.1)
            .set_opacity(0)
            for label in labels
        ]

    def label_alive_neighbors(self, grid):
        def alive_neighbors_of(x, y):
            return [
                cell
                for cell in grid.neighbors_of(x, y)
                if cell.alive
            ]

        anims = []
        labels = []
        for i, cell in enumerate(alive_neighbors_of(0, 0), start=1):
            # tiny number
            num_label = Text(str(i)).scale(0.3)
            num_label.move_to(cell.get_center())

            # cell.add(num_label)  # attach to this cell
            num_label.set_z_index(ICONS_Z_INDEX)

            # store in a list to eliminate later
            labels.append(num_label)
            # tint that cell
            anims.append(cell.animate.set_fill(PINK))
            # make it appear nicely
            anims.append(Write(num_label))
        return anims, labels

    def conway(self, target_width_percentage):
        img = ImageMobject("src/Conway picture.jpg")
        img.set_height(target_width_percentage * config.frame_height)

        caption = Paragraph(
            "John Conway",
            "(26 December 1937 - 11 April 2020)",
            alignment="center",
        ).set_width(img.get_width()).next_to(img, DOWN)

        # Group image and caption
        conway_group = Group(img, caption)
        return conway_group
