from distutils.core import setup

__packagename__ = "dualprocessing"

def get_version():
    import os, re
    VERSIONFILE = os.path.join(__packagename__, '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError('Unable to find version string in %s.' % (VERSIONFILE,))

__version__ = get_version()

setup(
    name = __packagename__,
    packages = [__packagename__], # this must be the same as the name above
    version = __version__,
    description = 'This module is designed to help with running a single-instance, thread-blocking computation pipeline on a second process. It does all the heavy lifting of scheduling calls and asynchronously waiting for the results.',
    author = 'Michael Osthege',
    author_email = 'thecakedev@hotmail.com',
    url = 'https://github.com/michaelosthege/dualprocessing', # use the URL to the github repo
    download_url = 'https://github.com/michaelosthege/dualprocessing/tarball/%s' % __version__,
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


########### How to upload
# In the command line, navigate to the project directory
# then run
# >>> python setup.py sdist register -r pypi upload -r pypi
# or
# >>> python setup.py sdist register -r pypitest upload -r pypitest

# Make sure to commit with a version-number tag!!
# >>> git tag [versionnumber]
# >>> git push --tags

#### References
# http://peterdowns.com/posts/first-time-with-pypi.html

