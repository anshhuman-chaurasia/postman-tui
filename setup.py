from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="api-tui",
    version="0.1.0",
    description="A sleek, lightning-fast Terminal API Client.",
    author="Your Name",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "api-tui=app:main",
        ],
    },
)
