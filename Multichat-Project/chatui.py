"""Thread-safe ANSI terminal UI for the chat client.

Incoming messages use a scrolling region above the prompt. Input is read one
character at a time with terminal echo disabled, allowing the prompt and the
partially typed command to be redrawn after every incoming message.
"""

import codecs
import os
import sys
import threading


_output_lock = threading.RLock()
_initialized = False
_reading = False
_prompt = "> "
_input_buffer = []


def init_windows():
    """Initialize the message region and protected input line."""
    global _initialized

    with _output_lock:
        lines = get_terminal_lines()

        buf = clear_screen()
        buf += position_cursor(1, 1)
        buf += set_scrolling_region(1, _message_bottom(lines))
        buf += position_cursor(lines, 1)

        print_now(buf)
        _initialized = True


def read_command(prompt="> "):
    """Read a command without allowing received messages to corrupt it."""
    global _reading, _prompt, _input_buffer

    if not _initialized:
        init_windows()

    with _output_lock:
        _reading = True
        _prompt = prompt
        _input_buffer = []
        _redraw_input()

    try:
        if not sys.stdin.isatty():
            return sys.stdin.readline().strip()

        if os.name == "nt":
            return _read_command_windows()

        return _read_command_posix()

    finally:
        with _output_lock:
            _reading = False
            _clear_input_line()


def print_message(s):
    """Print a received message, then redraw any partially typed command."""
    if not _initialized:
        init_windows()

    # Prevent carriage returns in network data from overwriting output.
    message = str(s).replace("\r\n", "\n").replace("\r", "\n")

    with _output_lock:
        lines = get_terminal_lines()
        bottom = _message_bottom(lines)

        buf = set_scrolling_region(1, bottom)

        for line in message.split("\n"):
            buf += position_cursor(bottom, 1)
            buf += clear_line()
            buf += line
            buf += "\r\n"

        print_now(buf)

        # Terminal echo is disabled while reading, so input is drawn only here
        # and in the input handlers, all while holding the same lock.
        if _reading:
            _redraw_input()
        else:
            print_now(position_cursor(lines, 1))


def end_windows():
    """Restore normal scrolling and leave the terminal in a clean state."""
    global _initialized, _reading

    with _output_lock:
        _reading = False
        lines = get_terminal_lines()

        buf = set_scrolling_region()
        buf += position_cursor(lines, 1)
        buf += clear_line()
        buf += "\n"

        print_now(buf)
        _initialized = False


def _read_command_posix():
    """Read input in cbreak mode on Linux/macOS using only the stdlib."""
    import select
    import termios
    import tty

    fd = sys.stdin.fileno()
    previous_settings = termios.tcgetattr(fd)
    decoder = codecs.getincrementaldecoder("utf-8")("replace")

    try:
        # Disable canonical input and terminal echo. Characters are displayed
        # only by _redraw_input(), under the output lock.
        tty.setcbreak(fd)

        while True:
            byte = os.read(fd, 1)

            if byte in (b"\r", b"\n"):
                return "".join(_input_buffer)

            if byte in (b"\x08", b"\x7f"):
                _backspace()
                continue

            if byte == b"\x03":
                raise KeyboardInterrupt

            if byte == b"\x04":
                if not _input_buffer:
                    return ""
                continue

            if byte == b"\x1b":
                # Discard arrow-key and function-key escape sequences.
                while select.select([fd], [], [], 0.01)[0]:
                    os.read(fd, 1)
                continue

            char = decoder.decode(byte)

            if char and char.isprintable():
                _append_input(char)

    finally:
        termios.tcsetattr(
            fd,
            termios.TCSADRAIN,
            previous_settings,
        )


def _read_command_windows():
    """Read input without echo on Windows using only the stdlib."""
    import msvcrt

    while True:
        char = msvcrt.getwch()

        if char in ("\r", "\n"):
            return "".join(_input_buffer)

        if char in ("\b", "\x7f"):
            _backspace()
            continue

        if char == "\x03":
            raise KeyboardInterrupt

        if char == "\x04" and not _input_buffer:
            return ""

        if char in ("\x00", "\xe0"):
            # The next character is the special-key scan code.
            msvcrt.getwch()
            continue

        if char.isprintable():
            _append_input(char)


def _append_input(char):
    with _output_lock:
        _input_buffer.append(char)
        _redraw_input()


def _backspace():
    with _output_lock:
        if _input_buffer:
            _input_buffer.pop()

        _redraw_input()


def _redraw_input():
    lines = get_terminal_lines()

    buf = set_scrolling_region(1, _message_bottom(lines))
    buf += position_cursor(lines, 1)
    buf += clear_line()
    buf += _prompt
    buf += "".join(_input_buffer)

    print_now(buf)


def _clear_input_line():
    lines = get_terminal_lines()

    buf = position_cursor(lines, 1)
    buf += clear_line()

    print_now(buf)


def print_now(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def get_terminal_lines():
    try:
        return max(3, os.get_terminal_size().lines)
    except OSError:
        return 24


def clear_line():
    return "\x1b[2K"


def clear_screen():
    return "\x1b[2J"


def save_cursor_position():
    return "\x1b7"


def restore_cursor_position():
    return "\x1b8"


def position_cursor(row, col=1):
    return f"\x1b[{row};{col}H"


def set_scrolling_region(line0=None, line1=None):
    if line0 is None:
        return "\x1b[r"

    if line1 is None:
        line1 = line0
        line0 = 1

    return f"\x1b[{line0};{line1}r"


def _message_bottom(lines):
    # Reserve one separator row and one prompt row.
    return max(1, lines - 2)