import os
import sys
import subprocess
from pathlib import Path
import shlex

def handle_cd(args) -> None:
    target_path = Path(args[0]).expanduser() if args else Path.home()

    if not target_path.exists():
        print(f"cd: {target_path}: No such file or directory")
        return

    if not target_path.is_dir():
        print(f"cd: {target_path}: Not a directory")
        return

    try:
        os.chdir(target_path)
    except OSError as error:
        print(f"cd: failed to change directory: {type(error).__name__}: {error}")


def handle_pwd(args):
    print(os.getcwd())


def handle_exit(args):
    try:
        status = int(args[0]) if args else 0
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
    if args[0] in command_handlers:
        print(f"{args[0]} is a shell builtin")
        return
    if path := find_executable(args[0]):
        print(f"{args[0]} is {path}")
    else:
        print(f"{args[0]}: not found")


def run_external_command(command, args):
    if path := find_executable(command):
        try:
            subprocess.run([command, *args], executable=path)
        except Exception:
            print(f"{command}: failed to execute")
    else:
        print(f"{command}: command not found")


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
            line = input("$ ")
            tokens = shlex.split(line, posix=True)
            if not tokens:
                continue
            command, *args = tokens
        except EOFError:
            break
        except ValueError:
            continue

        if handler := command_handlers.get(command):
            handler(args)
        else:
            run_external_command(command, args)


if __name__ == "__main__":
    main()
