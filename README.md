# Syde

An experimental software to Monitor and detect programs by their system calls.

# Requirements

`Python >3.6`

`strace`

Install python dependencies before using:

`pip install -r requirements.txt`

# Usage

Syde comes with two executable programs:

`syde/sigmaker`: Generate program signatures. Takes one argument,
which is the path to the trace folder. 

```bash
# on the folder where the README.md resides
PYTHONPATH=$PWD python syde/sigmaker traces/genuine

# the program writes the signatures to a file called "signatures" 
# in the given folder.
```

`traces/genuine` folder may be inspected for the expected structure
of the traces folder. 

`syde/main`: Main entry of the program. There are two main commands:
    
* `echo`: Prints the harvested programs in the format understood.
by `sigmaker`
* `monitor`: Executes the program and prints its guesses.

Examples:

```bash

PYTHONPATH=$PWD python syde/main.py echo touch foo
PYTHONPATH=$PWD python syde/main.py --signatures traces/genuine/signatures monitor touch foo

```

# Obtaining Signatures

As mentioned, `echo` command is used to collect traces.

```bash
PYTHONPATH=$PWD python syde/main echo touch foo > traces/genuine/touch.trace
```

After obtaining the traces, a file named `meta` must be created in 
the folder containing the traces. This file is essentially labels
each trace. `sigmaker` reads this file to obtain filenames for
traces, and generates signatures, labeling them accordingly.

The program is developed to aid dynamic analysis of malware; namely to 
identify them through their system calls, but the repo contains
signatures for a couple of standard POSIX tools for the purpose of demonstration.
The contained signatures has been obtained in a Linux machine, it should
work just fine under any Linux distribution, but you probably will need to
collect the traces and build the signatures from scratch if you are using another
POSIX'y operating system, such as FreeBSD.

# Algorithm

An ngram-based approach is utilized. These n-grams are held in a trie
where each symbol is a system call. Assuming we are using 6-grams,
when monitoring, obtained system calls are read by a sliding window
of size 6. These 6 system calls are then used to traverse the trie; this
traversal yields a set of labels. Then, the counter for each respective
label is incremented. If the 6-gram system calls are not recognized, the counter labeled as
"unknown" is incremented. The label which boasts the highest counter is 
yielded as the final decision about the monitored program.

The trie is implemented as nested hashmaps, or "dictionaries" in Python
jargon. Each step in the traversal yields one level deeper hashmap
with the exception of the last one; the last step yields a "set" of
labels.

# Credits

This project has been designed and implemented in collaboration with my most awesome colleagues 
[Julian Zuluaga](github.com/zuliandres) and [Kyle Denney](github.com/kyle-denney).
