class LR0Item:
    def __init__(self, lhs, rhs, dot):
        self.lhs = lhs  # Left-hand side of the production
        self.rhs = rhs  # Right-hand side of the production
        self.dot = dot  # Position of the dot in the production

    def __repr__(self):
        return f"{self.lhs} -> {' '.join(self.rhs[:self.dot] + ['.'] + self.rhs[self.dot:])}"

    def next_symbol(self):
        return None if self.dot >= len(self.rhs) else self.rhs[self.dot]

    def is_complete(self):
        return self.dot >= len(self.rhs)

    def __eq__(self, other):
        return (self.lhs == other.lhs and self.rhs == other.rhs and self.dot == other.dot)

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot))


class FormalGrammar:
    def __init__(self, filename):
        self.filename = filename
        self.non_terminals = []
        self.terminals = []
        self.productions = {}
        self.start = ''
        self.grammar = {}
        self.states = []
        self.action = {}
        self.goto_table = {}

        self.read_from_file()
        self.transform_grammar()

        self.start_symbol = 'S\''  # Augmented start symbol
        self.grammar[self.start_symbol] = [[self.start]]  # Augmenting the grammar

        self.construct_states()
        self.build_parsing_table()

    def get_all_productions(self, non_terminal):
        return self.productions[non_terminal]

    def __str__(self):
        return "non-terminals: " + str(self.non_terminals) + "\n" \
            + "terminals: " + str(self.terminals) + "\n" \
            + "productions: " + str(self.productions) + "\n" \
            + "start: " + str(self.start) + "\n"

    def is_cfg(self):
        # TODO: check if all values in productions are non-terminals

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
                value = production_str[1].strip()
                if key not in self.productions:
                    self.productions[key] = []
                self.productions[key].append(value)

    def transform_grammar(self):
        transformed_grammar = {}
        for lhs, rhs_list in self.productions.items():
            transformed_rhs = [rhs.split() for rhs in rhs_list]
            transformed_grammar[lhs] = transformed_rhs
        self.grammar = transformed_grammar
        self.grammar['S\''] = [[self.start]]

    def closure(self, items):
        closure = set(items)
        while True:
            new_items = set()
            for item in closure:
                symbol = item.next_symbol()
                if symbol and symbol in self.grammar:
                    for prod in self.grammar[symbol]:
                        new_item = LR0Item(symbol, prod, 0)
                        if new_item not in closure:
                            new_items.add(new_item)
            if not new_items:
                return closure
            closure |= new_items

    def compute_goto(self, items, symbol):
        return self.closure(
            {LR0Item(item.lhs, item.rhs, item.dot + 1) for item in items if item.next_symbol() == symbol})

    def construct_states(self):
        initial_item = LR0Item(self.start_symbol, [self.start], 0)
        self.states.append(self.closure({initial_item}))

        while True:
            new_states = []
            for state in self.states:
                symbols_after_dot = set()
                for item in state:
                    if item.next_symbol():  # Check if there is a symbol after the dot
                        symbols_after_dot.add(item.next_symbol())
                for symbol in symbols_after_dot:
                    goto_state = self.compute_goto(state, symbol)
                    if goto_state not in self.states and goto_state not in new_states:
                        new_states.append(goto_state)
            if not new_states:
                break
            self.states.extend(new_states)

    def build_parsing_table(self):
        for i, state in enumerate(self.states):
            for item in state:
                symbol = item.next_symbol()
                if symbol:
                    goto_state = self.compute_goto(state, symbol)
                    if goto_state in self.states:
                        if symbol in self.grammar:  # Non-terminal
                            self.goto_table[(i, symbol)] = self.states.index(goto_state)
                        else:  # Terminal
                            self.action[(i, symbol)] = ('shift', self.states.index(goto_state))
                elif item.is_complete():
                    if item.lhs == 'S\'':  # Check if the item is from the augmented start rule
                        self.action[(i, '')] = ('accept',)
                    else:
                        for prod in self.grammar[item.lhs]:
                            if prod == item.rhs:
                                self.action[(i, '')] = ('reduce', item.lhs, prod)

    def parse(self):
        # Print the states
        print("States:")
        for i, state in enumerate(self.states):
            print(f"State {i}: {[str(item) for item in state]}")

        # Print the action table
        print("\nAction Table:")
        for key, value in sorted(self.action.items()):
            state, symbol = key
            print(f"State {state}, Symbol '{symbol}': {value}")

        # Print the goto table
        print("\nGoto Table:")
        for key, value in sorted(self.goto_table.items()):
            state, symbol = key
            print(f"State {state}, Symbol '{symbol}': {value}")


gr = FormalGrammar("grammar_simple.in")
print(gr)
print(gr.is_cfg())
gr.parse()