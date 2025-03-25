from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="semantic-model-toolkit",
    version="0.1.0",
    author="Snowflake",
    author_email="support@snowflake.com",
    description="A Python library to generate semantic model YAML files for Snowflake databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/semantic-model-toolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "snowflake-connector-python>=3.0.0",
        "PyYAML>=6.0",
        "loguru>=0.6.0",
        "protobuf>=4.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "flake8>=4.0.0",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "all": ["openai>=1.0.0", "anthropic>=0.5.0"],
    },
) 