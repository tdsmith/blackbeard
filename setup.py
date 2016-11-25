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
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Other Scripting Engines',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    install_requires=['rpython', 'rply', 'typing'],
    entry_points={'console_scripts': [
        'bblex=blackbeard.lexer:main',
        'bbparse=blackbeard.parser:main',
    ]}
)
