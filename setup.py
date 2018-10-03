import setuptools

with open("README.md", "r") as fh:
        long_description = fh.read()

        setuptools.setup(
                name="systems",
                version="0.0.3",
                author="Will Larson",
                author_email="lethain@gmail.com",
                description="Describe and run systems diagrams.",
                long_description=long_description,
                long_description_content_type="text/markdown",
                url="https://github.com/lethain/systems",
                packages=setuptools.find_packages(),
                install_requires=[
                        "graphviz",
                ],
                classifiers=[
                        "Programming Language :: Python :: 3",
                        "License :: OSI Approved :: MIT License",
                        "Operating System :: OS Independent",
                ],
                scripts=[
                        "bin/systems-run",
                        "bin/systems-viz",
                ],
        )
