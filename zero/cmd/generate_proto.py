import subprocess


def generate_grpc_code(args):
    """
    Generates grpc code from the specified proto file.
    """
    file = args.file
    if not file:
        example_command = "\033[93mzero proto --file=example.proto\033[0m"
        print(f"\n\033[91mwarning: you must be set --file, like {example_command}\033[0m")
        return

    output = args.out or '.'
    command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"-I{output}",
        f"--python_out={output}",
        f"--grpc_python_out={output}",
        file
    ]
    subprocess.run(command)
