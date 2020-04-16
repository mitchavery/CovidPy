import mysql.connector
import matplotlib.pyplot as plt
import mySQL
import sys
import pygal
import countries_list
from pygal.maps.world import World
from covid import Covid  # covid API
from collections import OrderedDict
from datetime import datetime

current_date = datetime.today().strftime('%Y-%m-%d')


def place_value(number):
    return ("{:,}".format(number))


class mysql_object:

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
            'insert_us': "INSERT INTO covid_data_us (confirmed, active, deaths, recovered, death_rate, day) VALUES (%s, %s, %s, %s, %s, %s)",
            'insert_global': "INSERT INTO covid_data_global VALUES (%s, %s, %s, %s, %s)",
            'delete_us': "DELETE FROM covid_data_us",
            'delete_global': "DELETE FROM covid_data_global",
            'get_max_confirmed': "SELECT country, confirmed FROM covid_data_global WHERE confirmed = (SELECT MAX(confirmed) from covid_data_global)",
            'get_max_deaths': "SELECT country, deaths FROM covid_data_global WHERE deaths = (SELECT MAX(deaths) from covid_data_global)",
            'get_countries': "SELECT country FROM covid_data_global",
            'get_us_data': "SELECT * FROM covid_data_us",
            'get_global_data': "SELECT * FROM covid_data_global"
        }

    def _getCOVID_databyCountry(self, country_ID):
        country_cases = self._covidObject.get_status_by_country_id(country_ID)
        confirmed, active, deaths, recovered = country_cases['confirmed'], country_cases[
            'active'], country_cases['deaths'], country_cases['recovered']
        death_rate = self._getCurrentDeathRate()
        values = (confirmed, active,
                  deaths, recovered, death_rate, current_date)
        return values

    def _getALLDataForUs(self):
        us_data = {
            "confirmed": [],
            "deaths": [],
            "days": []
        }
        try:
            mysql_object().mySQL.execute(self.sql_scripts['get_us_data'])
            result = mysql_object().mySQL.fetchall()
            for entry in result:
                confirmed, deaths, day_num = entry[0], entry[2], entry[len(
                    entry) - 2]
                us_data['confirmed'].append(confirmed)
                us_data['deaths'].append(deaths)
                us_data['days'].append(day_num)
        except Exception as error:
            print("Error getting US data: {}".format(error))
        return us_data

    def _getGlobalData(self):
        global_data_confirmed = {}
        global_data_deaths = {}
        try:
            mysql_object().mySQL.execute(self.sql_scripts['get_global_data'])
            result = mysql_object().mySQL.fetchall()
            for entry in result:
                country, confirmed, deaths = entry[0], entry[1], entry[3]
                global_data_confirmed[country] = confirmed
                global_data_deaths[country] = deaths
        except Exception as error:
            print('Error getting Global data: {}'.format(error))
        return global_data_confirmed, global_data_deaths

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

    def _validateCountry(self, input_country):
        countries = []
        try:
            mysql_object().mySQL.execute(self.sql_scripts['get_countries'])
            result = mysql_object().mySQL.fetchall()  # returns a list of tuples
            for element in result:
                countries.append(element[0].lower())
            if input_country in countries:
                return True
            return False
        except Exception as error:
            print('Error validating country {}'.format(error))

    def _getCurrentDeathRate(self):
        confirmed, deaths = self._getDataForUS()
        death_rate = (deaths / confirmed) * 100
        return death_rate

    def _getDataForUS(self):
        us_status = self._covidObject.get_status_by_country_id(18)
        confirmed, deaths = us_status['confirmed'], us_status['deaths']
        return confirmed, deaths

    def _getDataForCountry(self):
        not_print = ['Id', 'Latitude', 'Longitude', 'Last_update']
        success = False
        while not success:
            country = input(colors().prGreen(
                'Country to look up for COVID info: ')).strip().lower()
            if self._validateCountry(country):
                success = True
            else:
                print('please enter a correct country')
        country_status = self._covidObject.get_status_by_country_name(country)
        for keys, values in country_status.items():
            if isinstance(values, int):
                values = place_value(values)
            if keys.capitalize() not in not_print:
                print('{}: {}'.format(keys.capitalize(), values))

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

    def _graphDataForUSStats(self, us_data):
        deaths_data = us_data['deaths']
        confirmed_data = us_data['confirmed']
        day_nums = us_data['days']
        plt.plot(day_nums, deaths_data, label="line 1", color='red', linestyle='dashed', linewidth=1,
                 marker='o', markerfacecolor='blue', markersize=2)
        plt.xlabel('Days')
        plt.ylabel('Deaths')
        plt.title('COVID deaths/Confirmed vs Days')
        plt.show()
        
    def _pairCountries(self):
        countries_list_pairs_confirmed, countries_list_pairs_deaths = {}, {}
        # countries/confirmed are both lists
        # dict contains countries and confirmed cases from JH API
        countries_dict_confirmed, countries_dict_deaths = self._getGlobalData()
        # dict contains country name and country code
        available_countries = countries_list.countries
        for country in countries_dict_confirmed.keys(): 
            if country in available_countries: 
                countries_list_pairs_confirmed[available_countries[country]] = countries_dict_confirmed[country]
        for country1 in countries_dict_deaths.keys():
            if country1 in available_countries: 
                countries_list_pairs_deaths[available_countries[country1]] = countries_dict_deaths[country1]
        return countries_list_pairs_confirmed, countries_list_pairs_deaths
        

    def _plotDataWorldMap(self):
        try:
            worldmap_chart = pygal.maps.world.World()
            worldmap_chart.title = 'COVID Active Cases Per Country'
            worldmap_chart.force_uri_protocol = "http"
            confirmed, deaths = self._pairCountries()
            worldmap_chart.add('Confirmed', confirmed)
            worldmap_chart.add('Deaths', deaths)
            worldmap_chart.render_in_browser()
            worldmap_chart.render_to_file('map.svg')
        except Exception as Error:
            print('Error found: {}'.format(Error))

    def main(self):
        covid_19 = COVID()
        print('--------------COVID Program Running-------------------')
        # covid_19.delete_mySQL(self.sql_scripts['delete_us'])
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
        covid_19._getDataForCountry()
        covid_19._graphDataForUSStats(covid_19._getALLDataForUs())
        covid_19._plotDataWorldMap()
        sys.exit()


if __name__ == '__main__':
    COVID().main()