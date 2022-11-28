import requests
from bs4 import BeautifulSoup
import statistics
from scipy import stats


def website_data(search):
    # URL contains search filters: used items, sold listings, and UK only
    url = f'https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw={search}' \
          f'&_in_kw=4&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&LH_ItemCondition=4&_samilow=&_samihi=&_stpos=M300AA' \
          f'&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1&_sop=12&_dmd=1&_ipg=60' \
          f'&LH_Complete=1&rt=nc&LH_PrefLoc=1'

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_data(soup):
    products = []
    results = soup.find('div', {'class': 'srp-river-results clearfix'}).find_all('li', {'class': 's-item '
                                                                                                 's-item__pl-on-bottom'})
    for item in results:
        price = item.find('span', class_='s-item__price').text.replace('£', '').replace(',', '')

        # Removing the results with that show a range of prices for the same listing
        # For example, £169.99 to £189.99
        if 'to' not in price:
            price = float(price)
            products.append(price)

    return products


def calculate_averages(products):
    median = statistics.median(products)
    mode = statistics.mode(products)

    # Mean must be trimmed as some outliers may exist in the search results
    # Trimming is set to 10%
    trim_percentage = 0.15
    trimmed_mean = stats.trim_mean(products, trim_percentage)

    return trim_percentage, trimmed_mean, median, mode
