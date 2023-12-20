import subprocess


def generate_grpc_code(proto_file, output_dir="."):
    """Generates grpc code from the specified proto file."""
    command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"-I{output_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        proto_file
    ]
    subprocess.run(command, check=True)
