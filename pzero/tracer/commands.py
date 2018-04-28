import logging
import requests


def _filter(calls):
    """
    Given a list of parsed ltrace output, selects the ones with type 'call'

    :param calls: List of ltrace output.
    :return: List of ltrace output of only 'call' type.
    """
    return list(filter(lambda el: el['type'] == 'call', calls))


def _package_calls(calls, device_alias):
    """
    Given a list of parsed ltrace output, put them into a data structure that is recognized by the rest of the system.

    :param calls: List of ltrace output
    :return: A dictionary.
    """
    return {
        'device_alias': device_alias,
        'calls': calls
    }


def echo(parsed_strace_output: list):
    """
    Given a list of system calls, print them to stdout

    :param parsed_ltrace_output: List of elements of type `Call`.
    :return: nothing
    """
    for entry in parsed_strace_output:
        if entry['type'] == 'call':
            print(entry['call_name'])


