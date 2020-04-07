import mysql.connector
import mySQL
from covid import Covid  # covid API
from collections import OrderedDict
from datetime import datetime

current_date = datetime.today().strftime('%Y-%m-%d')


def place_value(number):
    return ("{:,}".format(number))


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
        self._covidObject = Covid(source="john_hopkins")
        self.sql_scripts = {
            'insert_us': "INSERT INTO covid_data_us VALUES (%s, %s, %s, %s, %s)",
            'insert_global': "INSERT INTO covid_data_global VALUES (%s, %s, %s, %s, %s)",
            'delete_us': "DELETE FROM covid_data_us",
            'delete_global': "DELETE FROM covid_data_global",
            'get_max_confirmed': "SELECT country, confirmed FROM covid_data_global WHERE confirmed = (SELECT MAX(confirmed) from covid_data_global)",
            'get_max_deaths': "SELECT country, deaths FROM covid_data_global WHERE deaths = (SELECT MAX(deaths) from covid_data_global)",
        }

    def _getCOVID_databyCountry(self, country_ID):
        country_cases = self._covidObject.get_status_by_country_id(country_ID)
        confirmed, active, deaths, recovered = country_cases['confirmed'], country_cases[
            'active'], country_cases['deaths'], country_cases['recovered']
        values = (current_date, confirmed, active, deaths, recovered)
        return values

    def _getAllData(self):
        values = []
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
            values.append((country, confirmed, active, deaths, recovered))
        return values

    def insert_mySQL(self, values, sql_string, many=False):
        try:
            if many:
                mysql_object().mySQL.executemany(sql_string, values)
            else:
                mysql_object().mySQL.execute(sql_string, values)
            mysql_object().myDB.commit()
            print(colors().prGreen('Inserted values successfully'))
            return True
        except Exception as error:
            print(colors().prRed('{} error while inserting '.format(error)))

    def delete_mySQL(self, sql_string):
        try:
            mysql_object().mySQL.execute(sql_string)
            mysql_object().myDB.commit()
            print(colors().prGreen('Deleted values successfully'))
        except Exception as error:
            print('{} error while deleting'.format(error))

    def delete_mySQL(self, sql_string):
        try:
            mysql_object().mySQL.execute(sql_string)
            mysql_object().myDB.commit()
            print(colors().prGreen('Deleted values successfully'))
        except Exception as error:
            print('{} error while deleting'.format(error))

    def get_max(self, sql_string):
        max = None
        try:
            if 'confirmed' in sql_string:
                value = 'confirmed'
            if 'deaths' in sql_string:
                value = 'deaths'
            mysql_object().mySQL.execute(sql_string)
            result = mysql_object().mySQL.fetchone()
            max = result
        except Exception as error:
            print('{} error in getting max {}'.format(error, value))
        return max

    def _CountryWithMaxDeaths(self, max_deaths_tuple):
        return 'The country with the max deaths currently is {} with {} deaths'.format(
            max_deaths_tuple[0], place_value(max_deaths_tuple[1]))

    def _CountryWithMaxConfirmed(self, max_confirmed_tuple):
        return 'The country with the max confirmed cases currently is {} with {} cases'.format(
            max_confirmed_tuple[0], place_value(max_confirmed_tuple[1]))

    def _getTotalStats(self):
        total_stats = {
            'total_active_cases': self._covidObject.get_total_active_cases(),
            'total_confirmed_cases': self._covidObject.get_total_confirmed_cases(),
            'total_recovered_cases': self._covidObject.get_total_recovered(),
            'total_deaths': self._covidObject.get_total_deaths()
        }
        return total_stats

    def printDailyStatusReport(self, total_stats, country_max_deaths, country_max_confirmed):
        daily_report = """
        Here is the COVID-19 for today {date}: 
        
        Total Active Cases: {active_cases}
        Total Confirmed Cases: {confirmed_cases}
        Total Recovered Cases: {recovered_cases}
        Total Deaths: {deaths}
        
        {max_deaths}
        {max_confirmed}
        """.format(date=current_date, active_cases=total_stats['total_active_cases'],
                   confirmed_cases=total_stats['total_confirmed_cases'], recovered_cases=total_stats['total_recovered_cases'],
                   deaths=total_stats['total_deaths'], max_deaths=country_max_deaths, max_confirmed=country_max_confirmed)
        return daily_report

    def main(self):
        covid_19 = COVID()
        print('--------------COVID Program Running-------------------')
        covid_19.delete_mySQL(self.sql_scripts['delete_us'])
        covid_19.delete_mySQL(self.sql_scripts['delete_global'])
        covid_19.insert_mySQL(covid_19._getCOVID_databyCountry(
            18), self.sql_scripts['insert_us'])
        covid_19.insert_mySQL(covid_19._getAllData(),
                              self.sql_scripts['insert_global'], True)
        max_deaths = covid_19._CountryWithMaxDeaths(
            covid_19.get_max(self.sql_scripts['get_max_deaths']))
        max_confirmed = covid_19._CountryWithMaxConfirmed(
            covid_19.get_max(self.sql_scripts['get_max_confirmed']))
        print(covid_19.printDailyStatusReport(
            covid_19._getTotalStats(), max_deaths, max_confirmed))


if __name__ == '__main__':
    COVID().main()
