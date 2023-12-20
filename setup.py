from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()


def get_version() -> str:
    from zero import version
    return version.__version__


setup(
    name='zero-grpc',
    version=get_version(),
    author='Ethan',
    author_email='cheerxiong0823@163.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xccx0823/zero-grpc",
    description='zero-grpc is a grpc web framework implemented in python.',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
