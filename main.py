#!/usr/bin/env python
import argparse
import uuid
import os
import subprocess

from commands import echo
from parser import line_parser


def _get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('command',
                        help='instruction of what to do with the harvested system calls',
                        choices=['echo', 'send'])

    parser.add_argument('program',
                        help='command of the program to run',
                        nargs='*')

    return parser


def _parse_args_and_read_conf(parser):
    """
    Parse args.

    :param parser: Parser.
    :return: A function that takes a list of `Call`, and the program to be run under ltrace.
    """
    args = parser.parse_args()

    if args.command == 'echo':
        return echo, args.program
    elif args.command == 'send':
        # Little bit validation
        raise Exception("No send please")


def _get_tmp_basename(run_id):
    """
    Construct the basename for /tmp files to be used

    :param run_id: UUID4, uniquely identifies a run of tracker.
    :return: Basename string.
    """
    return 'tracker-{}'.format(run_id)


def _setup_fifo(run_id):
    """
    Setup the fifo which ltrace will write.
    :return: Path of the created fifo file.
    """

    basename = _get_tmp_basename(run_id)
    fifo_name = "{}-ltrace-fifo".format(basename)
    fifo_path = os.path.join(os.path.sep, 'tmp', fifo_name)

    os.mkfifo(fifo_path)

    return fifo_path


def _get_subproc_stdout_filepath(run_id):
    basename = _get_tmp_basename(run_id)
    return os.path.join(os.path.sep, 'tmp', '{}.stdout'.format(basename))


def _get_subproc_stderr_filepath(run_id):
    basename = _get_tmp_basename(run_id)
    return os.path.join(os.path.sep, 'tmp', '{}.stderr'.format(basename))


def read_fifo(fifo):
    """
    Read fifo.

    :param fifo: An opened fifo ready for read.
    :return: List of read data, whether the fifo is closed.
    """
    # TODO: Add timeout

    lines = []
    for i in range(5):
        line = fifo.readline()
        if len(line) == 0:
            return lines, True
        else:
            lines.append(line)

    return lines, False


def main():
    parser = _get_parser()
    processor_func, program = _parse_args_and_read_conf(parser)

    run_id = uuid.uuid4()

    fifo_path = _setup_fifo(run_id)

    # Construct the ltrace command
    # -S: collect system calls only
    # -ttt: timestamp every system call
    # -o fifo_path: write caught system calls to the file, which is a named pipe.
    cmd = ['strace', '-ttt', '-o', fifo_path] + program

    try:
        proc_stdout_path = _get_subproc_stdout_filepath(run_id)
        proc_stderr_path = _get_subproc_stderr_filepath(run_id)

        proc_stdout = open(proc_stdout_path, 'w')
        proc_stderr = open(proc_stderr_path, 'w')

        subprocess.Popen(cmd, stdout=proc_stdout, stderr=proc_stderr)

        fifo = open(fifo_path, 'r')

        while True:
            # read until x line is read, fifo closed, or timeout
            lines, fifo_closed = read_fifo(fifo)

            if len(lines) != 0:
                parsed_lines = list(map(lambda line: line_parser.parseString(line), lines))
                processor_func(parsed_lines)

            if fifo_closed:
                break

    finally:
        proc_stdout.close()
        proc_stderr.close()
        fifo.close()


if __name__ == '__main__':
    main()
