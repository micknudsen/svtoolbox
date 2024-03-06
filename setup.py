from setuptools import setup, find_packages

setup(
    name="svtoolbox",
    version="0.1.5",
    packages=find_packages("src"),
    package_dir={"": "src"},
    test_suite="tests",
    entry_points={"console_scripts": ["svtoolbox = svtoolbox.client:run"]},
    python_requires=">=3.10",
    install_requires=["click", "pysam"],
    author="Michael Knudsen",
    author_email="micknudsen@gmail.com",
)
