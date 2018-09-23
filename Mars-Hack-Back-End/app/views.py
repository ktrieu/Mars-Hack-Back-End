"""
Definition of views.
"""

import requests
import datetime
from datetime import date, timedelta
import json
import random
import decimal

import app.matcher

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.datastructures import MultiValueDictKeyError
from django.forms.models import model_to_dict
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
from app.models import OrderCombined
from app.models import OrderCombinedUser

#yeah, yeah don't put api keys in the code, it's not like this cost money or anything
API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJDQlAiLCJ0ZWFtX2lkIjoiMTQwZWQwNWItOGI1OS0zNmY4LThjMmEtZmQ1NzVmNGZiMWQzIiwiZXhwIjo5MjIzMzcyMDM2ODU0Nzc1LCJhcHBfaWQiOiI5MTZhNTg0NC1mMDM5LTQ4OTktOTA2OC1mNWYzNzk5NjBkNDgifQ.3FlPR9skHrQvrTbQ7pUTpcgbc2GipwNTxt0CzUXtSb4'

DATE_FORMAT = '%Y-%m-%d'

def make_td_request(method, endpoint, params=None):
    url = 'https://api.td-davinci.com/api/' + endpoint
    if method == 'GET':
        response = requests.get(url, headers = { 'Authorization': API_KEY }, params=params)
    elif method == 'POST':
        response = requests.post(url, headers = { 'Authorization': API_KEY }, json=params)
    return response.json()

#returns a user by TD id or by database pk
def get_user_by_id(id):
    #first try to retrieve by pk
    try:
        user = User.objects.get(pk=id)
    except (ObjectDoesNotExist, ValueError):
        user = User.objects.get(customer_id=id)
    return user

def home(request):
    return HttpResponse(r'<h1>SNAP BACK TO REALITY OH THERE GOES GRAVITY</h1>')

@csrf_exempt
def make_payment(user_id, amount, reason):
    account_id = make_td_request('GET', "customers/" + str(user_id) + "/accounts")

    transaction_info = {
        "amount": amount,
        "currency": "CAD",
        "fromAccountID": account_id['result']['bankAccounts'][0]['id'],
        "receipt": json.dumps({ 'reason' : reason }),
        "toAccountID": "1a4335bb-0986-4cc1-981b-3df0891f0369"
    }
    receipt = make_td_request('POST',"transfers", transaction_info)
    if (receipt['statusCode'] != 200):
        print(receipt)

@csrf_exempt
def release_funds(user_id, amount, reason):
    account_id = make_td_request('GET', "customers/" + str(user_id) + "/accounts")

    transaction_info = {
        "amount": amount,
        "currency": "CAD",
        "fromAccountID": "1a4335bb-0986-4cc1-981b-3df0891f0369",
        "receipt": json.dumps({ 'reason' : reason }),
        "toAccountID": account_id['result']['bankAccounts'][0]['id']
    }
    receipt = make_td_request('POST', "transfers", transaction_info)
    if (receipt['statusCode'] != 200):
        print(receipt)

@csrf_exempt
def load_user_from_api(request, **kwargs):
    if request.method != 'POST':
        return HttpResponseBadRequest(content='Invalid request method.')
    cust_id = kwargs['cust_id']
    endpoint = f'customers/{cust_id}'
    response = make_td_request('GET', endpoint)
    if response.get('errorMsg') == 'Invalid ID':
        return HttpResponseBadRequest(content='Invalid customer ID.')
    user = User()
    user_json = response['result']
    user.customer_id = cust_id
    user.income = int(user_json['totalIncome'])
    user.gender = user_json['gender']
    user.first_name = user_json['givenName']
    user.last_name = user_json['surname']
    principal_res = user_json['addresses']['principalResidence']
    user.latitude = principal_res['latitude']
    user.longitude = principal_res['longitude']
    user.address = f'{principal_res["streetNumber"]} {principal_res["streetName"]}, {principal_res["municipality"]}'
    try:
        user.save()
    except IntegrityError as e:
        return HttpResponseBadRequest(content='Error: customer already present in database.')
    return HttpResponse()

@csrf_exempt
def get_user(request, **kwargs):
    user = get_user_by_id(kwargs['cust_id'])
    return HttpResponse(serializers.serialize('json', [user]), content_type='application/json')

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

    return HttpResponse(order.pk)

@csrf_exempt
def get_order(request, **kwargs):
    id = kwargs['order_id']
    try:
        order = OrderIndividual.objects.get(pk=id)
    except:
        return HttpResponseBadRequest('Order not found.')
    order_json = serializers.serialize('json', [order])
    return HttpResponse(order_json, content_type='application/json')

@csrf_exempt
def get_orders(request):
    return HttpResponse(serializers.serialize('json', OrderIndividual.objects.all()), content_type='application/json')

@csrf_exempt
def cust_orders(request, **kwargs):
    user = get_user_by_id(kwargs['cust_id'])
    return HttpResponse(serializers.serialize('json', user.orderindividual_set.all()), content_type='application/json')

def cust_orders_merged(request, **kwargs):
    user = get_user_by_id(kwargs['cust_id'])
    related_combined = list()
    for combined_user in user.ordercombineduser_set.all():
        related_combined.append(combined_user.order)
    json_list = list()
    for combined in related_combined:
        #activate shitton of json
        json_combined = dict()
        json_combined.update(model_to_dict(combined))
        #add top-level combined order info
        json_combined['product'] = model_to_dict(combined.product)
        json_combined['users'] = list()
        #iterate through combined order through field
        for order_user in combined.ordercombineduser_set.all():
            order_user_dict = model_to_dict(order_user)
            order_user_dict['user'] = model_to_dict(order_user.user)
            json_combined['users'].append(order_user_dict)
        json_list.append(json_combined)
    return JsonResponse(json_list, safe = False)

@csrf_exempt
def demo_create_random_order(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Incorrect request method.')
    user = User.objects.order_by('?')[0]
    product = Product.objects.order_by('?')[0]
    percentage = random.choice([25, 50, 75])
    start_date = date.today()
    start_date += timedelta(days=random.randint(-2, 2))
    end_date = date.today() + timedelta(days=7)
    end_date += timedelta(days=random.randint(-2, 2))
    order = OrderIndividual()
    order.user = user
    order.product = product
    order.percentage = percentage
    order.delivery_begin = start_date
    order.delivery_end = end_date
    order.can_deliver = random.choice([True, False])
    order.save()
    return HttpResponse(order.pk)

def build_merged_order(group):
    combined = OrderCombined()
    combined.product = group.deliverer.product
    combined.date = group.date
    combined.save()
    #add the deliverer
    deliverer_user = OrderCombinedUser()
    deliverer_user.order = combined
    deliverer_user.user = group.deliverer.user
    deliverer_user.is_deliverer = True
    deliverer_user.is_complete = False
    deliverer_user.percentage = group.deliverer.percentage
    #add the receivers
    receiver_users = list()
    for receiver in group.receivers:
        receiver_user = OrderCombinedUser()
        receiver_user.user = receiver.user
        receiver_user.order = combined
        receiver_user.percentage = receiver.percentage
        receiver_user.is_deliverer = False
        receiver_user.is_complete = False
        receiver_users.append(receiver_user)
    #calculate payment
    total_price = combined.product.price
    deliverer_discount = total_price * decimal.Decimal(0.1)
    deliverer_user.payment = ((deliverer_user.percentage / decimal.Decimal(100)) * total_price) - deliverer_discount
    make_payment(deliverer_user.user.customer_id, float(deliverer_user.payment), 'MARS-HACK-PAY')
    deliverer_user.save()
    for receiver in receiver_users:
        receiver.payment = ((receiver.percentage / decimal.Decimal(100)) * total_price) + (deliverer_discount / len(receiver_users))
        receiver.save()
        make_payment(receiver.user.customer_id, float(receiver.payment), 'MARS-HACK-PAY')
    combined.save()
    group.deliverer.delete()
    for receiver in group.receivers:
        receiver.delete()

@csrf_exempt
def group_orders(request):
    groups = app.matcher.find_groups(OrderIndividual.objects.all())
    for group in groups:
        build_merged_order(group)
    return HttpResponse(f'{len(groups)} groups merged.')

def close_order(order):
    #TODO: actually close order
    for order_user in order.ordercombineduser_set.all():
        if order_user.is_deliverer:
            release_funds(order_user.user.customer_id, float(order.product.price), 'MARS-HACK-PAY')
    order.delete()

@csrf_exempt
def complete_order(request, **kwargs):
    order_id = kwargs['order_id']
    combined_order = OrderCombined.objects.get(pk=order_id)
    fully_complete = True
    for order_user in combined_order.ordercombineduser_set.all():
        if order_user.user.customer_id == kwargs['cust_id']:
            order_user.is_complete = True
        if not order_user.is_complete:
            fully_complete = False
        order_user.save()
    if fully_complete:
        close_order(combined_order)
        return HttpResponse('Order closed,')
    return HttpResponse('Order not closed.')


