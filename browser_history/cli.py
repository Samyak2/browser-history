"""This module defines functions and globals required for the
command line interface of browser-history."""

import argparse
import sys

from browser_history import (
    browsers,
    generic,
    get_bookmarks,
    get_browsers,
    get_history,
    utils,
)

# get list of all implemented browser by finding subclasses of generic.Browser
AVAILABLE_BROWSERS = ", ".join(b.__name__ for b in get_browsers())
AVAILABLE_FORMATS = ", ".join(generic.Outputs(fetch_type=None).format_map.keys())
AVAILABLE_TYPES = ", ".join(generic.Outputs(fetch_type=None).field_map.keys())


def make_parser():
    """Creates an ArgumentParser, configures and returns it.

    This was made into a separate function to be used with sphinx-argparse

    :rtype: :py:class:`argparse.ArgumentParser`
    """
    parser_ = argparse.ArgumentParser(
        description="""
                    A tool to retrieve history from
                    (almost) any browser on (almost) any platform""",
        epilog="""
                Checkout the GitHub repo
                https://github.com/pesos/browser-history
                if you have any issues or want to help contribute""",
    )

    parser_.add_argument(
        "-t",
        "--type",
        default="history",
        help=f"""
                argument to decide whether to retrieve history or bookmarks.
                Should be one of {AVAILABLE_TYPES}.
                Default is history.""",
    )
    parser_.add_argument(
        "-b",
        "--browser",
        default="all",
        help=f"""
                browser to retrieve history or bookmarks from. Should be one
                of all, {AVAILABLE_BROWSERS}.
                Default is all (gets history or bookmarks from all browsers).
                """,
    )

    parser_.add_argument(
        "-f",
        "--format",
        default="infer",
        help=f"""
            Format to be used in output. Should be one of {AVAILABLE_FORMATS}.
            Default is infer (it tries to infer it from the output file's
            extension. If no output file is given it defaults to csv)""",
    )

    parser_.add_argument(
        "-o",
        "--output",
        default=None,
        help="""
                File where history output or bookmark output is to be written.
                If not provided, standard output is used.""",
    )

    return parser_


parser = make_parser()


def main():
    """Entrypoint to the command-line interface (CLI) of browser-history.

    It parses arguments from sys.argv and performs the appropriate actions.
    """
    args = parser.parse_args()
    h_outputs = b_outputs = None
    fetch_map = {
        "history": {"var": h_outputs, "fun": get_history},
        "bookmarks": {"var": b_outputs, "fun": get_bookmarks},
    }

    if args.type not in fetch_map:
        utils.logger.error(
            "Type %s is unavailable." " Check --help for available types", args.type
        )
        sys.exit(1)

    if args.browser == "all":
        fetch_map[args.type]["var"] = fetch_map[args.type]["fun"]()
    else:
        try:
            # gets browser class by name (string).
            selected_browser = args.browser
            for browser in get_browsers():
                if browser.__name__.lower() == args.browser.lower():
                    selected_browser = browser.__name__
                    break
            browser_class = getattr(browsers, selected_browser)
        except AttributeError:
            utils.logger.error(
                "Browser %s is unavailable." " Check --help for available browsers",
                args.browser,
            )
            sys.exit(1)

        if args.type == "history":
            fetch_map[args.type]["var"] = browser_class().fetch_history()
        elif args.type == "bookmarks":
            fetch_map[args.type]["var"] = browser_class().fetch_bookmarks()

    try:
        if args.output is None:
            if args.format == "infer":
                args.format = "csv"
            print(args.type + ":")
            print(fetch_map[args.type]["var"].formatted(args.format))
        elif args.output is not None:
            fetch_map[args.type]["var"].save(args.output, args.format)

    except ValueError as e:
        utils.logger.error(e)
        sys.exit(1)
