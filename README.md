# StackScope – An Interactive Pushdown Automata Simulator and Visual Debugger

StackScope is a web-based educational tool built for students to understand and visualize the inner workings of **Deterministic Pushdown Automata (DPDA)**.

## Project Structure

```text
TOC Project/
│
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation and setup instructions
├── app.py              # Streamlit web application entry point
├── test_pda.py         # Unit test suite for PDA simulation logic
├── pda/                # Core PDA simulation and validation logic
│   ├── pda_core.py     # PDA 7-tuple and DPDA validation rules
│   ├── generator.py    # JSON-driven DPDA loader and catalog
│   ├── simulator.py    # Step-by-step DPDA simulation engine
│   └── diagram.py      # Graphviz DOT generator with live step highlighting
├── ui/                 # Streamlit web user interface components
│   ├── designer.py     # Automated DPDA Generator and transition viewer
│   └── simulator.py    # Step-by-step PDA Simulator with live diagram & stack view
└── data/               # 18 JSON-defined DPDA language configurations
    ├── 0n_1n.json
    ├── a2n_bn.json
    ├── am_bn_cn.json
    ├── an_b2n.json
    ├── an_b3n.json
    ├── an_bm_cn.json
    ├── an_bn.json
    ├── an_bn_cm.json
    ├── an_bn_empty.json
    ├── balanced_parentheses.json
    ├── inequality_m_greater_n.json
    ├── inequality_n_greater_m.json
    ├── inequality_n_neq_m.json
    ├── mixed_brackets.json
    ├── palindrome_c.json
    ├── palindrome_hash.json
    ├── sum_a_bm_cn.json
    └── sum_an_bm_c.json
```

## Technology Stack

- **Python**: Core simulation logic and DPDA processing.
- **Streamlit**: Web interface and interactive visualization controls.
- **Graphviz**: Automaton state-transition diagrams.
- **JSON**: Storage format for sample PDA configurations.

## Setup and Running

1. **Activate the virtual environment**:
   - On Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On Windows (Command Prompt):
     ```cmd
     venv\Scripts\activate.bat
     ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

4. **Run the unit tests**:
   ```bash
   python test_pda.py
   ```

