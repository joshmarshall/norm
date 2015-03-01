from setuptools import setup, find_packages

with open("VERSION") as version_fp:
    VERSION = version_fp.read().strip()

setup(
    name="normdb",
    description="Database-agnostic model and storage library",
    author="Josh Marshall",
    author_email="catchjosh@gmail.com",
    url="https://github.com/joshmarshall/norm",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    version=VERSION,
    packages=find_packages(exclude=["tests", "dist"]),
    install_requires=["interfaces"]
)
