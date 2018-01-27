# -*- coding: utf-8 -*-
#  This file is part of the ING-Scraper project (https://github.com/z3nk0/ING-Scraper).
#  Copyright (c) 2018 Manuel Jesús González Rodríguez.
 
#  This program is free software: you can redistribute it and/or modify  
#  it under the terms of the GNU General Public License as published by  
#  the Free Software Foundation, version 3.

#  This program is distributed in the hope that it will be useful, but 
#  WITHOUT ANY WARRANTY; without even the implied warranty of 
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
#  General Public License for more details.

#  You should have received a copy of the GNU General Public License 
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

FORMAT NOTES:

dni -> "123456789X"
birthday -> "dd/mm/aaaa"
password -> "123456"

'''
import json
import requests
import getpass

ENDPOINT_BASE = "https://ing.ingdirect.es"
ENDPOINTS = {
	"LOGIN" : ENDPOINT_BASE + "/genoma_login/rest/session",
	"POST_AUTH" : ENDPOINT_BASE + "/genoma_api/login/auth/response",
	"CLIENT" : ENDPOINT_BASE + "/genoma_api/rest/client",
	"PRODUCTS" : ENDPOINT_BASE + "/genoma_api/rest/products"
}

HEADERS = {
    'Accept' : 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/json; charset=utf-8'
}

verbose = False

def login_with_terminal(dni = None, birthday = None):
    log("Starting login process...")

    if dni is None or birthday is None:
        dni, birthday = set_login_data()

    pinpad_data, genoma_cookie = request_pinpad(dni, birthday)
    pin_positions = set_pinpad_positions(pinpad_data)
    ticket = request_ticket(pin_positions, genoma_cookie)
    auth_cookies = request_auth_cookies(ticket)
    log("Done")

    return auth_cookies

def login_auto(dni, birthday, password):
    numbers, positions, genoma_cookie = request_login_data(dni, birthday)
    
    if type(password) is not str:
        password = str(password)
    
    numbers = reverse_pinpad_numbers(numbers)
    positions = [numbers[int(password[i-1])] for i in positions]
    positions = list(map(int,positions))
    ticket = request_ticket(positions, genoma_cookie)
    auth_cookies = request_auth_cookies(ticket)
    return auth_cookies

def request_login_data(dni, birthday):
    log("Starting login process...")

    pinpad_data, genoma_cookie = request_pinpad(dni, birthday)
    numbers = pinpad_data["pinPadNumbers"]
    positions = pinpad_data["pinPositions"]
    return numbers, positions, genoma_cookie    

def send_login_data(pin_positions, genoma_cookie):
    ticket = request_ticket(pin_positions, genoma_cookie)
    auth_cookies = request_auth_cookies(ticket)
    log("Done")

    return auth_cookies

def set_login_data():
    log("Login Data")
    print("DNI: ", end='')
    dni = input()
    print("Birthday (dd/mm/aaaa): ", end='')
    birthday = input()
    return dni, birthday

def request_pinpad(dni, birthday):
    log("Requesting pinpad")
    url = ENDPOINTS["LOGIN"]
    headers = HEADERS
    payload = {
    	"device": "desktop",
    	"loginDocument": {
    		"document": dni,
    		"documentType": 0
    	},
    	"birthday": birthday
    }
    payload = json.dumps(payload)
    response = requests.post(url, headers = headers, data = payload)
    response_json = json.loads(response.text)
    if "errorCode" in response_json or "message" in response_json:
        print(response_json["message"])
        raise KeyError("API Error")
    cookies = response.cookies.get_dict()
    pinpad_data = {
        "pinPadNumbers": response_json["pinPadNumbers"],
        "pinPositions": response_json["pinPositions"],
    }
    genoma_cookie = {
        "genoma-session-id": cookies["genoma-session-id"]
    }
    return pinpad_data, genoma_cookie

def set_pinpad_positions(pinpad_data):
    numbers = pinpad_data["pinPadNumbers"]
    positions = pinpad_data["pinPositions"]
    reversed_numbers = reverse_pinpad_numbers(numbers)
    visual_pinpad = ["[ ]" if (n in positions) else "[*]" for n in range(1,7)]
    visual_pinpad = ''.join(visual_pinpad)
    print("Enter positions...")
    print(visual_pinpad)
    pin = []
    for position in positions:
        pin.append(int(getpass.getpass("Position " + str(position) + "  <-  ")))
    
    pin_positions = [ reversed_numbers[n] for n in pin]
    return pin_positions

def reverse_pinpad_numbers(pinpad_numbers):
    reversed_numbers = [0] * 10
    for i, number in enumerate(pinpad_numbers):
        reversed_numbers[number] = i
    return reversed_numbers


def request_ticket(pin_positions, cookie):
    log("Requesting ticket")
    log(pin_positions)
    url = ENDPOINTS["LOGIN"]
    headers = HEADERS
    payload = {
	    "pinPositions" : pin_positions
    }
    payload = json.dumps(payload)
    response = requests.put(url, headers = headers, data=payload, cookies = cookie)
    response_json = json.loads(response.text)
    if "errorCode" in response_json or "message" in response_json:
        print(response_json["message"])
        raise KeyError("API Error")
    ticket = response_json["ticket"]
    return ticket

def request_auth_cookies(ticket):
    log("Requesting auth cookies")
    url = ENDPOINTS["POST_AUTH"]
    headers = HEADERS.copy()
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    payload = "ticket=%s&device=desktop" % ticket
    response = requests.post(url, headers = headers, data = payload)
    cookies = response.cookies.get_dict()
    auth_cookies = {
        "Ucookie": cookies["Ucookie"],
        "genoma-session-id": cookies["genoma-session-id"]
    }
    return auth_cookies

def get_client(auth_cookies):
    return "TODO"

def get_products(auth_cookies):
    return "TODO"

def get_movements(auth_cookies, product, from_date, to_date):
    return "TODO"


# UTILS

def log(message, end = '\n'):
    if verbose:
        print(message, end = end)