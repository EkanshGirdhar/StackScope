# StackScope - Main Application
# No __init__.py is used in this project.

import streamlit as st
from pda.generator import load_dpda_from_file
from ui.designer import render_designer
from ui.simulator import render_simulator

st.set_page_config(page_title="StackScope", page_icon="🥞", layout="wide")

def main():
    if "pda" not in st.session_state:
        st.session_state["pda"] = load_dpda_from_file("an_bn.json")

    pda = st.session_state["pda"]
    is_valid, _ = pda.validate()

    st.sidebar.title("StackScope")
    st.sidebar.caption("DPDA Simulator & Debugger")

    page = st.sidebar.radio("Navigation", ["DPDA Generator", "PDA Simulator"])

    st.sidebar.markdown("---")
    st.sidebar.write(f"**Language:** {pda.name}")
    st.sidebar.write(f"**Transitions:** {len(pda.transitions)} rules")
    if is_valid:
        st.sidebar.success("Valid DPDA")
    else:
        st.sidebar.error("Invalid DPDA")

    if page == "DPDA Generator":
        render_designer()
    elif page == "PDA Simulator":
        render_simulator()

if __name__ == "__main__":
    main()
