def echo(parsed_strace_output: list):
    """
    Given a list of system calls, print them to stdout

    :param parsed_ltrace_output: List of elements of type `Call`.
    :return: nothing
    """
    for entry in parsed_strace_output:
        if entry['type'] == 'call':
            print(entry['call_name'])



