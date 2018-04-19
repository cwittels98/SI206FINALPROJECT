import unittest
from final_project import *



class TestSources(unittest.TestCase):
    #testing sources
    def test_scraping(self):
        list_of_ny = get_yelp_info("New York")
        self.assertEqual(len(list_of_ny), 100)

class TestDatabase(unittest.TestCase):
    #testing databases
    def test_restauraunt_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Restaurant'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 100)

    def second_test_table(self):
        sql = 'SELECT RestaurantWebsite FROM Info'
        results = cur.execute(sql)
        result_list = results.fetchone()
        self.assertIn(("biz"), result_list[0])

        sql = 'SELECT Cuizine FROM Info'
        results = cur.execute(sql)
        result_list = results.fetchone()
        self.assertEqual(type(result_list), str)

        sql = 'SELECT RestaurantMenu FROM Info'
        results = cur.execute(sql)
        result_list = results.fetchone()
        self.assertIn(('menu'), result_list)
#
#
    def test_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''SELECT Id
        FROM Restaurant
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(result_list[0], (1,))
        self.assertEqual(result_list[1], (2,))
        self.assertEqual(result_list[2], (3,))
        self.assertEqual(result_list[3], (4,))

class TestFunctions(unittest.TestCase):

    def test_top_restauraunt_function(self):
        name = get_top_restaurants("New York")
        self.assertEqual(len(name), 10)



    def test_get_restauraunt(self):
        name_3 = get_restaurant_info("Los Tacos No.1")
        self.assertIn(("/"), name_3[0][0])
        self.assertIn(("(212)"), name_3[0][1])
        self.assertIn(("menu"), name_3[0][2])
        self.assertEqual("Mexican", name_3[0][3])
        self.assertIn(("75"), name_3[0][4])




unittest.main()
