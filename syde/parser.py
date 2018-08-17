import unittest

from pyparsing import Word, alphanums, nums, Combine, ParseException, Literal, Or


def _call_act(original_string, location, tokens):
    """
    Called when a newly made call is parsed. On succh an event, sets the line type as 'call'.
    """
    tokens['type'] = 'call'


def _exit_remark_act(original_string, location, tokens):
    """
    Called when an exit remark is parsed. On such an event, sets the line type as 'exit' .
    """
    tokens['type'] = 'exit'


def _func_resume_act(original_string, location, tokens):
    """
    Called when a 'resume' line is parsed. On such an event, sets the line type as 'resume'.
    """
    tokens['type'] = 'resume'


microsec_timestamp = Combine(Word(nums) + '.' + Word(nums))\
    .setResultsName('unix_timestamp')\
    .setParseAction(lambda s, l, t: float(t[0]))

call_name = Word(alphanums + '_') \
    .setResultsName('call_name')

new_call = call_name.setParseAction(_call_act)

resume = Literal('<... ') + call_name + Literal('resumed>')
resume = resume.setParseAction(_func_resume_act)

exit_remark = \
    Literal('+++ exited with ') + \
    Word(nums) \
        .setResultsName('exit_code') \
        .setParseAction(lambda s, l, t: int(t[0])) + \
    Literal('+++')
exit_remark = exit_remark.setParseAction(_exit_remark_act)

line_parser = microsec_timestamp + (new_call ^ resume ^ exit_remark)


class ParserTests(unittest.TestCase):
    def test_parse_regular_input(self):
        """parser is able to parse a line of strace output and put set timestamp and call_name fields appropriately"""

        instr = '1510617255.621613 free(0)                            = <void>'

        result = line_parser.parseString(instr)
        result_dict = result.asDict()

        expected_dict = {
            'unix_timestamp': 1510617255.621613,
            'type': 'call',
            'call_name': 'free'
        }

        self.assertEqual(expected_dict, result_dict)

    def test_parse_exit(self):
        """parser is able to parse exit remark"""

        instr = '1510617255.621613 +++ exited (status 123) +++'

        result = line_parser.parseString(instr)
        result_dict = result.asDict()

        expected_dict = {
            'unix_timestamp': 1510617255.621613,
            'type': 'exit',
            'exit_code': 123
        }

        self.assertEqual(expected_dict, result_dict)

    def test_parse_resume(self):
        """parser is able to parse a 'resume' indicator."""

        instr = '1510622447.180887 <... malloc resumed> )         = 0x10f1010'

        result = line_parser.parseString(instr)
        result_dict = result.asDict()

        expected_dict = {
            'unix_timestamp': 1510622447.180887,
            'type': 'resume',
            'call_name': 'malloc'
        }

        self.assertEqual(expected_dict, result_dict)

    def test_exception_on_bad_input(self):
        """parser throws an exception in case it doesn't start with timestamp."""

        # instr must be any string that doesn't start with a digit
        instr = 'cslfiu'

        with self.assertRaises(ParseException):
            line_parser.parseString(instr)

