"""Executes pylint"""
from pylint.lint import Run
def main():
    """Executes pylint and validates score"""

    try:
        results = Run(['saltypie'], do_exit=False)
    except TypeError:
        results = Run(['saltypie'], exit=False)
    if results.linter.stats['global_note'] <= 9:
        exit('pylint score must be greater than 9')

main()
