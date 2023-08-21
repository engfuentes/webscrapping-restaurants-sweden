# Web scraping project of Swedish Restaurants that sell pizza

Web scraping of different pages of a website with Scrapy. It gathers name, type, city, adddress, etc.
It is also scraped another website for financial information of the restaurant and the own restaurant main website searching for their email contact.
The data that is obtained is processed in a Scrapy pipeline and saved to a json file.

To get the information from the javascript website is used the scrapy-playwright library that allows to use playwright with scrapy. To be able to use this library is necesary to run the program in wsl or linux.

Next stage: Analyze the data with pandas and seaborn libraries.