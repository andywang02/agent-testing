from setuptools import setup, find_packages

setup(
    name="swarm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "swarm=swarm.main:main",
            "swarm-daemon=swarm.daemon_cli:main",
            "swarm-spawn=swarm.cli_tools:spawn",
        ],
    },
)
