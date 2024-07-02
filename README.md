
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

To use the package, you can either create a script or run it directly from the command line.

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

### Command Line Usage
You can also run the package directly from the command line:

```bash
my_maps_generator --template path/to/template.jinja2 --input path/to/input.csv --output path/to/output.kml
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
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Untitled map</name>
    <description/>
    <Style id="icon-1899-0288D1-nodesc-normal">
      <IconStyle>
        <color>ffd18802</color>
        <scale>1</scale>
        <Icon>
          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle>
      <BalloonStyle>
        <text><![CDATA[<h3>$[name]</h3>]]></text>
      </BalloonStyle>
    </Style>
    <Style id="icon-1899-0288D1-nodesc-highlight">
      <IconStyle>
        <color>ffd18802</color>
        <scale>1</scale>
        <Icon>
          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
      </IconStyle>
      <LabelStyle>
        <scale>1</scale>
      </LabelStyle>
      <BalloonStyle>
        <text><![CDATA[<h3>$[name]</h3>]]></text>
      </BalloonStyle>
    </Style>
    <StyleMap id="icon-1899-0288D1-nodesc">
      <Pair>
        <key>normal</key>
        <styleUrl>#icon-1899-0288D1-nodesc-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#icon-1899-0288D1-nodesc-highlight</styleUrl>
      </Pair>
    </StyleMap>
    <Style id="icon-1899-E65100-normal">
      <IconStyle>
        <color>ff0051e6</color>
        <scale>1</scale>
        <Icon>
          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle>
    </Style>
    <Style id="icon-1899-E65100-highlight">
      <IconStyle>
        <color>ff0051e6</color>
        <scale>1</scale>
        <Icon>
          <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>
      </IconStyle>
      <LabelStyle>
        <scale>1</scale>
      </LabelStyle>
    </Style>
    <StyleMap id="icon-1899-E65100">
      <Pair>
        <key>normal</key>
        <styleUrl>#icon-1899-E65100-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#icon-1899-E65100-highlight</styleUrl>
      </Pair>
    </StyleMap>
    {% for continent, countries in map_data.items() -%}
    <Folder>
        <name>{{ continent }}</name>
        {% for country, info in countries.items() -%}
            <Placemark>
                <name>{{ country }}</name>
                {% if info["Notes"] is defined -%}
                 <description>{{ info["Notes"] }}</description>
                 {%- endif %}
                <styleUrl>{{ info["Colour"] }}</styleUrl>
                {% if info["Image_link"] is defined %}
                <description><![CDATA[<img src="{{ info["Image_link"] }}" width="500" height="300" />]]></description>
                {% endif %}
                <Point>
                <coordinates>
                    {{ info["longitude"] }},{{ info["latitude"] }},0
                </coordinates>
                </Point>
            </Placemark>
        {% endfor -%}
    </Folder>
    {% endfor %}}
  </Document>
</kml>
```

## Testing

### Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover -s tests
```

## Contributors

[Jeyashree Krishnan](https://github.com/krishnanj) contributed to this repository.

