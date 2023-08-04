#!/usr/bin/python3

import argparse
import i3ipc
from subprocess import Popen, PIPE
import signal
import sys


def on_window_event(args, process, swallowed_atom):
    def event_listener(_, event):
        process.poll()

        swallowed = swallowed_atom[0]

        if event.change == 'new' and not swallowed:
            focused.command('focus; move scratchpad')
            swallowed_atom[0] = True
            if args.d:
                i3.main_quit()

        elif event.change == 'close' and swallowed:
            focused.command('scratchpad show; floating toggle;')
            sys.exit()

    return event_listener


parser = argparse.ArgumentParser(description="i3-swallow.")
parser.add_argument("-d", action="store_true",
                    help="Don't return window on exit.")
parser.add_argument("cmd", nargs="+", help="Command to be executed")


if __name__ == "__main__":
    args = parser.parse_args()
    i3 = i3ipc.Connection()
    focused = i3.get_tree().find_focused()

    process = Popen(args.cmd, stdout=PIPE)
    process.send_signal(signal.SIGSTOP)

    listener = on_window_event(args, process, [False])

    i3.on("window::new", listener)
    if not args.d:
        i3.on("window::close", listener)

    process.send_signal(signal.SIGCONT)
    i3.main()
