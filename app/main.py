import os
import sys
import subprocess
from pathlib import Path
import shlex


def handle_cd(args) -> None:
    target_path = Path(args[0]).expanduser() if args else Path.home()

    if not target_path.exists():
        print(f"cd: {target_path}: No such file or directory", file=sys.stderr)
        return

    if not target_path.is_dir():
        print(f"cd: {target_path}: Not a directory", file=sys.stderr)
        return

    try:
        os.chdir(target_path)
    except OSError as error:
        print(f"cd: failed to change directory: {type(error).__name__}: {error}", file=sys.stderr)


def handle_pwd(_):
    print(os.getcwd())


def handle_exit(args):
    status = 0
    if args:
        try:
            status = int(args[0])
        except ValueError:
            status = 1
    sys.exit(status)


def handle_echo(args):
    print(" ".join(args))


def find_executable(command):
    for path in os.environ.get("PATH", "").split(":"):
        if not os.path.isdir(path):
            continue
        full_path = os.path.join(path, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None


def handle_type(args):
    if not args:
        return

    cmd = args[0]
    if cmd in command_handlers:
        print(f"{cmd} is a shell builtin")
        return

    path = find_executable(cmd)
    if path:
        print(f"{cmd} is {path}")
    else:
        print(f"{cmd}: not found", file=sys.stderr)


def run_external_command(command, args, stdout_file=None):
    path = find_executable(command)
    if not path:
        print(f"{command}: command not found", file=sys.stderr)
        return

    try:
        if stdout_file:
            subprocess.run([path] + args, stdout=stdout_file)
        else:
            subprocess.run([path] + args)
    except Exception as e:
        print(f"{command}: failed to execute: {e}", file=sys.stderr)


redirection_tokens = {">", "1>"}

def parse_redirection(tokens):
    for i, token in enumerate(tokens):
        if token in redirection_tokens:                     # space-separated form
            if i + 1 == len(tokens):
                print("Error: no file provided for redirection", file=sys.stderr)
                return tokens, None
            return tokens[:i] + tokens[i + 2:], tokens[i + 1]

        m = re.fullmatch(r"(1?>)(.+)", token)               # glued form: >file or 1>file
        if m:
            return tokens[:i] + tokens[i + 1:], m.group(2)

    return tokens, None


command_handlers = {
    "exit": handle_exit,
    "echo": handle_echo,
    "type": handle_type,
    "pwd": handle_pwd,
    "cd": handle_cd,
}


def main():
    while True:
        try:
            line = input("$ ").strip()
            if not line:
                continue
            tokens = shlex.split(line)
        except EOFError:
            sys.exit(0)
        except (ValueError, KeyboardInterrupt):
            continue

        tokens, redir_file = parse_redirection(tokens)
        if not tokens:
            continue

        command, *args = tokens
        if redir_file is None:
            if command in command_handlers:
                command_handlers[command](args)
            else:
                run_external_command(command, args)
            continue

        try:
            with open(redir_file, 'w') as f:
                if command in command_handlers:
                    original_stdout = sys.stdout
                    sys.stdout = f
                    command_handlers[command](args)
                    sys.stdout = original_stdout
                else:
                    run_external_command(command, args, f)
        except OSError as e:
            print(f"Error opening file: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
