import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="jupyter_Pandas_GUI",
    version="0.6.2",
    description="Pandas expression composers using Jupyter widgets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://jupyterphysscilab.github.io/jupyter_Pandas_GUI/",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    keywords="fitting, data-analysis, plotting, learning to code",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    package_data={},
    include_package_data=True,
    install_requires=[
        # 'python>=3.6',
        'jupyter>=1.0.0',
        'pandas>=1.2.5',
        'numpy>=1.19.0',
        'plotly>=5.5.0',
        'ipywidgets>=7.6.2',
        'JPSLUtils>=0.5.8',
        'lmfit>=1.0.3',
        'round-using-error>=1.1.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent'
    ]
)
