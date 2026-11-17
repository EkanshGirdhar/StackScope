# StackScope - Pushdown Automata Step Simulator
# Clean, simple simulation logic for college TOC.
# No __init__.py is used in this project.

from pda.pda_core import EPSILON, PushdownAutomaton, Transition


class SimulationStep:
    """Stores one instantaneous configuration of the PDA during execution."""
    def __init__(
        self,
        step_number: int,
        state: str,
        remaining_input: str,
        stack: list[str],
        transition: Transition = None,
        description: str = "",
        status: str = "RUNNING"
    ):
        self.step_number = step_number
        self.state = state
        self.remaining_input = remaining_input
        self.stack = list(stack)  # Deep copy of the stack at this step
        self.transition = transition
        self.description = description
        self.status = status

    @property
    def stack_top(self) -> str:
        """Returns the top of stack, or '(empty)'."""
        return self.stack[-1] if self.stack else "(empty)"


class SimulationResult:
    """Holds the complete result of simulating an input string on a DPDA."""
    def __init__(
        self,
        input_string: str,
        is_accepted: bool,
        status: str,
        reason: str,
        steps: list[SimulationStep]
    ):
        self.input_string = input_string
        self.is_accepted = is_accepted
        self.status = status  # "ACCEPTED" or "REJECTED"
        self.reason = reason
        self.steps = steps

    @property
    def total_steps(self) -> int:
        return len(self.steps)


class PDASimulator:
    """
    Simulates a Deterministic Pushdown Automaton step by step.
    Handles input symbols, epsilon transitions, and stack push/pop.
    """
    def __init__(self, pda: PushdownAutomaton, max_steps: int = 500):
        self.pda = pda
        self.max_steps = max_steps

    def run(self, input_string: str) -> SimulationResult:
        # 1. Validate PDA definition first
        is_valid, validation_errors = self.pda.validate()
        if not is_valid:
            error_msg = "; ".join(validation_errors)
            step0 = SimulationStep(
                step_number=0,
                state=self.pda.initial_state,
                remaining_input=input_string,
                stack=[self.pda.initial_stack_symbol] if self.pda.initial_stack_symbol else [],
                description=f"Invalid PDA definition: {error_msg}",
                status="REJECTED"
            )
            return SimulationResult(input_string, False, "REJECTED", error_msg, [step0])

        # 2. Validate input characters against input alphabet Sigma
        for idx, char in enumerate(input_string):
            if char not in self.pda.input_alphabet:
                error_msg = f"Invalid symbol '{char}' at index {idx}. Alphabet is {self.pda.input_alphabet}."
                step0 = SimulationStep(
                    step_number=0,
                    state=self.pda.initial_state,
                    remaining_input=input_string,
                    stack=[self.pda.initial_stack_symbol],
                    description=error_msg,
                    status="REJECTED"
                )
                return SimulationResult(input_string, False, "REJECTED", error_msg, [step0])

        # 3. Setup initial configuration
        current_state = self.pda.initial_state
        remaining_input = input_string
        stack = [self.pda.initial_stack_symbol]
        step_num = 0

        steps = [
            SimulationStep(
                step_number=0,
                state=current_state,
                remaining_input=remaining_input,
                stack=stack,
                description=f"Start at state '{current_state}', Stack [{stack[0]}], Input '{remaining_input or EPSILON}'",
                status="RUNNING"
            )
        ]

        # 4. Simulation loop
        while step_num < self.max_steps:
            # Acceptance check: all input consumed and current state is accepting
            if remaining_input == "" and current_state in self.pda.final_states:
                steps[-1].status = "ACCEPTED"
                reason = f"Input consumed and machine halted in accepting state '{current_state}'."
                return SimulationResult(input_string, True, "ACCEPTED", reason, steps)

            # Stack underflow check
            if not stack:
                steps[-1].status = "REJECTED"
                reason = "Stack underflow: Stack is empty, cannot perform any further transitions."
                return SimulationResult(input_string, False, "REJECTED", reason, steps)

            stack_top = stack[-1]
            chosen_transition = None
            consumed_char = None

            # Look for input-consuming transition first
            if remaining_input != "":
                next_char = remaining_input[0]
                t_input = self.pda.find_transition(current_state, next_char, stack_top)
                if t_input:
                    chosen_transition = t_input
                    consumed_char = next_char

            # If no input transition, look for an epsilon transition
            if not chosen_transition:
                chosen_transition = self.pda.find_transition(current_state, EPSILON, stack_top)

            # If no transition is possible, machine halts and rejects
            if not chosen_transition:
                steps[-1].status = "REJECTED"
                if remaining_input == "":
                    reason = f"Input fully consumed, but machine ended in non-accepting state '{current_state}' with no epsilon transition."
                else:
                    reason = f"Machine stuck: No valid transition from state '{current_state}' with input '{remaining_input[0]}' and stack top '{stack_top}'."
                return SimulationResult(input_string, False, "REJECTED", reason, steps)

            # Execute transition
            step_num += 1
            from_st = current_state
            to_st = chosen_transition.to_state

            popped = stack.pop()
            for sym in reversed(chosen_transition.push_symbols):
                stack.append(sym)

            if consumed_char:
                remaining_input = remaining_input[1:]
                action_text = f"Read '{consumed_char}', popped '{popped}', pushed '{chosen_transition.push_symbols_str()}', moved {from_st} -> {to_st}"
            else:
                action_text = f"Epsilon move, popped '{popped}', pushed '{chosen_transition.push_symbols_str()}', moved {from_st} -> {to_st}"

            current_state = to_st
            steps.append(
                SimulationStep(
                    step_number=step_num,
                    state=current_state,
                    remaining_input=remaining_input,
                    stack=stack,
                    transition=chosen_transition,
                    description=f"Step {step_num}: {action_text}",
                    status="RUNNING"
                )
            )

        # Step limit exceeded (e.g. infinite loop)
        steps[-1].status = "REJECTED"
        reason = f"Execution exceeded maximum step limit ({self.max_steps}). Probable infinite epsilon loop."
        return SimulationResult(input_string, False, "REJECTED", reason, steps)
