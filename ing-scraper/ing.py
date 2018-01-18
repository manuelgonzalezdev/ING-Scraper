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
import json
import requests

ENDPOINT_BASE = "https://ing.ingdirect.es"
ENDPOINTS = {
	"LOGIN" : ENDPOINT_BASE + "/genoma_login/rest/session",
	"POST_AUTH" : ENDPOINT_BASE + "/genoma_api/login/auth/response",
	"CLIENT" : ENDPOINT_BASE + "/genoma_api/rest/client",
	"PRODUCTS" : ENDPOINT_BASE + "/genoma_api/rest/products"
}

verbose = True

def login():

    def set_login_data():
        print("DNI: ", end='')
        dni = input()
        print("Birthday (dd/mm/aaaa): ", end='')
        birthday = input()
        return [dni, birthday]

    def request_pinpad(login_data):
        
        dni = login_data[0]
        birthday = login_data[1]

        url = ENDPOINTS["LOGIN"]

        headers = {
            'Content-Type': 'application/json'
        }

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

        reversed_numbers = [0] * 10
        for i, number in enumerate(numbers):
            reversed_numbers[number] = i

        visual_pinpad = ["[ ]" if (n in positions) else "[*]" for n in range(1,7)]
        visual_pinpad = ''.join(visual_pinpad)
        print("Enter positions...")
        print(visual_pinpad)
        pin = []
        for position in positions:
            print("Position " + str(position) + "  <-  ", end='')
            pin.append(int(input()))
        
        pin_positions = [ reversed_numbers[n] for n in pin]
        
        return pin_positions

    def request_ticket(pin_positions, cookie):
        url = ENDPOINTS["LOGIN"]

        headers = {
		    'Accept' : 'application/json, text/javascript, */*; q=0.01',
    	    'Content-Type': 'application/json; charset=utf-8'
	    }

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
        url = ENDPOINTS["POST_AUTH"]

        headers = {
		    'Accept' : 'application/json, text/javascript, */*; q=0.01',
	        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
	    }

        payload = "ticket=%s&device=desktop" % ticket
        response = requests.post(url, headers = headers, data = payload)
        
        cookies = response.cookies.get_dict()
        print(cookies)
        auth_cookies = {
            "Ucookie": cookies["Ucookie"],
            "genoma-session-id": cookies["genoma-session-id"]
        }
        return auth_cookies


    log("Starting login process...")

    log("Login Data")
    login_data = set_login_data()
    log("Requesting pinpad")
    pinpad_data, genoma_cookie = request_pinpad(login_data)
    pin_positions = set_pinpad_positions(pinpad_data)
    log("Requesting ticket")
    ticket = request_ticket(pin_positions, genoma_cookie)
    log("Requesting auth cookies")
    auth_cookies = request_auth_cookies(ticket)
    log("Done")
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
