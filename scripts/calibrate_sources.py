from __future__ import annotations

import sys

from randomiser.cli.app import main


if __name__ == "__main__":
    raise SystemExit(main(["calibrate", *sys.argv[1:]]))
