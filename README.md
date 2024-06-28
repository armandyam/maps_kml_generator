
# Maps KML Generator

[![Python Tests](https://github.com/armandyam/maps_kml_generator/actions/workflows/python-tests.yml/badge.svg)](https://github.com/armandyam/maps_kml_generator/actions/workflows/python-tests.yml)

This package processes city and country data from a CSV file, fetches geolocation coordinates, and generates a KML file using a Jinja2 template. This package can be used to generate a KML file required for uploade in [My Maps](https://www.google.com/maps/). 


![City and Country Map Generator](image_readme.webp)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

- Load city and country data from a CSV file.
- Fetch geolocation coordinates using the Geopy library.
- Generate KML files using Jinja2 templates.
- Cache coordinates in a local database to minimize geolocation requests.
- Logging of processing steps and errors.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/armandyam/maps_kml_generator.git
   cd maps_kml_generator
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use \`venv\Scripts\activate\`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the package, you can create a script that imports the necessary functions and runs the desired functionality.

### Example Script

Create a script named \`run_generator.py\` with the following content:

```python
from my_maps_generator.my_maps_generator import generate_template

if __name__ == '__main__':
    generate_template('path/to/template.jinja2', 'path/to/input.csv', 'path/to/output.kml')
```

Run the script:

```bash
python run_generator.py
```

## Configuration

### Environment Variables

- \`GEOLOCATOR_USER_AGENT\`: Set this environment variable to specify the user agent for the Geopy Nominatim geolocator.

### CSV Input File

The input CSV file should have the following format:

```
City,Country,Continent,Notes
Vienna,Austria,Europe,Some notes
Innsbruck,Austria,Europe,Some notes
Abu Dhabi,UAE,Asia,Some notes
```

### Jinja2 Template

The Jinja2 template file should define how the KML output should be generated. Here's an example template:

```jinja2
{% for continent, cities in map_data.items() %}
<Folder>
    <name>{{ continent }}</name>
    {% for city, details in cities.items() %}
    <Placemark>
        <name>{{ city }}</name>
        <description>{{ details.Notes }}</description>
        <Point>
            <coordinates>{{ details.longitude }},{{ details.latitude }}</coordinates>
        </Point>
    </Placemark>
    {% endfor %}
</Folder>
{% endfor %}
```

## Testing

### Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover -s tests
```

