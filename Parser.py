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


def read_scanner_output(file_path):
    tokens = []
    with open(file_path, 'r') as file:
        for line in file:
            token_type, token_value = line.strip().strip('()').split(', ')
            tokens.append((token_type.strip("'"), int(token_value)))
    return tokens


def read_symbol_table(file_path):
    symbol_table = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Skip irrelevant lines
            if line.strip() and not line.startswith('-'):
                parts = line.split()
                symbol = parts[0]
                value = ' '.join(parts[1:]).strip('"')  # Remove quotes
                symbol_table[symbol] = value  # Store as string
    return symbol_table


def convert_tokens(scanner_tokens, symbol_table):
    converted_tokens = []
    for token_type, token_value in scanner_tokens:
        if token_type == 'identifier' or token_type == 'constant':
            # Retrieve actual value from symbol table
            actual_value = symbol_table.get(str(token_value))
            if actual_value is not None:
                converted_tokens.append((actual_value, None))
            else:
                # If not found in symbol table, keep the original token
                converted_tokens.append((token_type, token_value))
        else:
            # Directly append other types of tokens
            converted_tokens.append((token_type, None))
    return converted_tokens


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

        parser_output = ParserOutput()
        stack = [0]  # Start state is always 0
        node_stack = []
        input_symbols = input_string.split(" ") + ['$']  # Add end marker
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

                    new_node_id = parser_output.add_node(current_symbol)
                    node_stack.append(new_node_id)
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

                    lhs_node_id = parser_output.add_node(lhs)
                    for _ in range(len(rhs)):
                        child_id = node_stack.pop()
                        parser_output.nodes[child_id]["parent"] = lhs_node_id
                        parser_output.nodes[lhs_node_id]["children"].insert(0, child_id)

                    node_stack.append(lhs_node_id)
                elif action == 'accept':
                    print("The string is accepted by the grammar. \n")
                    print("Parsing tree:")
                    parser_output.display_tree()
                    return parser_output.get_tree()
                else:
                    print(f"Invalid action: {action}")
                    return False
            else:
                print(f"No action defined for state {current_state} and symbol '{current_symbol}'.")
                return False

    def parse_tokens(self, tokens):
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

        print("Starting parsing process...")
        #print("Initial tokens:", tokens[:5])  # Log the first few tokens

        parser_output = ParserOutput()
        stack = [0]  # Start state is always 0
        node_stack = []
        idx = 0  # Pointer to the current token in tokens

        while True:
            current_state = stack[-1]
            current_token = tokens[idx]
            token_type = current_token[0]  # Use the token type for parsing

            print(f"Current state: {current_state}, Current token: {current_token}")  # Logging current state and token

            action_key = (current_state, token_type)

            if action_key in self.action:
                action_tuple = self.action[action_key]
                action = action_tuple[0]
                print(f"Action: {action}")

                if action == 'shift':
                    state = action_tuple[1]
                    stack.append(token_type)  # Push the token type onto the stack
                    stack.append(state)
                    idx += 1  # Move to the next token

                    new_node_id = parser_output.add_node(token_type)
                    node_stack.append(new_node_id)
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

                    # Create a new node for the left-hand side of the production
                    lhs_node_id = parser_output.add_node(lhs)

                    # Link all children to this new node and pop them from the node stack
                    for _ in range(len(rhs)):
                        child_id = node_stack.pop()
                        parser_output.nodes[child_id]["parent"] = lhs_node_id
                        parser_output.nodes[lhs_node_id]["children"].insert(0, child_id)

                    node_stack.append(lhs_node_id)

                elif action == 'accept':
                    print("The string is accepted by the grammar. \n")
                    print("Parsing tree:")
                    parser_output.display_tree()
                    return parser_output.get_tree()
                else:
                    print(f"Invalid action: {action}")
                    return False
            else:
                print(f"No action defined for state {current_state} and symbol '{token_type}'.")
                return False


class ParserOutput:
    def __init__(self):
        self.nodes = []
        self.node_counter = 0

    def add_node(self, symbol, parent=None):
        node = {
            "id": self.node_counter,
            "symbol": symbol,
            "parent": parent,
            "children": []
        }
        self.nodes.append(node)
        self.node_counter += 1
        return node["id"]

    def add_child(self, parent_id, symbol):
        child_id = self.add_node(symbol, parent=parent_id)
        self.nodes[parent_id]["children"].append(child_id)
        return child_id

    def display_tree(self):
        print(f"{'Node':<10}{'Symbol':<10}{'Parent':<10}{'Children':<10}")
        for node in self.nodes:
            children = ', '.join(str(self.nodes[child]["id"]) for child in node["children"])
            parent = node["parent"] if node["parent"] is not None else ''
            print(f"{node['id']:<10}{node['symbol']:<10}{parent:<10}{children:<10}")

    def get_tree(self):
        return self.nodes
