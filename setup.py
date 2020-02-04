import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="esportswiki_editing",
    version="0.0.1",
    author="RheingoldRiver",
    author_email="river.esports@gmail.com",
    description="River's wiki tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RheingoldRiver/esportswiki_editing",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['mwclient', 'mwparserfromhell', 'datetime']
)
