# StackScope - PDA Graphviz Diagram Generator
# No __init__.py is used in this project.

from pda.pda_core import PushdownAutomaton, Transition

def generate_pda_dot(
    pda: PushdownAutomaton,
    current_state: str = None,
    active_transition: Transition = None
) -> str:
    """Generates Graphviz DOT syntax for the PDA, highlighting active state and transition."""
    lines = [
        "digraph PDA {",
        "  rankdir=LR;",
        '  node [fontname="sans-serif", fontsize=11];',
        '  edge [fontname="sans-serif", fontsize=10];'
    ]

    # Initial state pointer
    if pda.initial_state:
        lines.append('  __start [shape=none, label="", width=0, height=0];')
        lines.append(f'  __start -> "{pda.initial_state}";')

    # States
    for s in pda.states:
        shape = "doublecircle" if s in pda.final_states else "circle"
        highlight = 'style=filled fillcolor="#FFE69C" penwidth=2' if s == current_state else 'color="#333333"'
        lines.append(f'  "{s}" [shape={shape} {highlight}];')

    # Transitions
    for t in pda.transitions:
        is_active = (t is active_transition) or (
            active_transition is not None and (t.from_state, t.input_symbol, t.stack_top) == (active_transition.from_state, active_transition.input_symbol, active_transition.stack_top)
        )
        edge_style = 'color="#D9534F" fontcolor="#D9534F" penwidth=2' if is_active else 'color="#555555"'
        lines.append(f'  "{t.from_state}" -> "{t.to_state}" [label="{t.to_display_label()}" {edge_style}];')

    lines.append("}")
    return "\n".join(lines)
