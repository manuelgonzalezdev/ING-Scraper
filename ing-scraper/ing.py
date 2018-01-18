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

verbose = False

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
                "documentType": 0,
            },
            "birthday": birthday
        }

        response = requests.post(url, headers = headers, data = payload)
        response = json.loads(response.text)
        pinpad_data = {
            "pinPadNumbers": response["pinPadNumbers"],
            "pinPositions": response["pinPositions"],
        }
        return pinpad_data


    def set_pinpad_positions(pinpad_data):
        return "TODO"

    def request_ticket(pinpad_positions):
        return "TODO"

    def request_auth_cookies(ticket):
        return "TODO"

    log("Starting login process...")

    log("Login Data")
    login_data = set_login_data()
    log("Requesting pinpad")
    pinpad_data = request_pinpad(login_data)
    pinpad_positions = set_pinpad_positions(pinpad_data)
    log("Requesting ticket")
    ticket = request_ticket(pinpad_positions)
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


# TEST

login()