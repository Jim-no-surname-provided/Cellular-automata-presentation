from manim import Text, DOWN

# Internal state
_DEBUG_STATE = {
    "scene": None,
    "label": None,
    "edge": DOWN,
    "buff": 0.2,
    "font_size": 22,
    "color": "#ffffff",
}

def set_debug_context(scene, *, edge=_DEBUG_STATE["edge"], buff=_DEBUG_STATE["buff"], font_size=_DEBUG_STATE["font_size"], color=_DEBUG_STATE["color"]):
    """Call once (e.g., in construct) to register the scene for debug_log()/clear_log()."""
    _DEBUG_STATE.update(scene=scene, edge=edge, buff=buff, font_size=font_size, color=color)

def debug_log(message: str):
    """Create or update a small debug text pinned to the bottom edge."""
    sc = _DEBUG_STATE["scene"]
    if sc is None:
        raise RuntimeError("set_debug_context(scene) must be called before debug_log().")

    label = _DEBUG_STATE["label"]
    if label is None:
        # First time: create and add
        label = Text(
            message,
            font_size=_DEBUG_STATE["font_size"],
            color=_DEBUG_STATE["color"],
        )
        label.set_z_index(1000)  # keep above most things
        label.to_edge(_DEBUG_STATE["edge"], buff=_DEBUG_STATE["buff"])
        sc.add(label)
        sc.wait(1e-6)
        _DEBUG_STATE["label"] = label
    else:
        # Update in-place while preserving edge pinning
        edge = _DEBUG_STATE["edge"]
        buff = _DEBUG_STATE["buff"]
        font_size = _DEBUG_STATE["font_size"]
        color = _DEBUG_STATE["color"]

        new_label = Text(message, font_size=font_size, color=color)
        new_label.to_edge(edge, buff=buff).set_z_index(label.z_index)
        label.become(new_label)
        sc.wait(1e-6)

def clear_log():
    """Remove the debug text if present."""
    sc = _DEBUG_STATE["scene"]
    label = _DEBUG_STATE["label"]
    if sc is None or label is None:
        return
    sc.remove(label)
    _DEBUG_STATE["label"] = None
