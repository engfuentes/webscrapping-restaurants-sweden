import scrapy
from scrapy_playwright.page import PageMethod # To wait that the page loads
import re
from swedish_restaurants.items import RestaurantItem

class Swedish_Restaurant_Spider(scrapy.Spider):
    name = "swedish_restaurant_financial_spider"

    def __init__(self):
        self.count = 1

    def start_requests(self):
        """Starts the request"""
        yield scrapy.Request("https://www.eniro.se/pizza/f%C3%B6retag",
                              meta={"playwright": True})#,
                                    #"playwright_page_methods": [PageMethod("wait_for_selector", "div#flex flex-col gap-4")] })

    def parse(self, response):
        """Parse the page with the list of pizza shops"""
        # Get the container
        restaurants_containers = response.css("div.relative a.absolute")

        # Get the link for each restaurant
        for restaurant in restaurants_containers:
            relative_url = restaurant.attrib['href']

            # Get the complete url for that restaurant
            restaurant_url = "https://www.eniro.se/" + relative_url

            # scrape the restaurant page with the other function
            yield response.follow(restaurant_url, callback=self.parse_restaurant_page) 

        # Get the total number of pages to scrap
        number_pages_to_scrap = int(response.xpath('//*[@id="company-result-page-scrollable-root"]/div/section[1]/nav/div[3]/a[2]').attrib['href'].split('/')[-1])

        # Scrap the rest of the pages of the main website 
        if self.count <= number_pages_to_scrap:
            next_page_url = f'https://www.eniro.se/pizza/f%C3%B6retag/{self.count + 1}'
            self.count +=1
            print(self.count)
            yield response.follow(next_page_url, callback=self.parse) # Continue and scrape the next page

    def parse_restaurant_page(self, response):
        """Scrap the restaurant page of the main website"""

        # Get the 2 parts of the address
        address_1 = response.xpath('//*[@id="__next"]/div/div/div/div[3]/div/main/div/aside/div[2]/div[2]/div/p[2]/text()').get()
        address_2 = response.xpath('//*[@id="__next"]/div/div/div/div[3]/div/main/div/aside/div[2]/div[2]/div/p[3]/text()').get()
        
        # Get all the links that are in the page and search for the link that takes to the website with financial data
        list_links = response.css('a::attr(href)').getall()
        url_financial_data = [i for i in list_links if i.startswith('https://www.proff.se/foretag')][0]
        
        # Check if the website has its own website
        try:
            restaurant_url = response.xpath('//*[@id="__next"]/div/div/div/div[3]/div/main/div/aside/div[1]/div[2]/a').attrib['href']
        except:
            restaurant_url = None

        # Create meta information to pass to the next function
        meta = {
        'name': response.css("section h1::text").get(),
        'type': response.css("section a::text").getall()[0],
        'city': response.css("section a::text").getall()[1],
        'url': restaurant_url,
        'address': ", ".join([address_1, address_2]),
        'url_financial_data': url_financial_data
        }
        
        # If the restaurant has its own website check if it has an email in the main page
        if restaurant_url:
            try:
                # Tr if the restaurant url works, because it doesnt for some restaurants
                yield response.follow(restaurant_url, callback=self.parse_url_page, meta=meta)
            except:
                meta['email'] = None
                try:
                    # Try to get the financial data of the restaurant
                    yield response.follow(meta['url_financial_data'], callback=self.parse_financial_page, meta=meta)  
                except:
                    # If cant then save info that could be scrapped to the item
                    restaurant_item = RestaurantItem() 
                    meta_info_keys = ['name', 'type', 'city', 'url', 'address']
                    for key in meta_info_keys:
                        restaurant_item[key] = response.meta[key]
                    
                    yield restaurant_item
        else:
            meta['email'] = None
            try:
                # Try to get the financial data of the restaurant
                yield response.follow(meta['url_financial_data'], callback=self.parse_financial_page, meta=meta)  
            except:
                # If cant then save info that could be scrapped to the item
                restaurant_item = RestaurantItem() 
                meta_info_keys = ['name', 'type', 'city', 'url', 'address']
                for key in meta_info_keys:
                    restaurant_item[key] = response.meta[key]
                
                yield restaurant_item

    def parse_url_page(self, response):
        """Scrap the restaurant main website to get the contact email"""
        
        # Get the meta and the urls that are needed
        meta = response.meta.copy()
        restaurant_url = response.meta.get('url')
        url_financial_data = response.meta.get('url_financial_data')
        
        # Get the possible end of the email from the website name without the https://www.
        email_end = '@' + restaurant_url.split('/')[2].replace("www.","")
        # Get the parts of the website that have the email_end as text
        page_possible_texts = response.xpath(f"//*[contains(text(), '{email_end}')]").getall()
        
        # Search if there is only one piece of text
        if len(page_possible_texts) == 1:
            # Find the possible email and append to the meta
            email = re.findall(f"([a-zA-Z0-9_.+-]+{email_end})", page_possible_texts[0])
            meta['email'] = email[0]
            try:
                # Continue to try to scrape the financial data
                yield response.follow(url_financial_data, callback=self.parse_financial_page, meta=meta) 
            except:
                pass
        # Search if there are more pieces of data
        elif len(page_possible_texts) > 1:
            # Find the possible email and save to a list
            possible_emails = list()
            for page_possible_text in page_possible_texts:
                email = re.findall(f"([a-zA-Z0-9_.+-]+{email_end})", page_possible_text)
                possible_emails.append(email[0])
            try:
                meta['email'] = possible_emails
                # Continue to try to scrape the financial data
                yield response.follow(url_financial_data, callback=self.parse_financial_page, meta=meta) 
            except:
                pass
        # Last case where it didnt find any text with a possible email
        else:
            meta['email'] = None
            try:
                # Continue to try to scrape the financial data
                yield response.follow(url_financial_data, callback=self.parse_financial_page, meta=meta) 
            except:
                pass

    def parse_financial_page(self, response):
        """Scrape the website that has financial data of the restaurant"""     
        restaurant_item = RestaurantItem()
        
        # Get the meta info to the item
        meta_info_keys = ['name', 'type', 'city', 'url', 'address', 'email']
        for key in meta_info_keys:
            restaurant_item[key] = response.meta.get(key)
        
        try:
            # Scrape the financial data to the item
            restaurant_item['num_employees'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[3]/div/div[5]/span[2]/text()').get()
            restaurant_item['telephone'] = response.xpath('//*[@id="__next"]/main/div/div/div/div/div[1]/div[1]/div[2]/div[3]/div[1]/span[2]/a/text()').get()
            restaurant_item['last_year_revenue'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[3]/div/div[1]/div/span[2]/text()').get()
            restaurant_item['last_year_result_after_financial_assets'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[3]/div/div[2]/div/span[2]/text()').get()
            restaurant_item['cash_flow_word'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[4]/div[1]/div/div[2]/div/div/div[2]/span[1]/div/b/text()').get()
            restaurant_item['cash_flow_percent'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[4]/div[1]/div/div[2]/div/div/div[2]/span[1]/text()').get()
            restaurant_item['profit_margin_word'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[4]/div[1]/div/div[3]/div/div/div[2]/span[1]/div/b/text()').get()
            restaurant_item['profit_margin_percent'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[4]/div[1]/div/div[3]/div/div/div[2]/span[1]/text()').get()
            restaurant_item['solidity_word'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[4]/div[1]/div/div[4]/div/div/div[2]/span[1]/div/b/text()').get()
            restaurant_item['solidity_percent'] = response.xpath('//*[@id="scrollable-auto-tabpanel-0"]/div/div[1]/div[1]/div/div[4]/div[1]/div/div[4]/div/div/div[2]/span[1]/text()').get()
        except:
            pass
        
        yield restaurant_item