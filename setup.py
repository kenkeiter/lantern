import sys

from setuptools import setup


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

with open('README.md', 'r') as fh:
    readme = fh.read()

if __name__ == '__main__':
    setup(name='yn-lantern',
        version='1.1.0',
        description='A library for communicating with Yongnuo LED video lights.',
        long_description = readme,
        long_description_content_type = 'text/markdown',
        url='https://github.com/kenkeiter/lantern',
        author='Ken Keiter',
        author_email='ken@kenkeiter.com',
        license='MIT',
        packages=['lantern'],
        include_package_data=True,
        keywords = ['video', 'photo', 'lantern', 'light'],
        test_suite='nose.collector',
        tests_require=['nose'],
        install_requires=parse_requirements('requirements.txt'))