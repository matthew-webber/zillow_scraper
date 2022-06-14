import json
import re
from datetime import datetime
import csv

import requests
from bs4 import BeautifulSoup

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


class ZillowHomeFactory:

    @staticmethod
    def create_home(home_data):
        """
        Create home
        :param home_data: list of home data
        """
        return [ZillowHome(home) for home in home_data]


class ZillowResults:
    """
    Class for zillow results
    """

    def __init__(self, data):
        self.data = data['cat1']['searchResults']['listResults']
        self.totalPages = data['cat1']['searchList']['totalPages']


class ZillowHome:
    """
    Class for zillow data
    """
    _csv_excluded_keys = [
        'data',
        'date_price_changed_timestamp',
        'img_url',
    ]

    def __init__(self, home_data):
        self.data = self.get_data(home_data)

        # set properties for all getters
        self.zestimate = self.get_zestimate()
        self.address = self.get_address()
        self.city = self.get_city()
        self.state = self.get_state()
        self.zipcode = self.get_zipcode()
        self.street_address = self.get_street_address()
        self.date_price_changed_timestamp = self.get_date_price_changed()
        self.bedrooms = self.get_bedrooms()
        self.bathrooms = self.get_bathrooms()
        self.tax_assessed_value = self.get_tax_assessed_value()
        self.price = self.get_price()
        self.url = self.get_url()
        self.img_url = self.get_img_url()
        self.date_price_changed = self.date_from_timestamp(
            self.date_price_changed_timestamp) if self.date_price_changed_timestamp else None
        # self.date_price_changed_parsed = self.parse_time(self.date_price_changed)

    @staticmethod
    def get_data(home_data):
        """
        Get home detail data
        """
        data1 = home_data['hdpData']['homeInfo']
        data2 = home_data
        return dict(data1, **data2)

    @staticmethod
    def parse_time(time_string):
        """
        Parse time from time string
        """
        return time_string.year, time_string.month, time_string.day, time_string.hour

    @staticmethod
    def date_from_timestamp(timestamp):
        """
        Convert from timestamp
        """
        return datetime.fromtimestamp(int(timestamp) / 1000)

    def get_meaningful_properties(self):
        """
        Get the properties of the data object useful for human consumption
        :return: array of properties
        """
        return [attr for attr in dir(self) if
                not callable(getattr(self, attr)) and not attr.startswith(
                    "_") and attr not in self._csv_excluded_keys]

    def get_meaningful_data(self, meaningful_properties):
        """
        Get meaningful data
        """
        return [str(getattr(self, prop)) for prop in meaningful_properties]

    def format_for_csv(self):
        """
        Format for csv
        """
        return [self.zestimate, self.address, self.city, self.state, self.zipcode, self.street_address,
                self.date_price_changed, self.bedrooms, self.bathrooms, self.tax_assessed_value, self.price]

    def dump(self):
        """
        Dump
        """
        return json.dumps(self.data)

    def dump_pretty(self):
        """
        Dump pretty
        """
        return json.dumps(self.data, indent=4)

    def dump_pretty_file(self, filename):
        """
        Dump pretty file
        """
        with open(filename, 'w') as f:
            f.write(self.dump_pretty())

    def dump_to_csv(self, filename):
        pass

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)

    def get_url(self):
        """
        Get url
        """
        return self.data['detailUrl']

    def get_img_url(self):
        """
        Get img url
        """
        return self.data['imgSrc']

    def get_zestimate(self):
        """
        Get zestimate
        """
        try:
            return self.data['zestimate']
        except KeyError:
            return 0

    def get_address(self):
        """
        Get address
        """
        return self.data['address']

    def get_city(self):
        """
        Get city
        """
        return self.data['city']

    def get_state(self):
        """
        Get state
        """
        return self.data['state']

    def get_zipcode(self):
        """
        Get zipcode
        """
        return self.data['zipcode']

    def get_street_address(self):
        """
        Get street address
        """
        return self.data['streetAddress']

    def get_date_price_changed(self):
        print('x')
        """
        Get date price changed
        """
        try:
            return self.data['datePriceChanged']
        except KeyError:
            return 0

    def get_bedrooms(self):
        """
        Get bedrooms
        """
        return self.data['bedrooms']

    def get_bathrooms(self):
        """
        Get bathrooms
        """
        return self.data['bathrooms']

    # get taxAssessedValue
    def get_tax_assessed_value(self):
        """
        Get tax assessed value
        """
        try:
            return self.data['taxAssessedValue']
        except KeyError:
            return 0

    # get price
    def get_price(self):
        """
        Get price
        """
        return self.data['price']

    @staticmethod
    def convert_to_price(price):
        """
        Convert to price
        """
        return "${:,.0f}".format(price)


def get_zillow_data(headers=None, status='for_sale', area=None, *args, **kwargs):
    """
    Get data from url
    :param area:
    :param status:
    :param headers:
    """
    if headers is None:
        headers = req_headers

    if area is None:
        raise Exception('City is required')
    else:
        area = area.replace(' ', '-')
        area = str(area)

    with requests.Session() as s:
        url = f'https://www.zillow.com/homes/{status}/{area}'
        response = s.get(url, headers=req_headers)

    return response


def parse_zillow_data(response):
    """
    Parse data from response
    :param response:
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    data = soup.find_all('script')
    for d in data:
        if 'zestimate' in d.text:
            return d


def get_zillow_data_json(response):
    """
    Get json data from response
    :param response:
    """
    json_data_soup = parse_zillow_data(response)
    json_data_only = re.search('<!--(.+?)-->', json_data_soup.text).group(1)
    json_data = json.loads(json_data_only)
    return json_data


def dump_data(path, _data, indent=4):
    """
    Dump data to json file
    :param indent:
    :param path:
    :param _data:
    """
    with open(f'{path}.json', 'w') as f:
        json.dump(_data, f, indent=indent)

def get_zillow_data(load=False, area=None, type=None, *args, **kwargs):
    """
    Get zillow data
    :param load:
    :param area:
    :param type:
    """
    if load:
        try:
            with open(f'{area}_{type}.json', 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            print('Existing file not found')
            response = input('Retrieve data from zillow? (y/n)')
            if response == 'y':
                pass
            else:
                return
    else:
        if area is None:
            raise Exception('Area is required')
        if type is None:
            raise Exception('Type is required')
        data = get_zillow_data_json(get_zillow_data(area=area, type=type))
    return data


if __name__ == '__main__':
    # check if zillow_data.json exists and load it into data variable
    try:
        with open('zillow_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        r = get_zillow_data(city='Charleston')
        data = get_zillow_data_json(r)

    zillow_results = ZillowResults(data)
    zillow_data = ZillowHomeFactory.create_home(zillow_results.data)

    # test all HomeData methods
    # properties = [attr for attr in dir(charleston_data[0]) if
    #               not callable(getattr(charleston_data[0], attr)) and not attr.startswith(
    #                   "_") and attr not in ZillowHome._csv_excluded_keys]

    properties = zillow_data[0].get_meaningful_properties()

    homes_data = []
    for home in zillow_data:
        home_data = home.get_meaningful_data(properties)
        homes_data.append(home_data)

    # dump data to csv
    with open('zillow_data.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(properties)
        writer.writerows(homes_data)

    # print('get_zestimate() = ', charleston_data.get_zestimate())
    # print('get_address() = ', charleston_data.get_address())
    # print('get_city() = ', charleston_data.get_city())
    # print('get_state() = ', charleston_data.get_state())
    # print('get_zipcode() = ', charleston_data.get_zipcode())
    # print('get_street_address() = ', charleston_data.get_street_address())
    # print('get_date_price_changed() = ', charleston_data.get_date_price_changed())
    # print('get_date_price_changed(raw=True) = ', charleston_data.get_date_price_changed(raw=True))
    # print('get_bedrooms() = ', charleston_data.get_bedrooms())
    # print('get_bathrooms() = ', charleston_data.get_bathrooms())
    # print('get_tax_assessed_value() = ', charleston_data.get_tax_assessed_value())
    # print('get_price() = ', charleston_data.get_price())
    # print('get_img_url() = ', charleston_data.get_img_url())
    # print('get_url() = ', charleston_data.get_url())
    # print('str() = ', charleston_data)
    # print('repr() = ', charleston_data)
    # print('__str__() = ', charleston_data)
    # print('__repr__() = ', charleston_data)
    # print('__dict__ = ', charleston_data.__dict__)

    print('hello world')
    print('hello world')
