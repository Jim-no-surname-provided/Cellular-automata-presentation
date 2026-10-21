# Setup & Usage

### Installation
This project uses uv to handle the virtual enviroment. To create a .venv with the necessary dependencies use
```bash
uv sync --locked
```

---

### Rendering Slides
To compile the videos and then slides, use:
```bash
uv run manim-slides render src/app/slides/intro.py Intro
```
If your scene contains many sub-mobjects, disable caching:
```bash
uv run manim-slides render src/app/slides/rules_examples.py RulesExamples --disable_caching
```

---

### Running the Slideshow
Run the slides interactively with:
```bash
uv run manim-slides --folder ./build/slides TitleCA LifeSlide Formal_Def Elementary_CA_Slide RulesExamples
uv run manim-slides --folder ./build/slides TitleCA LifeSlide Formal_Def_Mai Elementary_CA_Slide RulesExamples
uv run manim-slides --folder ./build/slides Intro TitleSI Boids LifeSlide Formal_Def Elementary_CA_Slide RulesExamples

```

---

### Exporting to HTML
Convert slides and videos into an `.html` file with:
```bash
uv run manim-slides convert SCENE scene.html -ccontrols=true
uv run manim-slides convert --folder ./build/slides Intro TitleSI Boids LifeSlide Formal_Def Elementary_CA_Slide RulesExamples presentation.html -ccontrols=true
```
Omit `-ccontrols=true` if you don’t want the playback controls at the bottom.
