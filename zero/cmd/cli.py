import argparse
import sys

from zero.cmd.generate_proto import generate_grpc_code


def main():
    """
    zero-grpc command line tool.
    """
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    parser = argparse.ArgumentParser('zero-grpc command line tool')
    parser.add_argument('--verbose', '-v', action='store_true', help='whether to enable detailed output.')

    subparsers = parser.add_subparsers(title='subparsers', dest='subcommand')
    parser_proto = subparsers.add_parser('proto2code', help='proto file generates code')
    parser_proto.add_argument('--file', '-f', help='proto file address')
    parser_proto.set_defaults(func=generate_grpc_code)

    args = parser.parse_args()
    args.func(args)
