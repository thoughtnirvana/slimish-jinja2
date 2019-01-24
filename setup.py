import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='slimish_jinja',
    version='1.1.1',
    packages=['slimish_jinja'],
    scripts=['slim_to_jinja.py'],
    install_requires=['future', 'jinja2'],
    license='BSD',
    description='Slim templates syntax for Jinja2 templates',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Rahul Kumar',
    url='https://github.com/thoughtnirvana/slimish-jinja2',
    author_email='rahul@thoughtnirvana.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
