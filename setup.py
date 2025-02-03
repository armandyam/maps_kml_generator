from setuptools import setup, find_packages

setup(
    name='my_maps_generator',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'geopy',
        'jinja2',
        'unidecode',
    ],
    entry_points={
        'console_scripts': [
            'my_maps_generator=my_maps_generator.my_maps_generator:main',
        ],
    },
    description='A package for processing geographical data and generating KML files ready to be uploaded to My Maps.',
)
