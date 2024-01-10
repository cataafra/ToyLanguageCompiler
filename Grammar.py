from Parser import LR0Parser

class FormalGrammar:
    def __init__(self, filename):
        self.filename = filename
        self.non_terminals = []
        self.terminals = []
        self.productions = {}
        self.start = ''
        self.read_from_file()

    def get_all_productions(self, non_terminal):
        return self.productions[non_terminal]

    def __str__(self):
        return "non-terminals: " + str(self.non_terminals) + "\n" \
            + "terminals: " + str(self.terminals) + "\n" \
            + "productions: " + str(self.productions) + "\n" \
            + "start: " + str(self.start) + "\n"

    def is_cfg(self):
        for key in self.productions:
            if key not in self.non_terminals:
                print(f"{key} is not a non-terminal")
                return False
        return True

    def print_productions(self, non_terminal):
        print(f"Productions for {non_terminal}:")
        for production in self.productions[non_terminal]:
            print(f"\t{non_terminal} -> {production}")

    def read_from_file(self):
        with open(self.filename) as file:
            self.non_terminals = file.readline().strip().split(":").pop().strip().split(" ")
            print(self.non_terminals)
            self.terminals = file.readline().strip().split(":").pop().strip().split(" ")
            self.start = file.readline().strip().split(":").pop().strip()
            for line in file:
                production_str = line.strip().split("->")
                key = production_str[0].strip()
                value = production_str[1].strip().split(" ")
                if key not in self.productions:
                    self.productions[key] = []
                self.productions[key].append(value)


