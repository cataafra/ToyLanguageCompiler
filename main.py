from Scanner import Scanner
from Grammar import FormalGrammar
from Parser import LR0Parser


if __name__ == '__main__':
    scanner = Scanner('token.in')
    scanner.scan('p3.txt')
    scanner.write_to_files('st.out', 'pif.out')

    gr = FormalGrammar("grammar_g4g.in")
    print(gr)

    parser = LR0Parser(gr.productions, gr.start, gr.terminals)
    parser.parse_string("aabb")
