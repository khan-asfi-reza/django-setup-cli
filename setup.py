from setuptools import setup, find_packages


def read_requirements():
    with open("./build-requirements.txt", "r") as req:
        content = req.read()
        requirements = content.split("\n")
    return requirements


with open("./README.MD", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='django-setup-cli',
    version='1.0.16',
    include_package_data=True,
    description="django-setup-cli helps to produce production ready django project",
    author="Khan Asfi Reza",
    author_email="khanasfireza10@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khan-asfi-reza/django-setup-cli",
    packages=find_packages(exclude=("tests*",)),
    install_requires=read_requirements(),
    package_data={'': ['*.template',
                       'django_cli/template/*.template',
                       'template/*.template'],
                  'django_cli': ['template/*.template']
                  },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    entry_points='''
        [console_scripts]
        django-cli=django_cli.cli:cli
    ''',
    python_requires=">=3.6",
)
