Charlotte Wittels
SI Final Project
4/18/18

For my final project, I decided to construct a program that provides people with information about restaurants in a specific area. I drew information from Yelp by scraping and crawling the site.

I broke my code up into different functions. My first function, get_yelp_info, creates database tables and scrapes Yelp. My second function, get_top_restaurants, returns the name and rating for the top ten restaurants. In this function, I also created a list of each restaurant and their ratings. The next function, make_restaurants_graphs, is where I create my displays with my data. I created five different graphs as I did not include a class in my code. My last two functions work together to return specific information about a certain restaurant.

First, the code will prompt you to enter a location to see the top 10 restaurants in that area. After you type your location, you will see a list of the top 10 restaurants in that locations based on their ratings.

Next, you will see five display options. You will be prompted to enter a number that corresponds to a certain graph, which will open the specific graph through Plotly on your browser. You are given the opportunity to see another display, can continue on in the program by typing "specific restaurant", or can type "new location" if you want to restart the code and see restaurants for a different location.

After this section, you will again see the list of the top ten restaurants, and can then type in a number to chose a certain restaurant. After you pick your restaurant, you will see four options that will provide you with additional information about a restaurant. You will type in a number corresponding to the information that you want to see, which includes its website (this option will open their website on your browser), phone number, menu (this option will open their menu from yelp on your browser), or cuisine type.
