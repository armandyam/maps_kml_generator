import collections
import csv
import logging
import json
import os
from geopy.geocoders import Nominatim
from jinja2 import Environment, FileSystemLoader, meta
from typing import Tuple, Dict, Set, Optional
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_json_data(filename: str) -> dict:
    """
    Read JSON data from a file.

    Args:
        filename (str): Path to the JSON file.

    Returns:
        dict: The data loaded from the JSON file.
    """
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def load_jinja_template(template_file: str) -> Tuple[Environment, Set[str]]:
    """
    Load a Jinja2 template and parse for undeclared variables.

    Args:
        template_file (str): Path to the Jinja2 template file.

    Returns:
        Tuple[Environment, Set[str]]: The Jinja2 template and a set of undeclared variables.
    """
    template_folder = os.path.dirname(template_file) or "."
    template_loader = FileSystemLoader(searchpath=template_folder)
    template_env = Environment(loader=template_loader)
    template_name = os.path.basename(template_file)
    template = template_env.get_template(template_name)
    template_source = template_env.loader.get_source(template_env, template_name)
    parsed_content = template_env.parse(template_source)
    undeclared_variables = meta.find_undeclared_variables(parsed_content)
    return template, undeclared_variables

def parse_country_list(file_name: str) -> Dict[str, Dict[str, dict]]:
    """
    Read country list from a CSV file and return data structure.

    Args:
        file_name (str): Path to the CSV file.

    Returns:
        Dict[str, Dict[str, dict]]: A dictionary with continent data.
    """
    continent_data = collections.defaultdict(dict)
    cities = set()
    countries = set()
    continents = set()

    with open(file_name, 'r') as csvfile:
        lines = csv.reader(csvfile)
        next(lines, None)
        for line in lines:
            city, country, continent, notes = map(str.strip, line[:4])
            lat, lon = get_city_coordinates(city, country, continent)
            cities.add(city)
            countries.add(country)
            continents.add(continent)
            if city not in continent_data[continent]:
                continent_data[continent][city] = {
                    "Notes": notes,
                    "latitude": lat,
                    "longitude": lon,
                    "Colour": "#icon-1899-0288D1-nodesc"
                }

    logging.info(f"Processed {len(cities)} cities, {len(countries)} countries, {len(continents)} continents.")
    return continent_data

def get_coordinates_from_db(city: str, country: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get latitude and longitude from the database.

    Args:
        city (str): Name of the city.
        country (str): Name of the country.

    Returns:
        Tuple[Optional[str], Optional[str]]: Latitude and longitude if found, otherwise None.
    """
    try:
        with open('city_country_data_base.csv', 'r') as csvfile:
            lines = csv.reader(csvfile)
            for line in lines:
                if line[0].strip() == city and line[1].strip() == country:
                    logging.info(f"{city}, {country} found in DB")
                    return line[3], line[4]
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    return None, None

def add_coordinates_to_db(city: str, country: str, continent: str, lat: float, lon: float) -> None:
    """
    Add latitude and longitude to the database.

    Args:
        city (str): Name of the city.
        country (str): Name of the country.
        continent (str): Name of the continent.
        lat (float): Latitude of the city.
        lon (float): Longitude of the city.
    """
    with open('city_country_data_base.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow([city.strip(), country.strip(), continent.strip(), lat, lon])

def get_city_coordinates(city: str, country: str, continent: str) -> Tuple[float, float]:
    """
    Get latitude and longitude, using cache or geolocation service.

    Args:
        city (str): Name of the city.
        country (str): Name of the country.
        continent (str): Name of the continent.

    Returns:
        Tuple[float, float]: Latitude and longitude of the city.
    """
    lat, lon = get_coordinates_from_db(city, country)
    if lat and lon:
        logging.info(f"Reading info about {city}, {country} from file")
        return float(lat), float(lon)
    else:
        logging.info(f"Getting info about {city}, {country} from geopy")
        user_agent = os.getenv('GEOLOCATOR_USER_AGENT', 'default_user_agent')
        geolocator = Nominatim(user_agent=user_agent)
        location = geolocator.geocode(f"{city}, {country}")
        add_coordinates_to_db(city, country, continent, location.latitude, location.longitude)
        return location.latitude, location.longitude

def render_template(template_data: dict, template: Environment, output_file: str) -> None:
    """
    Render Jinja2 template and write to output file.

    Args:
        template_data (dict): Data to be used in the template.
        template (Environment): Jinja2 template object.
        output_file (str): Path to the output file.
    """
    output_folder = os.path.dirname(output_file)
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_text = template.render(template_data)
    with open(output_file, "w") as text_file:
        text_file.write(output_text)


def generate_template(template_file: str, input_file: str, output_file: str) -> None:
    """
        Main function to process data and generate output.

        Args:
            template_file (str): Path to the Jinja2 template file.
            input_file (str): Path to the input CSV file.
            output_file (str): Path to the output file.
        """
    template, undeclared_variables = load_jinja_template(template_file)
    map_data = parse_country_list(input_file)
    template_data = {"map_data": map_data}
    render_template(template_data, template, output_file)


def main() -> None:
    parser = argparse.ArgumentParser(description='Process data and generate KML file.')
    parser.add_argument('--template', type=str, default='kml_maps.jinja2', help='Jinja2 template file')
    parser.add_argument('--input', type=str, default='country_city.csv', help='Input CSV file')
    parser.add_argument('--output', type=str, default='map_file_jk.kml', help='Output KML file')
    args = parser.parse_args()

    generate_template(args.template, args.input, args.output)

if __name__ == '__main__':
    main()
