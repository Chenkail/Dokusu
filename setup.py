import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Dokusu",
    version="0.0.1",
    author="Chenkai Luo, Yegor Kuznetsov",
    author_email="author@example.com",
    description="A library for solving Sudoku puzzles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Chenkail/Dokusu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)