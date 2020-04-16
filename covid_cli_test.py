import  unittest
from covid_cli import COVID


class TestCovidCLI(unittest.TestCase):
    
    def setUp(self):
        self.covid_cli = COVID()
        
    def test_getALLDataForUS(self):
        test_dict = self.covid_cli._getALLDataForUs()
        self.assertIsInstance(dict, test_dict)
        
    def tearDown(self):
        self.covid_cli.dispose()
        


unittest.main()