import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bitalino-lsl",
    version="0.0.1",
    author="Fernando Suárez Jiménez",
    author_email="fsuarezj@gmail.com",
    description="Python module to stream BITalino data though the Lab Streaming Layer (LSL)",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    url="https://github.com/fsuarezj/bitalino-lsl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL3 License",
        "Operating System :: OS Independent",
    ],
)
