import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dokusu",
    version="0.0.4",
    author="Chenkai Luo, Yegor Kuznetsov",
    author_email="author@example.com",
    description="A library for solving sudoku puzzles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Chenkail/dokusu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
