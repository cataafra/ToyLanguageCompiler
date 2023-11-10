from Scanner import Scanner

if __name__ == '__main__':
    scanner = Scanner('token.in')
    scanner.scan('p1.txt')
    scanner.write_to_files('st.out', 'pif.out')

