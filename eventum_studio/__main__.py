import os
import sys

import streamlit.web.cli as st_cli

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
    os.chdir(BASE_PATH)
    sys.argv = ['streamlit', 'run', STUDIO_ENTRYPOINT, *THEME_OPTIONS]
    exit(st_cli.main())


if __name__ == '__main__':
    main()
