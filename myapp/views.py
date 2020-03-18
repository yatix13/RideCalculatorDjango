import json
from django.shortcuts import render
# Create your views here.
from bs4 import BeautifulSoup
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from .models import FuelPrices
from django.http import HttpResponse
import requests
from django.core import serializers

@never_cache
@csrf_exempt
def updateCurrentFuelPrices(request):
    #petrol
    URL = 'https://www.bankbazaar.com/fuel/petrol-price-india.html'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find("div", {"class": "gold-rate-table"})
    print(results.prettify())

    data = []
    prices = dict()
    table = soup.find('table', attrs={'class': 'table table-curved tabdetails heightcontroltable'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        prices[cols[0]] = cols[1]
        data.append([ele for ele in cols if ele])  # Get rid
    #petrol
    # import these petrol prices in FuelPrices table -> type petrol
    for key in prices.keys():
        cityname = key
        fuelprice = prices[key]
        if fuelprice == 'Petrol ( / litre)':
            continue
        price = float(fuelprice[2:])

        if FuelPrices.objects.filter(city=cityname, fuel_type=1).exists():
            #update
            FuelPrices.objects.filter(city=cityname,fuel_type=1).update(price=price)
        else:
            #create new record
            fp = FuelPrices(city=cityname, price=price, fuel_type=1)
            fp.save()

    #diesel
    URL = 'https://www.bankbazaar.com/fuel/diesel-price-india.html'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find("div", {"class": "gold-rate-table"})
    print(results.prettify())

    data = []
    prices = dict()
    table = soup.find('table', attrs={'class': 'table table-curved tabdetails heightcontroltable'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        prices[cols[0]] = cols[1]
        data.append([ele for ele in cols if ele])  # Get rid

    # import these petrol prices in FuelPrices table -> type petrol
    for key in prices.keys():
        cityname = key
        fuelprice = prices[key]
        if fuelprice == 'Diesel ( / litre)':
            continue
        price = float(fuelprice[2:])

        if FuelPrices.objects.filter(city=cityname, fuel_type=2).exists():
            # update
            FuelPrices.objects.filter(city=cityname, fuel_type=2).update(price=price)
        else:
            # create new record
            fp = FuelPrices(city=cityname, price=price, fuel_type=2)
            fp.save()


    response = dict()
    response['data'] = 'ok'
    return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
@never_cache
def fetchFuelPrice(request):
    req = request.POST
    city = req['city']
    fuel_type = req['fuel_type']

    type = 1
    if fuel_type == "Diesel":
        type = 2
    elif fuel_type == "CNG":
        type = 3

    query_set = FuelPrices.objects.filter(city=city, fuel_type=type)
    json_data = serializers.serialize('json',query_set)
    data = json.loads(json_data)

    print('data = ',data)
    data = data[0]
    mydata = dict()
    mydata['id'] = data['pk']
    fields = data['fields']
    mydata['city'] = fields['city']
    mydata['price'] = fields['price']
    fuel_type = fields['fuel_type']
    if fuel_type == 1:
        mydata['fuel_type'] = 'Petrol'
    elif fuel_type == 2:
        mydata['fuel_type'] = 'Diesel'
    else:
        mydata['fuel_type'] = 'CNG'

    return HttpResponse(json.dumps(mydata), content_type='application/json')






