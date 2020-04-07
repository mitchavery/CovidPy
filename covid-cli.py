from covid import Covid
from collections import OrderedDict


class colors:
    def prRed(self, input_string):
        colored_string = ("\033[91m {}\033[00m" .format(input_string))
        return colored_string

    def prYellow(self, input_string):
        colored_string = ("\033[93m {}\033[00m" .format(input_string))
        return colored_string


class COVID(object):

    def __init__(self):
        self.covid_data = OrderedDict()
        self._covidObject = Covid(source="john_hopkins")

    def _getCOVID_databyCountry(self, country_ID):
        country_cases = self._covidObject.get_status_by_country_id(country_ID)
        return country_cases

    def main(self):
        covid_19 = COVID()
        covid_19._getCOVID_databyCountry(18)


if __name__ == '__main__':
    COVID().main()
