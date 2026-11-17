# StackScope - Pushdown Automata Core Data Structures & Validation
# No __init__.py is used in this project.

EPSILON = "ε"
EPSILON_ALIASES = {"", "ε", "e", "eps", "epsilon", "λ", "lambda"}

def is_epsilon(symbol) -> bool:
    """Check if a symbol represents an epsilon (empty/no-op) transition."""
    if symbol is None:
        return True
    return str(symbol).strip().lower() in EPSILON_ALIASES


def parse_push_symbols(push_symbols) -> list[str]:
    """
    Parses push symbols from a list or string into a clean list of symbols.
    Examples:
      - ["A", "Z0"] -> ["A", "Z0"]
      - "A, Z0"     -> ["A", "Z0"]
      - "A Z0"      -> ["A", "Z0"]
      - "ε" or ""   -> [] (pop only)
    """
    if isinstance(push_symbols, list):
        return [str(s).strip() for s in push_symbols if str(s).strip() and not is_epsilon(s)]
    
    text = str(push_symbols).strip()
    if is_epsilon(text):
        return []
    
    if "," in text:
        parts = text.split(",")
    elif " " in text:
        parts = text.split()
    else:
        return [text] if text else []
    
    return [p.strip() for p in parts if p.strip() and not is_epsilon(p)]


class Transition:
    """
    Represents a single PDA transition rule:
    delta(from_state, input_symbol, stack_top) -> (to_state, push_symbols)
    """
    def __init__(self, from_state: str, input_symbol: str, stack_top: str, to_state: str, push_symbols):
        self.from_state = str(from_state).strip()
        
        raw_sym = str(input_symbol).strip()
        self.input_symbol = EPSILON if is_epsilon(raw_sym) else raw_sym
        
        self.stack_top = str(stack_top).strip()
        self.to_state = str(to_state).strip()
        self.push_symbols = parse_push_symbols(push_symbols)

    @property
    def is_epsilon_transition(self) -> bool:
        """True if this transition does not consume any input symbol."""
        return self.input_symbol == EPSILON

    def push_symbols_str(self) -> str:
        """Returns string representation of pushed symbols, or 'ε' when popping only."""
        if not self.push_symbols:
            return EPSILON
        return " ".join(self.push_symbols)

    def to_display_label(self) -> str:
        """Standard PDA notation: input, stack_top -> push_symbols"""
        return f"{self.input_symbol}, {self.stack_top} -> {self.push_symbols_str()}"

    def to_dict(self) -> dict:
        return {
            "from_state": self.from_state,
            "input_symbol": self.input_symbol,
            "stack_top": self.stack_top,
            "to_state": self.to_state,
            "push_symbols": self.push_symbols
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            from_state=data["from_state"],
            input_symbol=data.get("input_symbol", EPSILON),
            stack_top=data["stack_top"],
            to_state=data["to_state"],
            push_symbols=data.get("push_symbols", [])
        )

    def __repr__(self):
        return f"Transition({self.to_display_label()} to {self.to_state})"


class PushdownAutomaton:
    """
    Formal 7-tuple DPDA: M = (Q, Sigma, Gamma, delta, q0, Z0, F)
    """
    def __init__(
        self,
        states=None,
        input_alphabet=None,
        stack_alphabet=None,
        initial_state="q0",
        initial_stack_symbol="Z0",
        final_states=None,
        transitions=None,
        name="Pushdown Automaton"
    ):
        self.name = name
        self.states = [str(s).strip() for s in (states or []) if str(s).strip()]
        self.input_alphabet = [str(a).strip() for a in (input_alphabet or []) if str(a).strip() and not is_epsilon(a)]
        self.stack_alphabet = [str(g).strip() for g in (stack_alphabet or []) if str(g).strip() and not is_epsilon(g)]
        self.initial_state = str(initial_state).strip()
        self.initial_stack_symbol = str(initial_stack_symbol).strip()
        self.final_states = [str(f).strip() for f in (final_states or []) if str(f).strip()]
        self.transitions = []
        if transitions:
            for t in transitions:
                if isinstance(t, Transition):
                    self.transitions.append(t)
                elif isinstance(t, dict):
                    self.transitions.append(Transition.from_dict(t))

    def add_transition(self, from_state, input_symbol, stack_top, to_state, push_symbols) -> Transition:
        t = Transition(from_state, input_symbol, stack_top, to_state, push_symbols)
        self.transitions.append(t)
        return t

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validates the DPDA definition against formal theoretical criteria:
        1. States, alphabet, stack alphabet non-empty.
        2. q0 in Q, Z0 in Gamma, F subset of Q.
        3. All transitions refer to valid states and alphabets.
        4. Determinism Check 1: No two identical (state, input, stack_top) transitions.
        5. Determinism Check 2: If delta(q, ε, X) exists, no delta(q, a, X) can exist for any a in Sigma.
        """
        errors = []

        if not self.states:
            errors.append("States set (Q) cannot be empty.")
        if not self.input_alphabet:
            errors.append("Input alphabet (Sigma) cannot be empty.")
        if not self.stack_alphabet:
            errors.append("Stack alphabet (Gamma) cannot be empty.")

        if self.initial_state not in self.states:
            errors.append(f"Initial state '{self.initial_state}' is not in states set Q.")

        if self.initial_stack_symbol not in self.stack_alphabet:
            errors.append(f"Initial stack symbol '{self.initial_stack_symbol}' is not in stack alphabet Gamma.")

        for f in self.final_states:
            if f not in self.states:
                errors.append(f"Final state '{f}' is not in states set Q.")

        seen_keys = set()
        epsilon_keys = set()      # (state, stack_top)
        input_keys = {}           # (state, stack_top) -> list of input symbols

        for i, t in enumerate(self.transitions):
            if t.from_state not in self.states:
                errors.append(f"Transition #{i+1}: from_state '{t.from_state}' is not in Q.")
            if t.to_state not in self.states:
                errors.append(f"Transition #{i+1}: to_state '{t.to_state}' is not in Q.")

            if not t.is_epsilon_transition and t.input_symbol not in self.input_alphabet:
                errors.append(f"Transition #{i+1}: input symbol '{t.input_symbol}' is not in Sigma.")

            if t.stack_top not in self.stack_alphabet:
                errors.append(f"Transition #{i+1}: stack top '{t.stack_top}' is not in Gamma.")

            for ps in t.push_symbols:
                if ps not in self.stack_alphabet:
                    errors.append(f"Transition #{i+1}: pushed symbol '{ps}' is not in Gamma.")

            # Determinism check 1: Duplicate transition
            key = (t.from_state, t.input_symbol, t.stack_top)
            if key in seen_keys:
                errors.append(
                    f"DPDA violation: Duplicate transition for state '{t.from_state}', "
                    f"input '{t.input_symbol}', stack top '{t.stack_top}'."
                )
            seen_keys.add(key)

            # Record for Determinism check 2: Epsilon conflict
            base_key = (t.from_state, t.stack_top)
            if t.is_epsilon_transition:
                epsilon_keys.add(base_key)
            else:
                if base_key not in input_keys:
                    input_keys[base_key] = []
                input_keys[base_key].append(t.input_symbol)

        # Determinism check 2: Conflicting epsilon and input transitions
        for base_key in epsilon_keys:
            if base_key in input_keys:
                conflicting_inputs = ", ".join(f"'{sym}'" for sym in input_keys[base_key])
                errors.append(
                    f"DPDA violation: Non-deterministic choice at state '{base_key[0]}' with stack top '{base_key[1]}'. "
                    f"It has both an epsilon transition and input transition(s) for {conflicting_inputs}."
                )

        return (len(errors) == 0, errors)

    def find_transition(self, current_state: str, input_symbol: str, stack_top: str):
        """Finds matching transition for (state, symbol, stack_top), or None."""
        for t in self.transitions:
            if t.from_state == current_state and t.input_symbol == input_symbol and t.stack_top == stack_top:
                return t
        return None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "states": self.states,
            "input_alphabet": self.input_alphabet,
            "stack_alphabet": self.stack_alphabet,
            "initial_state": self.initial_state,
            "initial_stack_symbol": self.initial_stack_symbol,
            "final_states": self.final_states,
            "transitions": [t.to_dict() for t in self.transitions]
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name", "Pushdown Automaton"),
            states=data.get("states", []),
            input_alphabet=data.get("input_alphabet", []),
            stack_alphabet=data.get("stack_alphabet", []),
            initial_state=data.get("initial_state", "q0"),
            initial_stack_symbol=data.get("initial_stack_symbol", "Z0"),
            final_states=data.get("final_states", []),
            transitions=[Transition.from_dict(t) for t in data.get("transitions", [])]
        )

    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str):
        import json
        return cls.from_dict(json.loads(json_str))
