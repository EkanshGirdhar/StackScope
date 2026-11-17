# StackScope - PDA Simulator Interface
# No __init__.py is used in this project.

import time
import streamlit as st
from pda.pda_core import PushdownAutomaton
from pda.simulator import PDASimulator, SimulationResult
from pda.diagram import generate_pda_dot

def render_simulator():
    """Renders the step-by-step PDA Simulator with animated Graphviz diagram."""
    st.header("PDA Simulator")

    pda: PushdownAutomaton = st.session_state.get("pda")
    if not pda:
        st.warning("No PDA found. Please design or load a PDA first.")
        return

    # Check validity
    is_valid, errors = pda.validate()
    if not is_valid:
        st.error("The current PDA has validation errors. Fix them in Designer before simulating:")
        for err in errors:
            st.write(f"- {err}")
        return

    st.write(f"**Problem:** {pda.name}")

    # Input string
    col_in, col_btn = st.columns([3, 1])
    with col_in:
        input_str = st.text_input("Enter Input String", value="aabb", key="sim_input_box")
    with col_btn:
        st.write("")
        st.write("")
        run_btn = st.button("Simulate", use_container_width=True, type="primary")

    # Run simulation on input change or button click
    if run_btn or "sim_result" not in st.session_state or st.session_state.get("last_input") != input_str:
        sim = PDASimulator(pda)
        st.session_state["sim_result"] = sim.run(input_str)
        st.session_state["last_input"] = input_str
        st.session_state["sim_step_idx"] = 0

    res: SimulationResult = st.session_state["sim_result"]
    total_steps = len(res.steps)

    if total_steps == 0:
        st.warning("No simulation steps available.")
        return

    # Controls: Previous, Next, Reset, Play
    c_prev, c_step, c_next, c_reset, c_play = st.columns([1, 2, 1, 1, 1])

    with c_prev:
        if st.button("◀ Previous", use_container_width=True) and st.session_state["sim_step_idx"] > 0:
            st.session_state["sim_step_idx"] -= 1
            st.rerun()

    with c_next:
        if st.button("Next ▶", use_container_width=True) and st.session_state["sim_step_idx"] < total_steps - 1:
            st.session_state["sim_step_idx"] += 1
            st.rerun()

    with c_reset:
        if st.button("⏮ Reset", use_container_width=True):
            st.session_state["sim_step_idx"] = 0
            st.rerun()

    play_clicked = False
    with c_play:
        if st.button("▶ Play", use_container_width=True):
            play_clicked = True

    curr_idx = st.session_state["sim_step_idx"]
    with c_step:
        st.write(f"**Step {curr_idx} / {total_steps - 1}**")

    # Slider for quick step navigation
    if total_steps > 1:
        slider_idx = st.slider("Step Slider", 0, total_steps - 1, curr_idx, label_visibility="collapsed")
        if slider_idx != curr_idx and not play_clicked:
            st.session_state["sim_step_idx"] = slider_idx
            st.rerun()

    # Step view container
    step_container = st.empty()

    def show_step(step_idx):
        step = res.steps[step_idx]
        with step_container.container():
            st.markdown("---")
            st.write(f"**Step {step.step_number}:** {step.description}")

            col_info, col_diagram = st.columns([1, 1])

            with col_info:
                m1, m2, m3 = st.columns(3)
                with m1:
                    final_flag = " (Accepting)" if step.state in pda.final_states else ""
                    st.metric("Current State", f"{step.state}{final_flag}")
                with m2:
                    rem_text = step.remaining_input if step.remaining_input else "ε (empty)"
                    st.metric("Remaining Input", rem_text)
                with m3:
                    st.metric("Stack Top", step.stack_top)

                st.markdown("---")
                st.write("**Stack (Top to Bottom):**")
                if step.stack:
                    st.code("  |  ".join(reversed(step.stack)))
                else:
                    st.code("[Empty Stack]")

                if step_idx == total_steps - 1:
                    if res.is_accepted:
                        st.success(f"🎉 **ACCEPTED**: {res.reason}")
                    else:
                        st.error(f"❌ **REJECTED**: {res.reason}")

            with col_diagram:
                st.write("**State Transition Diagram (Live Highlight):**")
                dot_str = generate_pda_dot(pda, current_state=step.state, active_transition=step.transition)
                st.graphviz_chart(dot_str, use_container_width=True)

    # Animation loop
    if play_clicked:
        for idx in range(curr_idx, total_steps):
            show_step(idx)
            st.session_state["sim_step_idx"] = idx
            time.sleep(0.5)
        st.rerun()
    else:
        show_step(curr_idx)
