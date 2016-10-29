from setuptools import setup

versionfile = 'blackbeard/version.py'
with open(versionfile, 'rb') as f:
    exec(compile(f.read(), versionfile, 'exec'))

setup(
    name='blackbeard',
    version=__version__,  # noqa
    url='https://github.com/tdsmith/blackbeard',
    license='Apache 2.0',
    author='Tim D. Smith',
    author_email='tim@tds.xyz',
    description='An R interpreter in RPython',
    packages=['blackbeard'],
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=['rpython', 'rply', 'typing'],
)
