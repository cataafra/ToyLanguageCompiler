class TreeNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    def add_child(self, child):
        self.children.append(child)


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
        self.conflicts = []
        augmented_start_symbol = f"{start_symbol}'"
        self.grammar = grammar.copy()
        self.grammar[augmented_start_symbol] = [[start_symbol]]
        self.start_symbol = augmented_start_symbol
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
                    if goto_state in self.states:
                        if symbol in self.grammar:  # Non-terminal
                            self.goto_table[(i, symbol)] = self.states.index(goto_state)
                        else:  # Terminal
                            self.action[(i, symbol)] = ('shift', self.states.index(goto_state))
                elif item.is_complete():
                    if item.lhs == 'S\'':  # Check if the item is from the augmented start rule
                        self.action[(i, '$')] = ('accept',)
                    else:
                        for prod in self.grammar[item.lhs]:
                            if prod == item.rhs:
                                self.action[(i, '$')] = ('reduce', item.lhs, prod)
        for key, value in self.action.items():
            if len(value) > 1:
                self.conflicts.append((key, value))

    def check_conflicts(self):
        if self.conflicts:
            print("Conflicts found in the parsing table:")
            for conflict in self.conflicts:
                print(f"Conflict at {conflict[0]}: {conflict[1]}")
            return True
        return False

    def parse(self, input_string):
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

        stack = [0]
        input_symbols = input_string.split() + ['']
        parse_tree_root = TreeNode("ROOT")
        current_node = parse_tree_root
        node_stack = [current_node]

        while True:
            state = stack[-1]
            symbol = input_symbols[0]
            if (state, symbol) in self.action:
                action = self.action[(state, symbol)]
                if action[0] == 'shift':
                    stack.append(action[1])
                    # Creating a new tree node for the shifted symbol
                    new_node = TreeNode(symbol)
                    current_node.add_child(new_node)
                    node_stack.append(new_node)
                    current_node = new_node
                    input_symbols = input_symbols[1:]
                elif action[0] == 'reduce':
                    # Logic for handling reductions
                    lhs, rhs = action[1], action[2]  # The production being reduced
                    reduce_node = TreeNode(lhs)  # Node for the LHS of the production
                    # Pop the stack for the number of symbols in RHS of the production
                    for _ in range(len(rhs)):
                        stack.pop()
                        node_stack.pop()
                    current_node = node_stack[-1]  # Set current node to the new top of the stack
                    current_node.add_child(reduce_node)  # Add the reduce node to the tree
                    stack.append(self.goto_table[(stack[-1], lhs)])  # Update the state stack
                    node_stack.append(reduce_node)  # Update the node stack
                elif action[0] == 'accept':
                    print("\nSuccessfully parsed.")
                    return parse_tree_root
            else:
                print("\nError in parsing.")
                return


class ParserOutput:
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        self.table = self.build_table()

    def build_table(self):
        table = []

        def traverse(node, parent=None, siblings=None):
            if siblings is None:
                siblings = []
            entry = {'Node': node.symbol, 'Parent': parent.symbol if parent else None,
                     'Siblings': [sib.symbol for sib in siblings]}
            table.append(entry)
            for child in node.children:
                new_siblings = [s for s in node.children if s != child]
                traverse(child, node, new_siblings)

        traverse(self.parse_tree)
        return table

    def print_to_screen(self):
        for row in self.table:
            print(row)

    def print_to_file(self, filename):
        with open(filename, 'w') as file:
            for row in self.table:
                file.write(f"{row}\n")


grammar = {
    'S': [['A']],
    'A': [['a', 'A'], ['b']]
}

parser = LR0Parser(grammar, 'S')
input_string = "a a b"

# Parse the input string to get the parse tree
parse_tree = parser.parse(input_string)

if parse_tree:
    output = ParserOutput(parse_tree)
    output.print_to_screen()
else:
    print("Failed to parse the input string.")
