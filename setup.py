from setuptools import setup, find_packages

setup(
    name='notebook-cat',
    version='1.5.0',
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
            'notebook-cat-web=notebook_cat.webui:launch_ui',
        ],
    },
    install_requires=[
        'gradio>=3.36.1',  # Compatible with current installed version
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Utilities',
    ],
    python_requires='>=3.8',
)
