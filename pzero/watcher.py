import unittest

from pzero.sigmaker import NGRAM_NUMBER
from pzero.sigmaker import traverse
from pzero.sigmaker import _add_signatures


class Watcher:
    # backlog buffer
    # statistics of predictions
    def __init__(self, signatures):
        self._signatures = signatures

        self._backlog = []
        self._stats = {'unknown': 0}
        self._total_predictions = 0

    def update(self, parsed_strace_calls: list):
        if len(self._backlog) + len(parsed_strace_calls) < NGRAM_NUMBER:
            self._backlog += parsed_strace_calls
            return

        scalls = list(filter(lambda el: el['type'] == 'call', parsed_strace_calls))
        scalls = list(map(lambda el: el['call_name'], scalls))

        scalls = self._backlog + scalls

        for i in range(len(scalls) - NGRAM_NUMBER + 1):
            window = scalls[i:i+NGRAM_NUMBER]
            labels = traverse(self._signatures, window)

            if labels == set():
                self._stats['unknown'] += 1

            for label in list(labels):
                self._stats[label] = self._stats.get(label, 0) + 1

            self._total_predictions += 1

        self._backlog = scalls[-NGRAM_NUMBER:]

    def report(self):
        if self._total_predictions == 0:
            return ''

        top_5 = self._top_5()
        strs = list(map(lambda el: '{}:\t%{:.2f}'.format(el[0], el[1]), top_5))
        return '\n'.join(strs)

    def _top_5(self):
        keys = list(self._stats)

        vals = []
        for key in keys:
            vals.append(self._stats[key])

        sum_vals = sum(vals)
        vals = list(map(lambda el: (el/sum_vals) * 100, vals))

        tups = []
        for i in range(len(vals)):
            tups.append((keys[i], vals[i]))

        tups.sort(key=lambda el: el[1])
        tups.reverse()
        return tups[:5]


def monitor(watcher, calls):
    watcher.update(calls)

    report = watcher.report()
    if report != '':
        print(report)


class Tests(unittest.TestCase):
    def test_update_1(self):
        calls = list('qwertyuiopasdfghjkl')
        signatures = {}
        _add_signatures(calls, signatures, 'baad')

        watcher = Watcher(signatures)

        calls = list('qwerty')
        calls = list(map(lambda el: {'type': 'call', 'call_name': el}, calls))

        watcher.update(calls)

        self.assertEqual(watcher._stats, {'baad': 1, 'unknown': 0})
        self.assertEqual(watcher._backlog, list('qwerty'))
        self.assertEqual(watcher._total_predictions, 1)

    def test_update_2(self):
        calls = list('qwertyuiopasdfghjkl')
        signatures = {}
        _add_signatures(calls, signatures, 'baad')

        watcher = Watcher(signatures)

        calls = list('asdfsd')
        calls = list(map(lambda el: {'type': 'call', 'call_name': el}, calls))

        watcher.update(calls)

        self.assertEqual(watcher._stats, {'unknown': 1})
        self.assertEqual(watcher._backlog, list('asdfsd'))
        self.assertEqual(watcher._total_predictions, 1)

    def test_update_3(self):
        calls = list('qwertyuiopasdfghjkl')
        signatures = {}
        _add_signatures(calls, signatures, 'baad')
        _add_signatures(calls, signatures, 'good')

        watcher = Watcher(signatures)

        calls = list('qwerty')
        calls = list(map(lambda el: {'type': 'call', 'call_name': el}, calls))

        watcher.update(calls)

        self.assertEqual(watcher._stats, {'unknown': 0, 'baad': 1, 'good': 1})
        self.assertEqual(watcher._backlog, list('qwerty'))
        self.assertEqual(watcher._total_predictions, 1)

    def test_top_5(self):
        watcher = Watcher({})
        watcher._stats = {'a': 10, 'b': 20, 'c': 30}
        watcher._total_predictions = 5

        expected = [('c', 30/60 * 100), ('b', 20/60 * 100), ('a', 10/60 * 100)]
        received = watcher._top_5()

        self.assertEqual(expected, received)

    def test_report(self):
        watcher = Watcher({})
        watcher._stats = {'a': 10, 'b': 20, 'c': 30}
        watcher._total_predictions = 5

        print('report returns:')
        print(watcher.report())

