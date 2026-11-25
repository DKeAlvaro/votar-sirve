"""Small editing helper for the site sources.

  python -I scripts/site_edit.py card <card-id> <snippet-file>        replace a card object in docs/assets/content.js
  python -I scripts/site_edit.py before <file> <marker> <snippet-file> insert snippet before a marker line in <file>
  python -I scripts/site_edit.py tldr <snippet-file>                   replace the TLDR constant
"""
import sys

ROOT = __file__.rsplit("scripts", 1)[0]


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    open(p, "w", encoding="utf-8").write(s)


def replace_card(cid, snippet):
    p = ROOT + "docs/assets/content.js"
    s = read(p)
    i = s.index(f'id: "{cid}"')
    a = s.rfind("{", 0, i)
    depth, j, q = 0, a, None
    while j < len(s):
        ch = s[j]
        if q:  # inside a string literal
            if ch == "\\":
                j += 2
                continue
            if ch == q:
                q = None
        elif ch in "\"'`":
            q = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    write(p, s[:a] + read(snippet).strip().rstrip(",") + s[j + 1:])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "card":
        replace_card(sys.argv[2], sys.argv[3])
    elif cmd == "before":
        p, marker, snip = ROOT + sys.argv[2], sys.argv[3], read(sys.argv[4])
        s = read(p)
        k = s.index(marker)
        write(p, s[:k] + snip.rstrip("\n") + "\n" + s[k:])
    elif cmd == "tldr":
        p = ROOT + "docs/assets/content.js"
        s = read(p)
        a = s.index("const TLDR = `")
        b = s.index("`;", a + 14)
        write(p, s[:a] + "const TLDR = `" + read(sys.argv[2]).strip() + s[b:])
    print("ok")
