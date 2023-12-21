import subprocess


def generate_grpc_code(file, output="."):
    """Generates grpc code from the specified proto file."""
    command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"-I{output}",
        f"--python_out={output}",
        f"--grpc_python_out={output}",
        file
    ]
    subprocess.run(command, check=True)
