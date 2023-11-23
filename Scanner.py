from FiniteAutomation import FiniteAutomation
from HashTable import HashTable
import re


class Scanner:
    def __init__(self, token_file):
        self.symbol_table = HashTable()
        self.pif = []
        self.tokens = []

        with open(token_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    self.tokens.append(line)

    def scan(self, src_file):
        fa_nc = FiniteAutomation("fa_numeric-const.in")
        fa_id = FiniteAutomation("fa_identifier.in")
        correct = True
        with open(src_file, 'r') as file:
            line_idx = 0
            for line in file:
                line_idx += 1
                line = re.sub('//.*$', '', line).strip()  # Remove comments
                if line:
                    # Splitting by tokens while considering the logical operators and array indexing
                    tokens = re.findall(r'"[^"]*"|[^\s\(\)\[\]{};:=,<>+!\-*\/%]+|\S', line)
                    for token in tokens:
                        if token in self.tokens:
                            self.pif.append((token, -1))
                        elif fa_id.is_accept(token):
                            # Identifiers
                            if not self.symbol_table.contains(token):
                                self.symbol_table.add(token)
                            idx = self.symbol_table.get_position(token)
                            self.pif.append(('id', idx))
                            self.symbol_table.add(token)
                        elif fa_nc.is_accept(token) or re.match(r'^".*"$', token):
                            # Numeric and string constants
                            if not self.symbol_table.contains(token):
                                self.symbol_table.add(token)
                            idx = self.symbol_table.get_position(token)
                            self.pif.append(('constant', idx))
                            self.symbol_table.add(token)
                        elif token in {'or', 'and', 'not'}:
                            self.pif.append((token, -1))
                        else:
                            print(f"lexical error: invalid token {token} on line {line_idx}.")
                            correct = False
        print("lexically correct") if correct else ""

    def write_to_files(self, symbol_file, pif_file):
        with open(symbol_file, 'w') as file:
            file.write('')
            for bucket in self.symbol_table.table:
                if bucket is not None:
                    for value in bucket:
                        file.write(str(value) + ' ')
                    file.write('\n')
                else:
                    file.write('-\n')
        with open(pif_file, 'w') as file:
            file.write('')
            for pair in self.pif:
                file.write(str(pair) + '\n')

    def __str__(self):
        return str(self.pif) + '\n' + str(self.symbol_table)
