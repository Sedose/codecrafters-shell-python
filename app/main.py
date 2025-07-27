import sys


def handle_exit(args):
    try:
        status = int(args[0]) if args else 0
    except ValueError:
        status = 1
    sys.exit(status)


def command_not_found(command):
    print(f"{command}: command not found")


command_handlers = {
    "exit": handle_exit,
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
            handler = command_handlers.get(command, lambda _args: command_not_found(command))
            handler(args)
        except EOFError:
            break


if __name__ == "__main__":
    main()
