from distutils.core import setup

setup(
    name='fixtable',  # How you named your package folder (MyLib)
    packages=['fixtable'],  # Chose the same as "name"
    version=
    '0.5',  # Start with a small number and increase it with every change you make
    license=
    'MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description=
    'Fix outreg2 table from stata',  # Give a short description about your library
    author='Leo Liu',  # Type in your name
    author_email='auleo.liu@gmail.com',  # Type in your E-Mail
    url= 'https://github.com/leoliu0/fixtable',  # Provide either the link to your github or to your website
    download_url= 'https://github.com/leoliu0/fixtable/archive/refs/tags/v0.5.tar.gz',
    #  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
    #  install_requires=[
    #  'validators',
    #  'beautifulsoup4',
    #  ],
    scripts=['fixtable/fixtable'],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
