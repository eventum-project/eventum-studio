import argparse
import os
import sys
from importlib.metadata import version

import streamlit.web.cli as st_cli

VERSION = version('eventum_studio')
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
STUDIO_ENTRYPOINT = os.path.join(BASE_PATH, '01_Time_distribution.py')

THEME_OPTIONS = [
    '--theme.primaryColor=#8282ef',
    '--theme.backgroundColor=#181818',
    '--theme.secondaryBackgroundColor=#252526',
    '--theme.textColor=#e3e3e3',
]


def main() -> None:
    """Execute command to run streamlit app."""
    argparser = argparse.ArgumentParser(
        prog='eventum-studio',
        description='Content designer for Eventum',
        epilog='Documentation: https://eventum-generatives.github.io/Website/',
    )
    argparser.add_argument(
        '-V', '--version',
        action='version',
        version=f'eventum-studio {VERSION}'
    )
    argparser.parse_args()

    os.chdir(BASE_PATH)
    sys.argv = ['streamlit', 'run', STUDIO_ENTRYPOINT, *THEME_OPTIONS]
    exit(st_cli.main())


if __name__ == '__main__':
    main()
