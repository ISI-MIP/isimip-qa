import argparse
import re

placeholder_pattern = re.compile(r'^.*?=.*?$')

class ArgumentAction(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        for value in values:
            match = placeholder_pattern.match(value)
            if match:
                try:
                    args.placeholders.append(value)
                except AttributeError:
                    args.placeholders = [value]
            else:
                try:
                    args.paths.append(value)
                except AttributeError:
                    args.paths = [value]
