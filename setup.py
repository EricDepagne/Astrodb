from setuptools import setup, find_packages

setup(
    name='Astrodb',
    version=__import__('astrodb').__version__,
    description=__import__('astrodb').__doc__,
    long_description=open('README.rst').read(),
    author='Eric Depagne',
    author_email='eric@depagne.org',
    url='https://github.com/EricDepagne/Astrodb',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'astropy==0.4.2',
        'psycopg2==2.4.5',
    ],
    entry_points={
        'console_scripts': [
            'astrodb = astrodb.console_script:cli_frontend',
        ]
    },
    include_package_data=True,
    zip_safe=False
)