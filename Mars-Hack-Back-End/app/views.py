"""
Definition of views.
"""

import requests
import datetime
import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from datetime import datetime

from app.models import User
from app.models import Product
from app.models import OrderIndividual

#yeah, yeah don't put api keys in the code, it's not like this cost money or anything
API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJDQlAiLCJ0ZWFtX2lkIjoiMTQwZWQwNWItOGI1OS0zNmY4LThjMmEtZmQ1NzVmNGZiMWQzIiwiZXhwIjo5MjIzMzcyMDM2ODU0Nzc1LCJhcHBfaWQiOiI1YmJhNDEzOS0xZWU3LTRhYzItOGU3Ny03MmVkM2Y2YjVhMTgifQ.qUk5SyVTtqvtNFw4kXrM_FWnjP77B2P1UJe_UMbFXoQ'

DATE_FORMAT = '%Y-%m-%d'

def make_td_request(endpoint, params=None):
    url = 'https://api.td-davinci.com/api/' + endpoint
    response = requests.get(url, headers = { 'Authorization': API_KEY }, params=params)
    return response.json()

def home(request):
    return HttpResponse(r'<h1>HAIL SATAN</h1>')

@csrf_exempt
def load_user_from_api(request, **kwargs):
    if request.method != 'POST':
        return HttpResponseBadRequest(content='Invalid request method.')
    cust_id = kwargs['cust_id']
    endpoint = f'customers/{cust_id}'
    response = make_td_request(endpoint)
    if response.get('errorMsg') == 'Invalid ID':
        return HttpResponseBadRequest(content='Invalid customer ID.')
    user = User()
    user_json = response['result']
    user.customer_id = cust_id
    user.income = int(user_json['totalIncome'])
    user.gender = user_json['gender']
    user.first_name = user_json['givenName']
    user.last_name = user_json['surname']
    user.latitude = user_json['addresses']['principalResidence']['latitude']
    user.longitude = user_json['addresses']['principalResidence']['longitude']
    try:
        user.save()
    except IntegrityError as e:
        return HttpResponseBadRequest(content='Error: customer already present in database.')
    return HttpResponse()

@csrf_exempt
def get_products(request):
    if request.method != 'GET':
        return HttpResponseBadRequest(content='Invalid request method.')
    return HttpResponse(serializers.serialize('json', Product.objects.all()), content_type='application/json')

@csrf_exempt
def create_order(request):
    order_json = json.loads(request.body.decode('utf-8'))
    if request.method != 'POST':
        return HttpResponseBadRequest(content='Invalid request method.')
    try:
        product = Product.objects.get(id=order_json['product_id'])
        user = User.objects.get(customer_id=order_json['user_id'])
    except KeyError:
        return HttpResponseBadRequest('No product or user id.')
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Could not find product or user.')
    try:
        start_date = datetime.strptime(order_json['start_date'], DATE_FORMAT)
        end_date = datetime.strptime(order_json['end_date'], DATE_FORMAT)
    except KeyError:
        return HttpResponseBadRequest('No start or end date.')
    except ValueError:
        return HttpResponseBadRequest('Invalid date format.')
    order = OrderIndividual(
        product=product,
        user=user,
        percentage=int(order_json['percentage']),
        delivery_begin=start_date,
        delivery_end=end_date,
        can_deliver=order_json['can_deliver'])
    order.save()
    return HttpResponse()