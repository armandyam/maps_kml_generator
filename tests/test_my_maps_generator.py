import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import subprocess
from my_maps_generator.my_maps_generator import (
    load_json_data,
    load_jinja_template,
    parse_country_list,
    get_coordinates_from_db,
    add_coordinates_to_db,
    get_city_coordinates,
    render_template,
    generate_template
)

class TestMyMapsGenerator(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_json_data(self, mock_file):
        filename = "dummy.json"
        data = load_json_data(filename)
        mock_file.assert_called_with(filename, 'r')
        self.assertEqual(data, {"key": "value"})

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_render_template_creates_output_folder(self, mock_file, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        template_data = {"key": "value"}
        template = MagicMock()
        output_file = "output_folder/output_file.kml"
        render_template(template_data, template, output_file)
        mock_makedirs.assert_called_with("output_folder")
        mock_file.assert_called_with(output_file, "w")

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_render_template_does_not_create_existing_folder(self, mock_file, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        template_data = {"key": "value"}
        template = MagicMock()
        output_file = "existing_folder/output_file.kml"
        render_template(template_data, template, output_file)
        mock_makedirs.assert_not_called()
        mock_file.assert_called_with(output_file, "w")

    @patch("builtins.open", new_callable=mock_open, read_data="City,Country,Continent,Notes\nVienna,Austria,Europe,\n")
    @patch("my_maps_generator.my_maps_generator.get_city_coordinates")
    def test_parse_country_list(self, mock_get_coords, mock_file):
        mock_get_coords.return_value = (48.2083537, 16.3725042)
        file_name = "dummy.csv"
        result = parse_country_list(file_name)
        expected = {
            "Europe": {
                "Vienna": {
                    "Notes": "",
                    "latitude": 48.2083537,
                    "longitude": 16.3725042,
                    "Colour": "#icon-1899-0288D1-nodesc"
                }
            }
        }
        self.assertEqual(result, expected)

    @patch("builtins.open", new_callable=mock_open, read_data="Vienna,Austria,Europe,48.2083537,16.3725042\n")
    def test_get_coordinates_from_db_found(self, mock_file):
        city = "Vienna"
        country = "Austria"
        lat, lon = get_coordinates_from_db(city, country)
        self.assertEqual(lat, "48.2083537")
        self.assertEqual(lon, "16.3725042")

    @patch("builtins.open", new_callable=mock_open)
    def test_get_coordinates_from_db_not_found(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        city = "NonExistentCity"
        country = "NonExistentCountry"
        lat, lon = get_coordinates_from_db(city, country)
        self.assertIsNone(lat)
        self.assertIsNone(lon)

    @patch("csv.writer")
    @patch("builtins.open", new_callable=mock_open)
    def test_add_coordinates_to_db(self, mock_file, mock_writer):
        city = "NewCity"
        country = "NewCountry"
        continent = "NewContinent"
        lat = 12.34
        lon = 56.78
        add_coordinates_to_db(city, country, continent, lat, lon)
        mock_file.assert_called_with('city_country_data_base.csv', 'a')
        mock_writer().writerow.assert_called_with(["NewCity", "NewCountry", "NewContinent", 12.34, 56.78])

    @patch("geopy.geocoders.Nominatim.geocode")
    @patch("my_maps_generator.my_maps_generator.get_coordinates_from_db")
    @patch("my_maps_generator.my_maps_generator.add_coordinates_to_db")
    def test_get_city_coordinates(self, mock_add_db, mock_get_db, mock_geocode):
        city = "Vienna"
        country = "Austria"
        continent = "Europe"
        mock_get_db.return_value = (None, None)
        mock_geocode.return_value = MagicMock(latitude=48.2083537, longitude=16.3725042)
        lat, lon = get_city_coordinates(city, country, continent)
        self.assertEqual(lat, 48.2083537)
        self.assertEqual(lon, 16.3725042)
        mock_add_db.assert_called_with(city, country, continent, 48.2083537, 16.3725042)

    @patch("my_maps_generator.my_maps_generator.load_jinja_template")
    @patch("my_maps_generator.my_maps_generator.parse_country_list")
    @patch("my_maps_generator.my_maps_generator.render_template")
    def test_generate_template(self, mock_render, mock_parse, mock_load_template):
        template_file = "template.jinja2"
        input_file = "input.csv"
        output_file = "output.kml"
        mock_load_template.return_value = (MagicMock(), set())
        mock_parse.return_value = {"key": "value"}
        generate_template(template_file, input_file, output_file)
        mock_load_template.assert_called_with(template_file)
        mock_parse.assert_called_with(input_file)
        mock_render.assert_called_with({"map_data": {"key": "value"}}, mock_load_template.return_value[0], output_file)

class TestCLI(unittest.TestCase):

    def setUp(self):
        # Create dummy input CSV file
        self.input_file = 'dummy_country_city.csv'
        with open(self.input_file, 'w') as f:
            f.write("City,Country,Continent,Notes\n")
            f.write("Vienna,Austria,Europe,\n")
            f.write("Innsbruck,Austria,Europe,\n")
            f.write("Abu Dhabi,UAE,Asia,\n")

        # Create dummy database CSV file
        self.database_file = 'city_country_data_base.csv'
        with open(self.database_file, 'w') as f:
            f.write("Vienna,Austria,Europe,48.2083537,16.3725042\n")
            f.write("Innsbruck,Austria,Europe,47.2654296,11.3927685\n")
            f.write("Brussels,Belgium,Europe,50.8465573,4.351697\n")
            f.write("Ghent,Belgium,Europe,51.0538286,3.7250121\n")

        # Create dummy template file
        self.template_file = 'dummy_template.jinja2'
        with open(self.template_file, 'w') as f:
            f.write("""
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
            """)

        self.output_file = 'output/map_file_jk.kml'

    def tearDown(self):
        os.remove(self.input_file)
        os.remove(self.database_file)
        os.remove(self.template_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_cli(self):
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        result = subprocess.run([
            'my_maps_generator',
            '--template', self.template_file,
            '--input', self.input_file,
            '--output', self.output_file
        ], capture_output=True, text=True)

        # Check that the process ran successfully
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(self.output_file))

if __name__ == '__main__':
    unittest.main()
