from Scanner import Scanner
from Grammar import FormalGrammar
from Parser import *


def simple_test():
    gr_simple = FormalGrammar("grammar_g4g.in")
    print(gr_simple)

    parser_simple = LR0Parser(gr_simple.productions, gr_simple.start, gr_simple.terminals)
    parser_simple.parse_string("a a b b")


def complex_test():
    scanner = Scanner('token.in')
    scanner.scan('p0.txt')
    scanner.write_to_files('st.out', 'pif.out')

    gr = FormalGrammar("grammar.in")
    print(gr)

    parser = LR0Parser(gr.productions, gr.start, gr.terminals)

    scanner_tokens = read_scanner_output('pif.out')
    symbol_table = read_symbol_table('st.out')

    converted_tokens = convert_tokens(scanner_tokens, symbol_table)

    parser.parse_tokens(converted_tokens)


if __name__ == '__main__':
    simple_test()
    # complex_test()
