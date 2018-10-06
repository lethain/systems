"""
Tools for formatting lexed tokens into full format.
"""
import sys
import systems.lexer


def main():
    txt = sys.stdin.read()
    lexed = systems.lexer.lex(txt)
    print(systems.lexer.readable(lexed))


if __name__ == "__main__":
    main()
