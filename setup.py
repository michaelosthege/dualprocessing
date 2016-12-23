from distutils.core import setup
setup(
    name = 'dualprocessing',
    packages = ['dualprocessing'], # this must be the same as the name above
    version = '0.1',
    description = 'This module is designed to help with running a single-instance, thread-blocking computation pipeline on a second process. It does all the heavy lifting of scheduling calls and asynchronously waiting for the results.',
    author = 'Michael Osthege',
    author_email = 'thecakedev@hotmail.com',
    url = 'https://github.com/michaelosthege/dualprocessing', # use the URL to the github repo
    download_url = 'https://github.com/michaelosthege/dualprocessing/tarball/0.1',
    keywords = ['multiprocessing'], # arbitrary keywords
    license = 'MIT',
    classifiers= [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: Developers"
    ]
)
