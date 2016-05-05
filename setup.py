"""Setup module"""

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open  # pylint:disable=W0622
from os.path import abspath, dirname, join

from linter.version import __version__

README = join(abspath(dirname(__file__)), 'README.md')
try:
    import pypandoc
    DESCRIPTION = pypandoc.convert(README, 'rst')
except(IOError, ImportError):
    # Get the long description from the README file
    with open(README, encoding='utf-8') as fptr:
        DESCRIPTION = fptr.read()

setup(
    name='LintPlaybook',
    version=__version__,
    description='Lint ansible-playbooks for logical pitfalls',
    long_description=DESCRIPTION,
    url='https://github.com/host-anshu/lint-playbook',
    author='Anshu Choubey',
    author_email='anshu.choubey@imaginea.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='ansible ansible-playbook dry-run lint ansible-lint interceptor',
    packages=find_packages(),
    scripts=['bin/lint-pbook'],
    # test_suite="test"
    install_requires=['SimpleInterceptor==0.1'],
)
