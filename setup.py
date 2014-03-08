import setuptools

with open("VERSION") as version_fp:
    VERSION = version_fp.read().strip()

setuptools.setup(
    name="norm",
    description="Database-agnostic model and storage library",
    author="Josh Marshall",
    author_email="catchjosh@gmail.com",
    url="https://github.com/joshmarshall/norm",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    version=VERSION,
    packages=["norm", "norm.backends"])
