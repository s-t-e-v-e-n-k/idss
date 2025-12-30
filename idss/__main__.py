import argparse
import logging

from . import __version__
from .idss import IDSS


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"idss {__version__}"
    )
    parser.add_argument(
        "-n",
        "--no-act",
        action="store_true",
        help="do not perform any actions",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="show debug messages",
    )
    return parser


def main():
    args = parser().parse_args()
    if args.no_act:
        return 0
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)
    idss = IDSS()
    idss.process_events()


if __name__ == "__main__":  # pragma: no cover
    main()
