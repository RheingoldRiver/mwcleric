import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

__version__ = "0.10.4"

setuptools.setup(
    name="mwcleric",
    version=__version__,
    author="RheingoldRiver",
    author_email="river.esports@gmail.com",
    description="River's mwclient wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RheingoldRiver/mwcleric",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['mwparserfromhell', 'pytz', 'mwclient>=0.10.1']
)
