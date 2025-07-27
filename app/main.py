import os
import sys
import subprocess


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


def handle_type(args):
    if not args:
        return

    command = args[0]

    if command in command_handlers:
        print(f"{command} is a shell builtin")
        return

    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(":"):
        if not os.path.isdir(directory):
            continue
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            print(f"{command} is {full_path}")
            return

    print(f"{command}: not found")


def run_external_command(command, args):
    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(":"):
        if not os.path.isdir(directory):
            continue
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            try:
                subprocess.run([command, *args], executable=full_path)
            except Exception:
                print(f"{command}: failed to execute")
            return
    print(f"{command}: command not found")


def command_not_found(command):
    print(f"{command}: command not found")


command_handlers = {
    "exit": handle_exit,
    "echo": handle_echo,
    "type": handle_type,
    "pwd": handle_pwd,
}


def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            line = input()
            if not line:
                continue
            parts = line.split()
            command, args = parts[0], parts[1:]
            handler = command_handlers.get(command)
            if handler:
                handler(args)
            else:
                run_external_command(command, args)
        except EOFError:
            break


if __name__ == "__main__":
    main()
