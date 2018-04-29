import unittest
import os.path
import pickle
import sys


NGRAM_NUMBER = 6


def _get_meta(meta_path):
    with open(meta_path, 'r') as file_:
        contents = file_.read()

    lines = contents.split('\n')
    return list(map(lambda el: el.split(' '), lines))


def _add_signatures(calls, signatures, label):
    for i in range(len(calls) - NGRAM_NUMBER):
        snext = signatures
        ngram = calls[i: i + NGRAM_NUMBER]
        for call in ngram[:-1]:
            nx = snext.get(call)
            if nx is None:
                nx = {}
                snext[call] = nx
            snext = nx

        st = snext.get(ngram[-1])
        if st is None:
            st = set()
            snext[ngram[-1]] = st

        st.add(label)


def make_signatures(folder_path):
    meta_path = os.path.join(folder_path, 'meta')
    meta = _get_meta(meta_path)

    signatures = {}
    for elem in meta:
        mal_name, label = elem
        filepath = os.path.join(folder_path, f'{mal_name}.trace')

        with open(filepath, 'r') as file_:
            calls = file_.read()

        calls = calls.split('\n')

        _add_signatures(calls, signatures, label)

    return signatures


def main():
    if len(sys.argv) != 2:
        print("usage: makesig <folder_path>")
        print("<folder_path>: path of the folder containing malware traces")
        return

    folder_path = sys.argv[1]
    signatures = make_signatures(folder_path)

    sig_filepath = os.path.join(folder_path, 'signatures')
    with open(sig_filepath, 'wb') as file_:
        pickle.dump(signatures, file_)


if __name__ == '__main__':
    main()


class SigTest(unittest.TestCase):
    def test_add_signature(self):
        calls = list('qwertyuiopasdfghjkl')
        signatures = {}
        _add_signatures(calls, signatures, 'baad')

