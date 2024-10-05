import sys
import os
import random
import string

if os.name == 'nt':  # If the system is Windows
    import msvcrt
else:  # For Unix-like systems
    import termios
    import tty

def random_char():
    """Generate a random character from printable ASCII letters and digits."""
    return random.choice(string.ascii_letters + string.digits)

def masked_input(prompt):
    """Custom input function that masks the input characters with random characters."""
    if os.name == 'nt':  # Windows
        sys.stdout.write(prompt)
        sys.stdout.flush()
        input_chars = []
        while True:
            char = msvcrt.getch()
            if char == b'\r':  # Enter key (Windows)
                sys.stdout.write('\n')
                break
            elif char == b'\x08':  # Backspace key (Windows)
                if input_chars:
                    input_chars.pop()
                    sys.stdout.write('\b \b')  # Move cursor back, overwrite with space, move back again
            else:
                input_chars.append(char.decode('utf-8'))
                sys.stdout.write(random_char())  # Display a random character
                sys.stdout.flush()
        return ''.join(input_chars)
    else:  # Unix
        sys.stdout.write(prompt)
        sys.stdout.flush()
        input_chars = []
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            while True:
                char = sys.stdin.read(1)
                if char == '\n':  # Enter key (Unix)
                    sys.stdout.write('\n')
                    break
                elif char == '\x7f':  # Backspace key (Unix)
                    if input_chars:
                        input_chars.pop()
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                else:
                    input_chars.append(char)
                    sys.stdout.write(random_char())  # Display a random character
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ''.join(input_chars)

