from Scanner import Scanner
from Grammar import FormalGrammar
from Parser import *


if __name__ == '__main__':
    scanner = Scanner('token.in')
    scanner.scan('p0.txt')
    scanner.write_to_files('st.out', 'pif.out')

    gr = FormalGrammar("grammar.in")
    print(gr)

    parser = LR0Parser(gr.productions, gr.start, gr.terminals)

    scanner_tokens = read_scanner_output('pif.out')
    symbol_table = read_symbol_table('st.out')

    converted_tokens = convert_tokens(scanner_tokens, symbol_table)

    parse_tree = parser.parse_tokens(converted_tokens)



