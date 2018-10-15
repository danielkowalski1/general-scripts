#!/usr/bin/python3

import requests

from requests.auth import HTTPBasicAuth

import json

import datetime

 

# Sumo Logic API Creds

ACCESS_ID = ‘xxxxxxxxxx'

ACCESS_KEY = 'xXXXXXXXXXXXXXXXxxxxxxxxxxxx’

SEARCH_URL = 'https://api.us2.sumologic.com/api/v1/search/jobs'

HEADER = { "Content-Type":"application/json",

        "Accept":"application/json"}

QUERY = '_collector="Dan-Test-Cloudtrail-Ingest"'

BODY = {"query":QUERY, "from":"2018-10-07T00:00:00", "to":"2018-10-07T15:00:00", "timeZone":"CST"}

 

def displayActions():

    print ("Creating search query:\t" + QUERY + '\n')

    x = datetime.datetime.now()

    print ("Time: " + str(x) + '\n')

 
def createSearch(URL, body, header, ACCESS_ID, ACCESS_KEY):

    call = requests.post(URL, json=body, headers=header, auth=HTTPBasicAuth(ACCESS_ID, ACCESS_KEY))

    print ("We are inside the function:\n")

    print (call.text)

    print (call.url + '\n')
 

def main():

    displayActions()

    createSearch(SEARCH_URL, BODY, HEADER, ACCESS_ID, ACCESS_KEY)

 

if __name__ == '__main__':

    main()