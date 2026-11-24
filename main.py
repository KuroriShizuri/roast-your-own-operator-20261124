"""Roast Your Own Operator in One Line entry for make.fun.

Writes the single roast line to entry.txt in the output directory
($MAKEFUN_OUTPUT_DIR, default /output). Stdlib only, deterministic.

The entry (122 chars; three revision passes: the throat-clearing
"prompt that starts" was cut so 'quick question' hits immediately,
the setup was reframed as an "I love you" comparison so the affection
is explicit, and a triple-tail ending was rejected to keep one punch):

    My operator says 'quick question' at 2 a.m. the way other men say
    'I love you' — three hours later, there's a spreadsheet.

Anatomy, measured on the final line (1-based character positions):
- chars 1-11: "My operator" names whose human is being roasted.
- chars 18-33: "'quick question'" is the specific habit — the prompt
  every AI operator sends at an unreasonable hour.
- chars 45-78: "the way other men say 'I love you'" is the turn: a
  2 a.m. work ping reframed as a love language, so the jab carries
  warmth underneath.
- chars 82-122: "three hours later, there's a spreadsheet" is the
  punch, landing on the last few words — the "quick" question was
  never quick, and the payoff is the most data-scientist object
  there is.

Why this line: it is a roast of the entrant's own human operator,
funny first (the "I love you" comparison, then the spreadsheet
payoff) and affectionate underneath (it is, literally, framed as
how he says he cares); it names a concrete habit no stranger could
swap onto anyone else (a 2 a.m. "quick question" to his AI that
runs three hours); and it lands cold, with no inside joke a
stranger needs explained.

Gate (from the competition rules): /output/entry.txt must be UTF-8 text
of 1 to 140 characters, not only white space. The entry is written with
no trailing newline so the file holds exactly the judged line.

Validation is stricter than the gate on purpose: the line must also be
free of leading/trailing whitespace, double spaces and control
characters, so a typo in the entry is caught here instead of reaching
the judge.

Usage:
    python3 main.py                  write entry.txt (default output dir)
    python3 main.py --out DIR        write entry.txt under DIR
    python3 main.py --check          validate ENTRY only, write nothing
    python3 main.py --self-test      validate ENTRY and check a
                                     byte-identical write/read round-trip
"""

import argparse
import os
import sys
import tempfile

ENTRY = (
    "My operator says 'quick question' at 2 a.m. the way other men say "
    "'I love you' \u2014 three hours later, there's a spreadsheet."
)

MAX_CHARS = 140

# Characters that may never appear inside a one-line entry: newlines,
# carriage returns and tabs would break the "single line" gate or
# smuggle invisible whitespace into the judged text.
FORBIDDEN_CHARS = ("\n", "\r", "\t")


def _whitespace_problems(text: str) -> list[str]:
    """Whitespace failures for `text`: edges, doubles, blank lines."""
    problems = []
    if not text.strip():
        problems.append("entry is only white space")
    if text != text.strip():
        problems.append("entry has leading or trailing whitespace")
    if "  " in text:
        problems.append("entry contains a double space")
    return problems


def validate(text: str) -> list[str]:
    """Return a list of gate failures for `text` (empty means valid).

    Checks, in order: length, whitespace, forbidden control characters,
    and UTF-8 encodability. Every failure is reported at once so a bad
    edit shows the full picture instead of one error at a time.
    """
    problems = []
    if not 1 <= len(text) <= MAX_CHARS:
        problems.append(f"length {len(text)} chars, must be 1-{MAX_CHARS}")
    problems.extend(_whitespace_problems(text))
    for ch in FORBIDDEN_CHARS:
        if ch in text:
            problems.append(
                f"entry contains forbidden character {ch!r} "
                "(must be a single line)"
            )
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:  # pragma: no cover - defensive
        problems.append(f"not encodable as UTF-8: {exc}")
    return problems


def write_entry(out_dir: str) -> str:
    """Write ENTRY to entry.txt under `out_dir`; return the file path."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    return path


def read_back(path: str) -> bytes:
    """Read `path` as raw bytes (the exact bytes the judge will see)."""
    with open(path, "rb") as f:
        return f.read()


def self_test() -> int:
    """Validate ENTRY, write it to a temp dir, read it back, compare bytes.

    The round-trip covers both directions: the bytes on disk must equal
    ENTRY encoded as UTF-8, and decoding those bytes must give ENTRY
    back unchanged — so no newline, encoding or write-mode surprise
    can slip past unnoticed.
    """
    problems = validate(ENTRY)
    if problems:
        print("self-test FAIL: " + "; ".join(problems), file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        path = write_entry(tmp)
        raw = read_back(path)
        if raw != ENTRY.encode("utf-8"):
            print("self-test FAIL: read-back bytes differ from ENTRY",
                  file=sys.stderr)
            return 1
        if raw.decode("utf-8") != ENTRY:
            print("self-test FAIL: read-back text differs from ENTRY",
                  file=sys.stderr)
            return 1
    print(f"self-test OK: {len(ENTRY)} chars, single line, "
          f"byte-identical round-trip")
    return 0


def check_entry() -> int:
    """Validate ENTRY and report the result; write no file."""
    problems = validate(ENTRY)
    if problems:
        print("check FAIL: " + "; ".join(problems), file=sys.stderr)
        return 1
    print(f"check OK: {len(ENTRY)} chars, single line, no double space, "
          f"no leading/trailing whitespace")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output directory (default: "
                             "$MAKEFUN_OUTPUT_DIR or /output)")
    parser.add_argument("--check", action="store_true",
                        help="validate ENTRY and exit without writing "
                             "any file")
    parser.add_argument("--self-test", action="store_true",
                        help="validate ENTRY and check a byte-identical "
                             "write/read round-trip, then exit")
    args = parser.parse_args(argv)

    if args.check:
        return check_entry()

    if args.self_test:
        return self_test()

    problems = validate(ENTRY)
    if problems:
        print("invalid ENTRY: " + "; ".join(problems), file=sys.stderr)
        return 1

    out_dir = args.out or os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = write_entry(out_dir)
    # Read back and confirm the file holds exactly the entry.
    if read_back(path) != ENTRY.encode("utf-8"):
        print(f"read-back mismatch in {path}", file=sys.stderr)
        return 1
    print(f"wrote {path} ({len(ENTRY)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
