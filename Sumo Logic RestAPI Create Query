#!/usr/bin/python3

##########################################
# Written by: DK
# Date: 10/21/2018
# Purpose: Python 3 script to create a Sumo Logic search job using Requests module.

# Documentation: https://help.sumologic.com/APIs/Search-Job-API/About-the-Search-Job-API
#
# Sample return object:
# API returns the following json on success
#   {"id":"xxxxxxxxxxxx","link":{"rel":"self","href":"https://api.us2.sumologic.com/api/v1/search/jobs/xxxxxxxxxx"}}
#   https://api.us2.sumologic.com/api/v1/search/jobs
##########################################
import requests
from requests.auth import HTTPBasicAuth
import datetime
import sys
import os


# Sumo Logic API Creds
ACCESS_ID = 'xxxxx'
ACCESS_KEY = 'xxxxxxxxxxxxxxxxxxxxxx'


def create_search_job(access_id, access_key, query='_collector="Test-Cloudtrail-Ingest"'):
    ''' Create search job and return status code and response json 
        If query is blank, use default query 
        Return all details (job, time, call.status_code, query) '''

    url = 'https://api.us2.sumologic.com/api/v1/search/jobs'
    header = { "Content-Type":"application/json", 
                    "Accept":"application/json"}
    body = {"query":query, "from":"2018-10-07T00:00:00", "to":"2018-10-07T15:00:00", "timeZone":"CST"}


    call = requests.post(url, json=body, headers=header, auth=HTTPBasicAuth(access_id, access_key))
    time = datetime.datetime.now().strftime('%m-%d-%Y-%H:%M:%S')

    if call.status_code != 202:
        print("Something went wrong. Return code: {0}".format(call.status_code))
        sys.exit(1)
    else:
        # print (call.text)
        # print (call.url)
        job = call.json()

        # Return tuple containing JSON object and timestamp
        return (job, time, call.status_code, query)


def write_job_to_file(job_id, time):
    ''' Write job ID to timestamped file and return filename '''
    
    # Appended date to filename
    dated_fn = time + '_job.id'
    
    with open (dated_fn, 'w') as f:
        f.write(job_id)
    return (dated_fn)


def get_query_from_user():
    ''' Prompt user for Sumo Logic query string and return it '''
    
    print("Enter Sumo Logic Query: ")
    user_input = ''
    user_input = input()
    # No input from user
    if not user_input:
        print("You entered nothing! Using default query...")
        return ''
    # All whitespaces from user
    elif user_input.isspace():
        print("Just whitespace is not allowed! Using default query...")
        return ''
    return (user_input)

def display_output(status_code, user_query, time, job, filename):
    ''' Print all details to console '''

    # Print job information and filename
    print("HTTP Status:".ljust(40) + str(status_code))
    print("Query:".ljust(40) + user_query)
    print("Timestamp:".ljust(40) + time)
    print("Job ID:".ljust(40) + job['id'])
    print("Link:".ljust(40) + job['link']['href'])
    print("Wrote ".ljust(40) + os.getcwd() + '/' + filename)


def main():
    query = ''
    # Prompt for query string
    query = get_query_from_user()
    # User typed nothing, use defaults
    if not query:
        print("Creating default search job...")
        job, time, status_code, user_query = create_search_job(ACCESS_ID, ACCESS_KEY)
        filename = write_job_to_file(job['id'], time)
    # Create user-defined query
    else:
        job, time, status_code, user_query = create_search_job(ACCESS_ID, ACCESS_KEY, query)
        filename = write_job_to_file(job['id'], time)
    
    display_output(status_code, user_query, time, job, filename)


if __name__ == '__main__':
    main()
