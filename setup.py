from setuptools import setup, find_packages

setup(
    name='oapi',
    version='0.1',
    description='Инструмент для аналитики пользовательского поведения.',
    long_description=open("README.md").read(),
    author='green-kit-7',
    author_email='',
    packages=find_packages(),
    install_requires=['requests','tqdm'],
    include_package_data=True,
    zip_safe=False
)