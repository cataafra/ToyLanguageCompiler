class FiniteAutomation:
    def __init__(self, filename):
        self.filename = filename
        self.states = []
        self.alphabet = []
        self.start = ''
        self.final = []
        self.transitions = {}
        self.read_from_file()

    def is_accept(self, string):
        state = self.start
        for char in string:
            if char not in self.alphabet:
                return False
            if (state, char) not in self.transitions.keys():
                return False
            state = self.transitions[(state, char)]
        return state in self.final

    def __str__(self):
        return "states: " + str(self.states) + "\n" \
            + "alphabet: " + str(self.alphabet) + "\n" \
            + "transitions: " + str(self.transitions) + "\n" \
            + "start: " + str(self.start) + "\n" \
            + "final: " + str(self.final) + "\n"

    def read_from_file(self):
        with open(self.filename) as file:
            self.states = file.readline().strip().split(':').pop().strip().split(" ")
            self.alphabet = file.readline().strip(':').split(":").pop().strip().split(" ")
            self.start = file.readline().strip().split(':').pop().strip()
            self.final = file.readline().strip().split(':').pop().strip().split(" ")
            self.transitions = {}
            for line in file:
                transition_str = line.strip().split(":").pop().strip()
                key = (transition_str.split(" ")[0].strip(), transition_str.split(" ")[1].strip())
                value = transition_str.split(" ")[2].strip()
                self.transitions[key] = value
