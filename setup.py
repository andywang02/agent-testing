from setuptools import setup, find_packages

setup(
    name="aflow",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "aflow=aflow.main:main",
            "aflow-daemon=aflow.daemon_cli:main",
            "aflow-spawn=aflow.cli_tools:spawn",
        ],
    },
)
