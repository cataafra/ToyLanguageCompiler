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
    def __init__(self, grammar, start_symbol, terminals):
        self.conflicts = []
        augmented_start_symbol = f"{start_symbol}'"
        self.grammar = grammar.copy()
        self.grammar[augmented_start_symbol] = [[start_symbol]]
        self.start_symbol = augmented_start_symbol
        self.terminals = terminals
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
        return self.closure(
            {LR0Item(item.lhs, item.rhs, item.dot + 1) for item in items if item.next_symbol() == symbol})

    def construct_states(self):
        initial_item = LR0Item(self.start_symbol, [self.grammar[self.start_symbol][0][0]], 0)
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
        self.conflicts = []
        for i, state in enumerate(self.states):
            for item in state:
                symbol = item.next_symbol()
                if symbol:
                    goto_state = self.compute_goto(state, symbol)
                    action_key = (i, symbol)
                    if goto_state in self.states:
                        if symbol in self.grammar:  # Non-terminal
                            self.goto_table[action_key] = self.states.index(goto_state)
                        else:  # Terminal
                            action_value = ('shift', self.states.index(goto_state))
                            if action_key in self.action:
                                if self.action[action_key] != action_value:
                                    self.conflicts.append((action_key, self.action[action_key], action_value))
                            else:
                                self.action[action_key] = action_value
                elif item.is_complete():
                    action_key = (i, '$')
                    if item.lhs == 'S\'':
                        action_value = ('accept',)
                    else:
                        action_value = ('reduce', item.lhs, item.rhs)
                    if action_key in self.action:
                        if self.action[action_key] != action_value:
                            self.conflicts.append((action_key, self.action[action_key], action_value))
                    else:
                        self.action[action_key] = action_value

                    action_key = (i, '$')
                    if not item.lhs == 'S\'':
                        for symbol in self.terminals:
                            action_key = (i, symbol)
                            action_value = ('reduce', item.lhs, item.rhs)
                            if action_key in self.action:
                                if self.action[action_key] != action_value:
                                    self.conflicts.append((action_key, self.action[action_key], action_value))
                            else:
                                self.action[action_key] = action_value

        if self.conflicts:
            print("Conflicts found in the parsing table:")
            for conflict in self.conflicts:
                state, symbol, actions = conflict
                print(f"Conflict in state {state} on symbol '{symbol}': {actions}")
            print("The grammar is not LR(0).")

    def check_conflicts(self):
        if self.conflicts:
            print("Conflicts found in the parsing table:")
            for conflict in self.conflicts:
                print(f"Conflict at {conflict[0]}: {conflict[1]}")
            return True
        return False

    def parse_string(self, input_string):
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

        stack = [0]  # Start state is always 0
        input_symbols = list(input_string) + ['$']  # Add end marker
        idx = 0  # Pointer to the current symbol in input_string

        while True:
            current_state = stack[-1]
            current_symbol = input_symbols[idx]
            action_key = (current_state, current_symbol)

            if action_key in self.action:
                action_tuple = self.action[action_key]
                action = action_tuple[0]

                if action == 'shift':
                    state = action_tuple[1]
                    stack.append(current_symbol)
                    stack.append(state)
                    idx += 1  # Move to the next symbol in the input string
                elif action == 'reduce':
                    lhs = action_tuple[1]
                    rhs = action_tuple[2]
                    # Pop the stack twice the length of the right-hand side of the production
                    for _ in range(2 * len(rhs)):
                        stack.pop()
                    # Push the left-hand side of the production onto the stack
                    top_state = stack[-1]
                    stack.append(lhs)
                    goto_state = self.goto_table[(top_state, lhs)]
                    stack.append(goto_state)
                elif action == 'accept':
                    print("The string is accepted by the grammar.")
                    return True
                else:
                    print(f"Invalid action: {action}")
                    return False
            else:
                print(f"No action defined for state {current_state} and symbol '{current_symbol}'.")
                return False


# grammar = {
#     'S': [['A', 'A']],
#     'A': [['a', 'A'], ['b']]
# }
#
# parser = LR0Parser(grammar, 'S', ['a', 'b'])
# parser.parse_string("bb")

