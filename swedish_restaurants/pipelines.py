# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class SwedishRestaurantsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item) # with the adapter we can get the field names and loop between them
        field_names = adapter.field_names()

        ## Capitalize every word of the restaurant and city names
        capitalize_keys = ['name', 'city']
        for capitalize_key in capitalize_keys:
            name_string = adapter.get(capitalize_key)
            capitalized_name = name_string.title()
            adapter[capitalize_key] = capitalized_name

        ## Change type names to english
        type_string = adapter.get('type')
        if type_string == 'Restaurang' or 'restaurang' in type_string.lower():
            adapter['type'] = 'Restaurant'
        elif 'pizza' in type_string.lower() or 'pizzeria' in type_string.lower():
            adapter['type'] = 'Pizzeria'
        else:
            adapter['type'] = 'Other'


        ## Change type to int
        int_keys = ['num_employees', 'last_year_revenue', 'last_year_result_after_financial_assets']
        for int_key in int_keys:
            if adapter[int_key] is not None:
                int_string = adapter.get(int_key).replace('\xa0','').replace('\u2212','-')
                adapter[int_key] = int(float(int_string))

        ## Change words from Swedish to English
        translate_keys = ['cash_flow_word','profit_margin_word','solidity_word']
        for translate_key in translate_keys:
            if adapter[translate_key] is not None:
                if adapter[translate_key] == 'Mycket bra' or 'verygood' in (adapter[translate_key]).lower():
                    adapter[translate_key] = 'Very Good'
                elif adapter[translate_key] == 'Svag' or 'weak' in (adapter[translate_key]).lower():
                    adapter[translate_key] = 'Weak'
                elif adapter[translate_key] == 'Bra' or 'good' in (adapter[translate_key]).lower():
                    adapter[translate_key] = 'Good'
                elif adapter[translate_key] == 'Inte tillfredsst.' or 'notsatisfactory' in (adapter[translate_key]).lower():
                    adapter[translate_key] = 'Not Satisfactory'
                elif adapter[translate_key] == 'Tillfredsst.' or 'satisfactory' in (adapter[translate_key]).lower():
                    adapter[translate_key] = 'Satisfactory'

        # Change numbers to float
        float_keys = ['cash_flow_percent','profit_margin_percent','solidity_percent']
        for float_key in float_keys:
            if adapter[float_key] is not None:
                float_string = adapter[float_key].replace(',','.').replace(' %','').replace('\u2212','-')
                adapter[float_key] = float(float_string) 
        
        # Delete repeated emails
        emails = adapter.get('email')
        if type(emails) == list and len(emails) > 1:
            set_emails = set(emails)
            if len(set_emails) == 1:
                adapter['email'] = next(iter(set_emails))
            else:
                adapter['email'] = set_emails
        
        return item
        

class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item) # with the adapter we can get the field names and loop between them

        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        ## Category & Product Type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        ## Price --> convert to float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)
        
        ## Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])