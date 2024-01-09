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


class LR0Parser:
    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.grammar['S\''] = [[start_symbol]]
        self.start_symbol = 'S\''
        self.states = []
        self.action = {}
        self.goto_table = {}
        self.construct_states()
        self.build_parsing_table()

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
        return self.closure({LR0Item(item.lhs, item.rhs, item.dot + 1) for item in items if item.next_symbol() == symbol})

    def construct_states(self):
        initial_item = LR0Item(self.start_symbol, ['S'], 0)
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


# Example grammar
grammar = {
    'S': [['A', 'A']],
    'A': [['a', 'A'], ['b']]
}

# Initialize parser with the new grammar and start symbol
parser = LR0Parser(grammar, 'S')

# Parse the input string
parser.parse()
