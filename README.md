# Web scraping and Data Analysis project of Swedish Restaurants that sell pizza

## Web Scraping
There is a website (https://www.eniro.se/pizza/företag) that has a list of restaurants that sell pizza in Sweden. This website has a JS rendering so is not possible to get the information with *request* and *beautiful soup* libraries directly.

To Scrap the information from the different pages is used the **Scrapy Framework**. And to solve the problem of the JS rendering I use the **scrapy-playwright** library that allows to use playwright with Scrapy. To be able to use this library the script must be run on wsl or linux.

**Restaurant contact information**:
The spider gathers the information from the main pages and then request the eniro's restaurant pages to gather more information. From this pages it gets data like name, type, city, adddress, etc.

**Restaurant financial information**:
The spider also scrap a website with the restaurant's financial information. For example last year revenue, last year result after financial assets, cashflow, profit margin, etc.

**Restaurant email contact**:
Finally, the spider also Scrap the restaurant main website, if it has one, to search for the email to contact them.

### Data pipeline
The data that was obtained by the spider is processed in a **Scrapy Pipeline** and after is saved as a json file.

## Data Analysis
For the Data Analysis a **Jupyter Notebook** is utilized.

First the json file is loaded to the notebook with **pandas** library. Then I use **geocoder** library to get the Latitude and Longitude from the restaurant and from the cities. I also load the Swedish population from another website and combine all the data to a new DataFrame and save it as a json file.

Secondly, there is some data processing, to reduce the quantity of restaurant types, and to categorize some of the information, for example restaurant url, email and telephone. There is a cleaning stage to quit the rows with na values.

After, is used the **seaborn** library to detect and eliminate possible outliers and to analyze the relationship between the last year revenue and the number of employees.

Finally, the data is grouped by cities to analyse the average values of each city. **plotly** library is utilized to generate 2 interactive maps where can be seen the locations of each city, the quantity of employees and in one map the last year revenue and in the other the last year result after financial assets. It is also detected which are the cities with the best revenues and results.

![Average Revenue by city](<img/Average Revenue by city.png>)

![Average Result After Financial Assets by city](<img/Average Result After Financial Assets by city.png>)