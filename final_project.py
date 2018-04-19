import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import webbrowser
from pprint import pprint as pp
import plotly.plotly as py
import plotly.graph_objs as go
import webbrowser



CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params={}):
    unique_ident = params_unique_combination(baseurl,params)
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]
    else:
        print("Making a request for new data...")
        resp = requests.get(baseurl, params)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]

DBNAME = 'restaurant_ratings.db'

conn = sqlite3.connect(DBNAME)
cur = conn.cursor()


def get_yelp_info(location):
    statement_1 = 'DROP TABLE IF EXISTS "Restaurant"'
    cur.execute(statement_1)
    conn.commit()
    statement_2 = 'DROP TABLE IF EXISTS "Info"'
    cur.execute(statement_2)
    conn.commit()

    statement_3 = '''
    CREATE TABLE IF NOT EXISTS 'Restaurant' (
    'Id' INTEGER PRIMARY KEY,
    'Name' TEXT,
    'GeneralLocation' TEXT,
    'RestaurantAddress' TEXT
    )
    '''
    cur.execute(statement_3)
    conn.commit()

    statement_4 = '''
    CREATE TABLE IF NOT EXISTS 'Info' (
    'Id' INTEGER PRIMARY KEY,
    'Rating' INTEGER,
    'Cuizine' TEXT,
    'RestaurauntID' INTEGER,
    'RestaurantMenu' TEXT,
    'RestaurantPhonenumber' TEXT,
    'RestaurantWebsite' TEXT)
    '''
    cur.execute(statement_4)
    conn.commit()

    start_number = 0
    for x in range(0, 100, 10):
        page_text = make_request_using_cache("https://www.yelp.com/search", params = {"find_loc" : location, "start" : x})
        page_soup = BeautifulSoup(page_text, 'html.parser')
        restaurant_list = page_soup.find_all('li', class_="regular-search-result")
        for info in restaurant_list:
            restauraunt_name = info.find("a", class_="biz-name").text
            restauraunt_link = info.find("a", class_="biz-name")["href"]
            print(restauraunt_link)
            page_text = make_request_using_cache("https://www.yelp.com/" + restauraunt_link)
            page_soup = BeautifulSoup(page_text, 'html.parser')
            try:
                restaurant_website = page_soup.find("span", class_= "biz-website").find("a")["href"]
            except:
                restaurant_website = None
            try:
                restauraunt_phone_number = page_soup.find("span", class_="biz-phone").text
            except:
                restauraunt_phone_number = None
            try:
                restaurant_address = page_soup.find("address").text
            except:
                restaurant_address = None
            try:
                restaurant_menu = page_soup.find("a", class_="menu-explore")["href"]
            except:
                restaurant_menu = None
            try:
                restauraunt_location = info.find("span", class_="neighborhood-str-list").text
            except:
                restauraunt_location = None
            try:
                type_of_food = ",".join([x.strip() for x in info.find("span", class_="category-str-list").text.replace("\n", "").split(',')])
            except:
                type_of_food = None
            try:
                restauraunt_rating = info.find("div", class_="i-stars")
            except:
                restauraunt_rating = None
            try:
                rating = restauraunt_rating["title"][0:3]
            except:
                rating = None

            insertion = (None, restauraunt_name, restauraunt_location, restaurant_address)
            statement_4 = '''
            INSERT INTO 'Restaurant'
            Values (?, ?, ?, ?)
            '''
            cur.execute(statement_4, insertion)

            statement_5 = '''
            SELECT Id
            FROM Restaurant
            WHERE Name = ?
            '''
            cur.execute(statement_5, (restauraunt_name, ))

            Id = cur.fetchone()[0]

            insertion_2 = (None, rating, type_of_food, Id, restaurant_menu, restauraunt_phone_number, restaurant_website)
            statement_6 = '''
            INSERT INTO 'Info'
            Values (?, ?, ?, ?, ?, ?, ?)
            '''
            cur.execute(statement_6, insertion_2)
    conn.commit()
    return restaurant_list


def get_top_restaurants(user_input):
    #get_yelp_info(user_input)

    statement = '''
    SELECT Name, Info.Rating, RestaurantAddress
    FROM Restaurant
    JOIN Info ON Restaurant.Id = Info.Id
    ORDER BY Info.Rating DESC
    LIMIT 10'''

    cur.execute(statement)
    results = cur.fetchall()
    restaurant_list = [x for x in results]

    formatted_list = []
    count = 0
    for each in restaurant_list:
        # print ("{0}\t{1}\t{2}\t".format(count, each[0], each[1]))
        formatted_list.append("{0}) {1}".format(count, each[0]))
        print ("{0}) {1}".format(count, each[0]))
        count +=1
    return restaurant_list

def make_restaurants_graphs(user_input, display_number):

    statement = '''
    SELECT Name, Info.Rating, GeneralLocation, RestaurantAddress
    FROM Restaurant
    JOIN Info ON Restaurant.Id = Info.Id
    ORDER BY Info.Rating DESC
    LIMIT 10'''

    cur.execute(statement)
    results = cur.fetchall()
    restaurant_list = [x for x in results]

    new_list_names = []
    new_list_ratings = []
    general_location = []
    addresses = []
    for each in restaurant_list:
        rest_name = each[0]
        rating = each[1]
        address = each[3]
        new_list_names.append(rest_name)
        new_list_ratings.append(rating)
        addresses.append(address)


    general_location = {}
    for locations in restaurant_list:
        if locations[2] not in general_location:
            general_location[locations[2]] = 0
        general_location[locations[2]] += 1
    # print (dict(general_location))


    if display_number == "1":
        data = [go.Bar(
        x= new_list_names,
        y= new_list_ratings)]
        layout = go.Layout(
            title = 'Restaurant Ratings',
            xaxis = dict(
            title = 'Restaurants'
            ),
            yaxis = dict(
            title = 'Ratings'
            ))
        fig = go.Figure(data=data, layout = layout)
        return py.plot(fig, filename='restaurant-bar')

    #pie chart
    elif display_number == "2":
        labels = new_list_ratings
        values = new_list_ratings
        trace = go.Pie(labels=labels, values=values)
        layout = go.Layout(
            title = 'Restaurant Rating Average')
        return py.plot([trace], filename='basic_pie_chart')

    #table
    elif display_number == "3":
        trace = go.Table(
        header=dict(values=['Restaurants', 'Ratings'],
                line = dict(color='#7D7F80'),
                fill = dict(color='#a1c3d1'),
                align = ['left'] * 5),
            cells=dict(values=[new_list_names, new_list_ratings],
                line = dict(color='#7D7F80'),
                fill = dict(color='#EDFAFF'),
                align = ['left'] * 5))

        layout = dict(width=1000, height=1000)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return py.plot(fig, filename = 'styled_table')


    elif display_number == "4":
        data = [go.Bar(
        x= list(general_location.keys()),
        y= list(general_location.values()))]
        layout = go.Layout(
            title = 'General Restaurant Location Mapper',
            xaxis = dict(
            title = 'General Location'
            ),
            yaxis = dict(
            title = 'Number of Restaurants'
            ))
        fig = go.Figure(data=data, layout = layout)
        return py.plot(fig, filename='restaurant-bar')

    elif display_number == "5":

        trace = go.Table(
        header=dict(values=['Restaurants', 'Addresses'],
                line = dict(color='#7D7F80'),
                fill = dict(color='#a1c3d1'),
                align = ['left'] * 5),
            cells=dict(values=[new_list_names, addresses],
                line = dict(color='#7D7F80'),
                fill = dict(color='#EDFAFF'),
                align = ['left'] * 5))

        layout = dict(width=1000, height=1000)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return py.plot(fig, filename = 'styled_table')

def get_restaurant_info(name):
    statement = '''
    SELECT Info.RestaurantWebsite, Info.RestaurantPhonenumber, Info.RestaurantMenu, Info.Cuizine, RestaurantAddress
    FROM Restaurant
    JOIN Info ON Restaurant.Id = Info.Id
    WHERE Restaurant.Name = '{}'
    '''.format(name)
    # print (statement)
    cur.execute(statement)
    results = cur.fetchall()
    restaurant_info = [x for x in results]
    return restaurant_info

def specific_restaurant_info(name, number):
    info = get_restaurant_info(name)

    if "1" == number:
        if info[0][int(number) - 1] != None:
            print ("Opening resturaunt's website.")
            webbrowser.open('https://www.yelp.com' + info[0][int(number) - 1])
        else:
            print ("Sorry, we cannot find a website on Yelp.")


    if "2" == number:
        if info[0][int(number) - 1] != None:
            print (info[0][int(number) - 1])
        else:
            print ("Sorry, we cannot find a phone number on Yelp.")

    if "3" == number:
        if info[0][int(number) - 1] != None:
            print ("Opening resturaunt's menu.")
            webbrowser.open('https://www.yelp.com' + info[0][int(number) - 1])
        else:
            print ("Sorry, we cannot find a menu on Yelp.")

    if "4" == number:
        if info[0][int(number) - 1] != None:
            print (info[0][int(number) - 1])
        else:
            print ("Sorry, we cannot find the cuisine on Yelp.")



def interactive_prompt():
    user_input = ""
    while user_input.lower() != "exit":
        user_input = input("Hi! Welcome to the top restaurant finder program. \nPlease enter a location to see the top 10 restaurants in that area, or type exit to stop the program: ")
        if user_input == "exit":
            print ("Goodbye!")
            exit()
        else:
            rest_list = get_top_restaurants(user_input)
            if len(rest_list) <1:
                print ("Please enter a valid location!")
                continue


            print ("\n----------------------------------------\n The following are options that will provide you with a display of information about the resturaunts and their ratings.")
            print ("#1: See a bar chart that shows the restaurants and their ratings.")
            print ("#2: See a pie chart that shows how many restaurants in that area have a certain rating.")
            print ("#3: See a table of the restaurants and their corresponding ratings.")
            print ("#4: See a bar chart of a general location in that area and the amount of restaurants in that locaiton.")
            print ("#5: See a table of the restaurants and their addresses.")

            while True:
                display_input = input("\n----------------------------------------\nPlease enter the number corresponding to the graph that you would like to see. ")

                try:
                    val = int(display_input)
                    make_restaurants_graphs(user_input, display_input)
                    break
                except ValueError:
                    print("Please enter a valid number!")
                    continue


            second_display_input = input("\n----------------------------------------\nIf you want to see another display, please type the number that corresponds to the display of information you want to see. \nOr, type 'specific restaurant' if you would like to see more information about a certain restaurant. \nType 'new location' if you would like to search a different location:")
            if second_display_input != "exit":
                try:
                    int(second_display_input) in range(1,5)
                    make_restaurants_graphs(user_input, second_display_input)
                except:
                    if second_display_input == 'new location':
                        continue
                    elif second_display_input == "specific restaurant":
                        pass
                    elif second_display_input == "exit":
                        exit()


            get_top_restaurants(user_input)
            while True:
                new_user_input = input("\n----------------------------------------\nPlease enter a number to see more information about a restaurant: ")
                try:
                    val = int(new_user_input)
                    break
                except ValueError:
                    print("Please enter a valid number!")
                    continue
            list_of_restauraunts = get_top_restaurants(user_input)
            name = list_of_restauraunts[int(new_user_input)][0]

            print ("\n----------------------------------------\nThe following are options that will provide you with information about the resturaunt: ")
            print ("#1: See {}'s website.".format(name))
            print ("#2: See {}'s phone number.".format(name))
            print ("#3: See {}'s menu.".format(name))
            print ("#4: See {}'s cuisine type.".format(name))

            while True:
                second_user_input = input("\n----------------------------------------\nPlease enter a number to choose which information about a restaurant you want to see: ")
                try:
                    val = int(second_user_input)
                    specific_restaurant_info(name, second_user_input)
                    break
                except ValueError:
                    print("Please enter a valid number!")
                    continue

            third_user_input = input("\n----------------------------------------\nIf you want to see more information, please enter another number to choose the information about a restaurant you want to see. \nOr, Type 'new location' if you would like to search a different location. \nType 'exit'if you would like to stop the program:  ")
            if third_user_input == "exit":
                exit()
            if third_user_input != "exit":
                try:
                    int(third_user_input) in range(1,5)
                    specific_restaurant_info(name, third_user_input)
                except:
                    if third_user_input == 'new location':
                        continue




if __name__=="__main__":
    interactive_prompt()
