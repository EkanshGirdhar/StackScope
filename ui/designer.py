# StackScope - Language to DPDA Generator & Visualizer
# No __init__.py is used in this project.

import streamlit as st
from pda.pda_core import PushdownAutomaton
from pda.generator import LANGUAGE_CATALOG, generate_dpda_for_language
from pda.diagram import generate_pda_dot

def render_designer():
    """Renders the automated Language-to-DPDA generator and transition viewer."""
    st.header("DPDA Generator")
    st.caption("Select any theoretical DPDA language case to automatically synthesize the automaton, view all transitions, and render the state diagram.")

    # 1. Direct Language Selection (No Category filter)
    languages = list(LANGUAGE_CATALOG.keys())
    selected_lang = st.selectbox("Select Language:", languages)

    meta = LANGUAGE_CATALOG[selected_lang]
    st.info(f"*{meta['description']}*")

    # Generate the DPDA for the chosen language
    pda, err = generate_dpda_for_language(selected_lang)
    if err or not pda:
        st.error(f"Error generating DPDA: {err}")
        return

    # Update active PDA in session state for simulator and diagram tabs
    st.session_state["pda"] = pda

    st.markdown("---")

    # 2. Formal 7-Tuple Specification
    st.subheader(f"Formal DPDA for {pda.name}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"- **States ($Q$):** `{{{', '.join(pda.states)}}}`")
        st.write(f"- **Input Alphabet ($\\\\Sigma$):** `{{{', '.join(pda.input_alphabet)}}}`")
    with col2:
        st.write(f"- **Stack Alphabet ($\\\\Gamma$):** `{{{', '.join(pda.stack_alphabet)}}}`")
        st.write(f"- **Start State ($q_0$):** `{pda.initial_state}`")
    with col3:
        st.write(f"- **Initial Stack ($Z_0$):** `{pda.initial_stack_symbol}`")
        st.write(f"- **Final States ($F$):** `{{{', '.join(pda.final_states)}}}`")

    st.markdown("---")

    # 3. Complete Transitions Table & Diagram side-by-side
    col_trans, col_diag = st.columns([1, 1])

    with col_trans:
        st.subheader(f"All Transitions ({len(pda.transitions)} Rules)")
        table_rows = [
            {
                "#": i + 1,
                "Rule": f"δ({t.from_state}, {t.input_symbol}, {t.stack_top}) = ({t.to_state}, {t.push_symbols_str()})"
            }
            for i, t in enumerate(pda.transitions)
        ]
        st.dataframe(table_rows, use_container_width=True, hide_index=True)

    with col_diag:
        st.subheader("Transition Diagram")
        dot_str = generate_pda_dot(pda)
        st.graphviz_chart(dot_str, use_container_width=True)
