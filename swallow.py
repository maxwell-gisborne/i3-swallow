#!/usr/bin/python3

import i3ipc

import argparse
from sys import exit

from subprocess import Popen, PIPE
import signal


parser = argparse.ArgumentParser(description="i3-swallow.")
parser.add_argument("-d", action="store_true",
                    help="Don't return window on exit.")
parser.add_argument("cmd", nargs="+", help="Command to be executed")
args = parser.parse_args()


i3 = i3ipc.Connection()
focused = i3.get_tree().find_focused()
swallowed_atom = [False]

process = Popen(args.cmd, stdout=PIPE)
process.send_signal(signal.SIGSTOP)
# The following line is ment to allow the script to call programs
# that do not open an xwindow, and not hang forever waiting for the
# window::close callback. However it seems to brake swallowing for some reason.
# signal.signal(signal.SIGCHLD, lambda *_: None if process.poll() else exit())


def listener(_, event):
    process.poll()

    swallowed = swallowed_atom[0]

    if event.change == 'new' and not swallowed:
        focused.command('focus; move scratchpad')
        swallowed_atom[0] = True
        if args.d:
            i3.main_quit()

    elif event.change == 'close' and swallowed:
        focused.command('scratchpad show; floating toggle;')
        exit()


i3.on("window::new", listener)
if not args.d:
    i3.on("window::close", listener)

process.send_signal(signal.SIGCONT)
i3.main()
