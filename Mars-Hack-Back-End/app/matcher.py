import requests
import datetime
from math import sin, cos, sqrt, atan2, radians
import geopy.distance

class Group:

    def  __init__(self):
        self.deliverer = None
        self.receivers = list()
        self.percentage = 0

def date_matches (deliverer, receiver):
    deliverer_time_start = deliverer.delivery_begin
    deliverer_time_end = deliverer.delivery_end
    receiver_time_start = receiver.delivery_begin
    receiver_time_end = receiver.delivery_end

    return (deliverer_time_start <= receiver_time_end and deliverer_time_end >= receiver_time_start)

def distance_in_km(coord1x, coord1y, coord2x, coord2y):
    coords_1 = (coord1x, coord1y)
    coords_2 = (coord2x, coord2y)
    return geopy.distance.vincenty(coords_1, coords_2).km

#Check for possible deliverers
def find_groups(individual_orders):

    deliverer_list = list()
    receiver_list = list()

    for order in individual_orders:
        if order.can_deliver:
            deliverer_list.append(order)
        else:
            receiver_list.append(order)

    deliverer_list_sorted = sorted(deliverer_list, key=lambda k: k.product.pk)
    receiver_list_sorted = sorted(receiver_list, key=lambda k: k.product.pk)
    return find_receiver_match_deliverer(deliverer_list_sorted, receiver_list_sorted)

def find_receiver_match_deliverer(dlist_sorted, rlist_sorted):
    occupied = set()
    origin_dists = dict()
    group_list = []

    for deliverer in dlist_sorted:
        if deliverer in occupied:
            continue
        group = Group()
        current_percent = deliverer.percentage
        group.deliverer = deliverer
        receivers = []
        deliverer_x = deliverer.user.latitude
        deliverer_y = deliverer.user.longitude
        alone = True

        for receiver in rlist_sorted:
            if (current_percent + receiver.percentage > 100):
                continue
            if (receiver in occupied):
                continue
            if (not (date_matches(deliverer, receiver))):
                continue
            if (deliverer.product == receiver.product):
                receiver_x = receiver.user.latitude
                receiver_y = receiver.user.longitude
                distance = distance_in_km(receiver_x, receiver_y, deliverer_x, deliverer_y)
                if (distance <= 10):
                    alone = False
                    current_percent = current_percent + receiver.percentage
                    receivers.append(receiver)
                    occupied.add(receiver)
                    origin_dists[receiver] = distance


        group.receivers = receivers
        group.percentage = current_percent
        if not alone:
          occupied.add(deliverer)
          group_list.append(group)
        receivers = []

    return group_list