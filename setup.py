from setuptools import setup, find_packages

setup(
    name="mantatools",
    version="0.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    test_suite="tests",
    entry_points={"console_scripts": ["mantatools = mantatools.client:run"]},
    python_requires=">=3.8",
    install_requires=["click", "pysam"],
    author="Michael Knudsen",
    author_email="micknudsen@gmail.com",
)
