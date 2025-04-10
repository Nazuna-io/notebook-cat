from setuptools import setup, find_packages

setup(
    name='notebook-cat',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'notebook-cat=notebook_cat.main:main',
        ],
    },
    install_requires=[
        # Dependencies will be added here
    ],
    python_requires='>=3.8',
)
