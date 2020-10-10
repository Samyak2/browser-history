"""This module defines functions and globals required for the
command line interface of browser-history."""

import sys
import argparse
from browser_history import get_history, get_bookmarks, generic, browsers

# get list of all implemented browser by finding subclasses of generic.Browser
AVAILABLE_BROWSERS = ', '.join(b.__name__ for b in generic.Browser.__subclasses__())
AVAILABLE_FORMATS = ', '.join(generic.Outputs.formats)
AVAILABLE_TYPES='history,bookmarks'

def make_parser():
    """Creates an ArgumentParser, configures and returns it.

    This was made into a separate function to be used with sphinx-argparse

    :rtype: :py:class:`argparse.ArgumentParser`
    """
    parser_ = argparse.ArgumentParser(description='''
                                            A tool to retrieve history from
                                            (almost) any browser on (almost) any platform''',
                                      epilog='''
                                            Checkout the GitHub repo https://github.com/pesos/browser-history
                                            if you have any issues or want to help contribute''')

    parser_.add_argument('-t','--type',
                        default='history',
                        help=f'''
                                argument to decide whether to retrieve history or bookmarks.
                                Should be one of all, {AVAILABLE_TYPES}.
                                Default is history
                                .''')
    parser_.add_argument('-b', '--browser',
                         default='all',
                         help=f'''
                                browser to retrieve history or bookmarks from. Should be one of all, {AVAILABLE_BROWSERS}.
                                Default is all (gets history or bookmarks from all browsers).''')

    parser_.add_argument('-f', '--format',
                         default="csv",
                         help=f'''
                                Format to be used in output. Should be one of {AVAILABLE_FORMATS}.
                                Default is csv''')

    parser_.add_argument('-o', '--output',
                         default=None,
                         help='''
                                File/Folder where history output and/or bookmark output is to be written. 
                                If not provided, standard output is used.''')

    return parser_

parser = make_parser()

def main():
    """Entrypoint to the command-line interface (CLI) of browser-history.

    It parses arguments from sys.argv and performs the appropriate actions.
    """
    args = parser.parse_args()
    assert args.type in ['history','bookmarks','all'], \
                        f"Type should be one of all, {AVAILABLE_TYPES}"

    h_outputs = b_outputs =None
    fetch_map = {'history':[h_outputs ,get_history()],
                 'bookmarks':[b_outputs,get_bookmarks()]}

    if args.browser == 'all':
        fetch_map[args.type][0] = fetch_map[args.type][1]
    else:
        try:
            # gets browser class by name (string).
            selected_browser = args.browser
            for browser in generic.Browser.__subclasses__():
                if browser.__name__.lower() == args.browser.lower():
                    selected_browser = browser.__name__
                    break
            browser_class = getattr(browsers, selected_browser)
        except AttributeError:
            print(f'Browser {args.browser} is unavailable. Check --help for available browsers')
            sys.exit(1)

        try:
            if args.type == 'history':
                fetch_map[args.type][0] = browser_class().fetch_history()
            elif args.type =='bookmarks':
                fetch_map[args.type][0] = browser_class().fetch_bookmarks()
        except AssertionError as e:
            print(e)
            sys.exit(1)

    try:
        if args.output is None:
            print(args.type+':\n')
            print(fetch_map[args.type][0].formatted(args.format,args.type))
        elif not args.output is None:
            with open(args.output, 'w') as output_file:
                output_file.write(fetch_map[args.type][0].formatted(args.format,args.type))

    except ValueError as e:
        print(e)
        sys.exit(1)
