#!/usr/bin/env python
import requests
import webbrowser
from bs4 import BeautifulSoup


GENERAL = {
    'mileage-to': 60000,
    'price-to': 6000,
    'region': 3  # athens, hardcoded
}

MODELS = [
    {
        'make': 'toyota',
        'model': 'yaris',
        'registration-from': '2007',
    },
    {
        'make': 'volkswagen',
        'model': 'polo',
        'registration-from': '2010',
    },
    {
        'make': 'hyundai',
        'model': 'i 20',
        'registration-from': '2009',
    },
    {
        'make': 'suzuki',
        'model': 'swift',
        'registration-from': '2009',
    },
    {
        'make': 'suzuki',
        'model': 'splash',
        'registration-from': '2008',
    },
    {
        'make': 'opel',
        'model': 'corsa',
        'registration-from': '2008',
    },
    {
        'make': 'opel',
        'model': 'agila',
        'registration-from': '2008',
    },
]

html_headers = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Results</title></head><body>'
html_footer = '</body></html>'


def create_request(model):
    url = 'http://www.car.gr/classifieds/cars/?fs=1&price-with=>1&category=&make=%s&model=%s&variant=&price-from=&price-to=<%s&registration-from=>%s&registration-to=&mileage-from=&mileage-to=<%s&engine_power-from=&engine_power-to=&engine_size-from=&engine_size-to=&fuel_type=&exterior_color=&significant_damage=f&doors=4-5&number_plate_ending=&gearbox_type=&drive_type=&euroclass=&airbags-ranged=&kteo=&seats-from=&seats-to=&sort=&rg=%s&radius=&postcode=&modified=&hi=&st=&offer_type=sale' % (model.get('make-code'), model.get('model-code'), GENERAL.get('price-to'), model.get('registration-from'), GENERAL.get('mileage-to'), GENERAL.get('region'))
    return url


def get_car_make(make):
    soup = BeautifulSoup(requests.get('http://www.car.gr/classifieds/cars/search/').text)
    options = soup.find_all('select', {'name': 'make'})[0].find_all('option')
    for option in options:
        if option.text == make.capitalize():
            return option['value']
    return False


def get_car_model(make, wanted_model):
    models = requests.get('http://www.car.gr/classifieds/cars/models/%s/?e' % (make)).json()
    for model in models.get('models'):
        if model[0].split('|')[0] == wanted_model.capitalize():
            return model[0].split('|')[1]
    return False


if __name__ == '__main__':
    results = []
    html = ''
    for car in MODELS:
        car['make-code'] = get_car_make(car.get('make'))
        car['model-code'] = get_car_model(car.get('make-code'), car.get('model'))
        response = requests.get(create_request(car))
        soup = BeautifulSoup(response.text)
        rows = soup.find_all('a', {'class': 'vehicle'})
        for row in rows:
            release_date = row.find_all('span', {'itemprop': 'releaseDate'})[0].text
            price = row.find_all('span', {'itemprop': 'price'})[0].text
            mileage = row.find_all('div', {'class': 'mileage'})[0].text
            row['href'] = 'http://car.gr%s' % row['href'],
            result = {
                'make': car.get('make'),
                'model': car.get('model'),
                'date': release_date,
                'price': price,
                'km': mileage.strip(),
                'url': row['href'],
                'html': row.prettify()
            }
            results.append(result)
    for r in results:
        html += '<a href="%s">%s</a>' % (r.get('url'), r.get('html'))
    final_html = '%s%s%s' % (html_headers, html.encode('utf-8'), html_footer)
    with open('/tmp/car.html', 'w') as f:
        f.write(final_html)
        webbrowser.open('file:///tmp/car.html')
