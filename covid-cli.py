import mysql.connector
import mySQL
from covid import Covid  # covid API
from collections import OrderedDict
from datetime import datetime


class mysql_object(object):

    def __init__(self):
        self.mySQL = mySQL.mycursor
        self.myDB = mySQL.mydb


class colors:
    def prRed(self, input_string):
        colored_string = ("\033[91m {}\033[00m" .format(input_string))
        return colored_string

    def prGreen(self, input_string):
        colored_string = ("\033[92m {}\033[00m" .format(input_string))
        return colored_string

    def prYellow(self, input_string):
        colored_string = ("\033[93m {}\033[00m" .format(input_string))
        return colored_string


class COVID(object):

    def __init__(self):
        self.covid_data = OrderedDict()
        self._covidObject = Covid(source="john_hopkins")
        self.sql_string = "INSERT INTO covid_data_us VALUES (%s, %s, %s, %s, %s)"
        self.current_date = datetime.today().strftime('%Y-%m-%d')

    def _getCOVID_databyCountry(self, country_ID):
        country_cases = self._covidObject.get_status_by_country_id(country_ID)
        confirmed, active, deaths, recovered = country_cases['confirmed'], country_cases[
            'active'], country_cases['deaths'], country_cases['recovered']
        values = (self.current_date, confirmed, active, deaths, recovered)
        return values

    def _getAllData(self):
        global_data = self._covidObject.get_data()
        for elem in global_data:
            for key, value in elem.items():
                if key == 'country':
                    country = value
                if key == 'confirmed':
                    confirmed = value
                if key == 'active':
                    active = value
                if key == 'deaths':
                    deaths = value
                if key == 'recovered':
                    recovered = value
        values = (country, confirmed, active, deaths, recovered)
        return values

    def insert_mySQL(self, values):
        try:
            mysql_object().mySQL.execute(self.sql_string, values)
            mysql_object().myDB.commit()
            print(colors().prGreen('Inserted Successfully'))
            return True
        except Exception as error:
            print(colors().prRed('{} error created'.format(error)))

    def main(self):
        covid_19 = COVID()
        covid_19.insert_mySQL(covid_19._getCOVID_databyCountry(18))


if __name__ == '__main__':
    COVID().main()
