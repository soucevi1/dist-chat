from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = ''.join(f.readlines())


setup(
    name='soucevi1_dist_chat',
    version='0.1.2',
    packages=find_packages(),
    url='https://github.com/soucevi1/dist-chat',
    author='Vit Soucek',
    author_email='soucevi1@fit.cvut.cz',
    description='Distributed chat based on Chang-Roberts algorithm',
    long_description=long_description,
    keywords='chat,Chang-Roberts,distributed',
    license='Public Domain',
    classifiers=[
        'Topic :: Communications :: Chat',
        'Topic :: System :: Distributed Computing',
        'Intended Audience :: Education',
        'License :: Public Domain',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'soucevi1_dist_chat = soucevi1_dist_chat.cli:main',
        ]
    },
    install_requires=[
        'click',
        'setuptools',
        'prompt_toolkit',
    ]
)
