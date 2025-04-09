class TuringMachine:
    def __init__(self, states, tape_alphabet, transitions, start_state, blank_symbol, accept_state, input_string):
        self.states = states  # {q0, q1, q2, q3, q4}
        self.tape_alphabet = tape_alphabet  # {0,1,X,Y,B}
        self.transitions = transitions  # Transition function
        self.current_state = start_state  # q0
        self.blank_symbol = blank_symbol  # B
        self.accept_state = accept_state  # q4
        self.head_position = 0
        self.tape = list(input_string) + [blank_symbol]  # Append blank at the end

    def step(self):
        if self.current_state == self.accept_state:
            return False  # Machine halts

        current_symbol = self.tape[self.head_position]
        if (self.current_state, current_symbol) in self.transitions:
            new_state, new_symbol, move = self.transitions[(self.current_state, current_symbol)]
            self.tape[self.head_position] = new_symbol  # Write new symbol
            self.current_state = new_state  # Change state
            
            if move == 'R':
                self.head_position += 1
            elif move == 'L':
                self.head_position = max(0, self.head_position - 1)
            return True
        else:
            return False  # No transition, halt

    def run(self):
        print("Initial tape:", ''.join(self.tape))
        while self.step():
            print("State:", self.current_state, "Tape:", ''.join(self.tape), "Head:", self.head_position)
        print("Final tape:", ''.join(self.tape))
        print("Machine halted in state:", self.current_state, "(Accepted)" if self.current_state == self.accept_state else "(Rejected)")

# Define Turing machine components
states = {"q0", "q1", "q2", "q3", "q4"}
tape_alphabet = {"0", "1", "X", "Y", "B"}
transitions = {
    ("q0", "0"): ("q1", "X", "R"),
    ("q0", "1"): ("q0", "Y", "L"),
    ("q1", "0"): ("q1", "0", "R"),
    ("q1", "1"): ("q2", "Y", "L"),
    ("q2", "0"): ("q1", "X", "R"),
    ("q2", "X"): ("q0", "X", "R"),
    ("q3", "Y"): ("q3", "Y", "R"),
    ("q3", "1"): ("q4", "B", "R"),
}
start_state = "q0"
blank_symbol = "B"
accept_state = "q4"
input_string = "0011"

# Create and run Turing Machine
tm = TuringMachine(states, tape_alphabet, transitions, start_state, blank_symbol, accept_state, input_string)
tm.run()
