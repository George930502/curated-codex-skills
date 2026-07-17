#!/usr/bin/env python3
"""Print the SHA-256 digest of the exact bytes received on stdin."""

from __future__ import annotations

import hashlib
import sys


def main() -> int:
    digest = hashlib.sha256()
    while chunk := sys.stdin.buffer.read(65_536):
        digest.update(chunk)
    print(digest.hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
