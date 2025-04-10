from setuptools import setup, find_packages

setup(
    name='notebook-cat',
    version='0.1.0',
    description='Concatenate text, markdown, and JSON files for Google NotebookLM',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='Nazuna',
    author_email='todd@example.com',
    url='https://github.com/Nazuna-io/notebook-cat',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'notebook-cat=notebook_cat.main:main',
        ],
    },
    install_requires=[
        # No external dependencies required beyond standard library
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
    ],
    python_requires='>=3.8',
)
