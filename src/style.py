import json

from pygments import highlight, lexers, formatters


def pprint_dict(data):
    fmt_json = json.dumps(data, indent=4)
    p_json = highlight(fmt_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(p_json)

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
