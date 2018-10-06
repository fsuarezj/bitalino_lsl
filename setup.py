import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bitalino_lsl",
    version="0.0.3",
    author="Fernando Suarez Jimenez",
    author_email="fsuarezj@gmail.com",
    description="Python module to stream BITalino data though the Lab Streaming Layer (LSL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fsuarezj/bitalino-lsl",
    packages=setuptools.find_packages(),
    install_requires=[
        'bitalino',
        'future',
        'pylsl',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
