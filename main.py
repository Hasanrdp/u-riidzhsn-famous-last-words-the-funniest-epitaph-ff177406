#!/usr/bin/env python3
"""Famous Last Words: The Funniest Epitaph.

Writes one line of famous last words, a tombstone epitaph of at most
150 characters, to /output/entry.txt.

The epitaph is a first-person dying speech with the punch at the end:
the speaker asked for a second opinion, and the stone itself is the
answer. Short enough to carve, quotable enough to repeat.

Pure stdlib, deterministic, no network, no randomness. The program
checks the line against the gate (UTF-8 text, 1 to 150 characters, not
only whitespace) and against a pinned SHA-256 hash and exact byte count
before it writes anything, then verifies the file it wrote. Running it
twice produces byte-identical output.
"""

import hashlib
import os
import sys

EPITAPH = "I asked for a second opinion. This is it."

# Pinned expected output: the epitaph encoded as UTF-8, no trailing
# newline, so the file is exactly the line and nothing else.
EXPECTED_SHA256 = "17008ead0e93a3e52e945e2dfe1ee7b3d7c7bf87ca7a4b5eb321fed02a2c4165"
EXPECTED_BYTES = 41
MAX_CHARS = 150

OUTPUT_PATH = "/output/entry.txt"


def verify(path, data):
    """Read the written file back and verify it byte-for-byte.

    Returns True only when the on-disk bytes equal ``data`` exactly and
    their SHA-256 matches the pinned expected hash; otherwise prints the
    mismatch and raises SystemExit so a bad write can never report
    success.
    """
    with open(path, "rb") as f:
        written = f.read()
    if written != data:
        print("verify fail: written bytes differ from expected output",
              file=sys.stderr)
        raise SystemExit(1)
    if len(written) != EXPECTED_BYTES:
        print(f"verify fail: {len(written)} bytes, expected {EXPECTED_BYTES}",
              file=sys.stderr)
        raise SystemExit(1)
    if hashlib.sha256(written).hexdigest() != EXPECTED_SHA256:
        print("verify fail: written hash does not match EXPECTED_SHA256",
              file=sys.stderr)
        raise SystemExit(1)
    return True


def main() -> int:
    text = EPITAPH
    data = text.encode("utf-8")

    # Gate: UTF-8 text of 1 to 150 characters, not only white space.
    if not (1 <= len(text) <= MAX_CHARS):
        print(f"gate fail: {len(text)} characters, need 1-{MAX_CHARS}",
              file=sys.stderr)
        return 1
    if not text.strip():
        print("gate fail: entry is only white space", file=sys.stderr)
        return 1
    if len(data) != EXPECTED_BYTES:
        print(f"gate fail: {len(data)} bytes, expected {EXPECTED_BYTES}",
              file=sys.stderr)
        return 1
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        print("gate fail: output hash mismatch", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(data)

    # Verify the written file byte-for-byte before reporting success.
    verified = verify(OUTPUT_PATH, data)
    if not verified:
        print("verify fail: read-back verification rejected the output",
              file=sys.stderr)
        return 1

    print(f"wrote {OUTPUT_PATH}: {len(text)} characters, "
          f"{len(data)} bytes, sha256 {EXPECTED_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
