# -*- coding: utf-8 -*-

import requests
import time
import re
import csv
import os
import typing
import random
import pandas

import pdb
t0 = time.time()

main_base_url = "http://sbcassessor.com/assessor/"

def get_apn_results_per_digit():
    apn_results_search_url = main_base_url + "Results.aspx?"
    
    # Make a request to get all APNS with a 0, then a 1, then a 2, ... until 9. 
    # Return an 10-element list of raw results of APNs.
    
    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'en-US,en;q=0.8,en-GB;q=0.6',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'style=null',
'DNT':'1',
'Host':'sbcassessor.com',
'Referer':'http://sbcassessor.com/assessor/AssessorParcelMap.aspx?ER=NoResults',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    response_array = []
    
    for i in range(0, 1): # Change to 1 for debugging only
        while True: 
            search_url = "APN=" + str(i) + "&HN=&SN=&UN=&SB=SB_APN"

            response = requests.get(apn_results_search_url + search_url, verify=True) # needed for HTTPs
            
            # The website seems to always (?) respond with HTTP 200, even if it couldn't query data,
            # so you can't always assume that valid server response code equals meaningful response...
            if response.status_code == 200 and "The Website is down for maintenance. Please check back later." not in response.text:
                print("Successful response received.")
                response_array.append(response.text)
                break
                # # Save the response to a text file too
                # with open("APN-" + str(i) + ".txt", "w") as text_file:
                #     text_file.write(response.text)
                
                
            else:
                print(f"Query for website failed (HTTP {response.status_code} )")
                # Take a quick nap
                time.sleep(random.randint(0, 5))

    '''
    # Test a single request
    testing_url = 'http://sbcassessor.com/assessor/Results.aspx?APN=07506200&HN=&SN=&UN=&SB=SB_APN'
    payload = {'APN': '07506200', 'HN': '', 'SN': '', 'UN': '', 'SB': 'SB_APN'}

    response = requests.get(testing_url)

    reply = response.text
    print(reply)
    '''
    return response_array

    
def parse_apn_response(raw_apn_results):
    """ Returns a de-duplicated array of APNs found in the full HTML contained in the file that was passed to it. """
    # APNs don't have a strict format required, but they're all usually at least 3 digits
    apn_regex = "apn=([\d]{3,})"

    pdb.set_trace()

    apn_list = re.findall(apn_regex, raw_apn_results)
    print ("Matches found for regex:", len(apn_list))
    
    return list(set(apn_list))
    

def get_details_for_apn(apn):
    """
    Takes an APN, returns the data for it in a list consisting of:
    APN, Address, City, State, ZIP code, Transfer Date, TRA, Document #, Transfer Tax Amount, Use Description,
    Jurisdiction, Acreage, Square Feet, Year Built, Bedrooms, Bathrooms, Fireplaces,
    Land & Mineral Rights, Improvements, Personal Property, Home Owner Exemption, Other Exemption,
    Net Assessed Value
     """
    time.sleep(0.8) # Since the server keeps timing out... 
    headers = ['APN', ' Address', ' City', ' State', ' ZIP code', ' Transfer Date', ' TRA', ' Document #', ' Transfer Tax Amount', ' Use Description', ' Jurisdiction', ' Acreage', ' Square Feet', ' Year Built', ' Bedrooms', ' Bathrooms', ' Fireplaces', ' Land & Mineral Rights', ' Improvements', ' Personal Property', ' Home Owner Exemption', ' Other Exemption', ' Net Assessed Value'] 
    if ( int(apn) == 0 ): # use this to return the column headings
        return headers

    ## Given an APN, make a request to the server to get its details
    apn_detail_url = main_base_url + "details.aspx?apn="
    response = requests.get(apn_detail_url + apn)
    values = []
    search_tags = ['LblAPN', 'LblAddress', 'LblCity', 'LblTransferDate', 'LblTRA', 'LblDocNum', 'LblStampAmt', 'LblUseCode',
                   'LblJurisdiction', 'LblAcreage', 'LblSqrFt', 'LblYearBuilt', 'LblBedrooms', 'LblBathrooms', 'LblFireplaces',
                   'LblLand', 'LblImprove', 'LblPersonal', 'LblHomeOwnerExem', 'LblOtherExem', 'LblNetVal']


    reply = response.text

    for search_string in search_tags:
        # Once the search tag is found, go to the end of it (after the closing quote), and grab everything until the '</span',
        # thats the value we need!

        pdb.set_trace()

        starting_index = reply.find(search_string) + len(search_string) + 1 # to accont for the extra quote
        value = reply[starting_index: starting_index + 50] # get the next 50 characters, no input will ever be longer than this
        ending_index = value.find('</span>')
        value = value[1:ending_index] # to account for the closing '>' on the span
        
        if (value == ' '): # replace missing spaces with N/A
            value = 'N/A'
        
         # Special case to filter out some unicode
        if (value == '/xa0'):
            value = ' '
        
       # print("The value found for the tag", search_string, "is: ", value)
        
        if (search_string == 'LblCity'): # Parse manually to remove city, state, zip
            city =  value.split(',')[0] 
            state = (value.split(',')[1]).split()[0] # Get stuff to the right of the comma but to the left on the space

            # the far right element in the space-broken string is always going to be the zip code
            # Maybe even index this to save some time
            zip_code = value.split(' ')[-1] 
            values.append(city)
            values.append(state)
            values.append(zip_code)
            
        else:
            values.append(value)
    
            
    if (len(values) != len(headers)):
        print ("It looks like an error occurred in parsing your data, since your headers have:", len(headers), \
               "elements, but your data only passed in", len(values), " variables.")
        
    return values

if __name__ == "__main__":

    # Start by getting the 'master' list of APN responses.
    # Then filter each of those responses down until you have a list of all APNs registered.
    # Lastly, query details of each APN and then write that to the final spreadsheet.

    raw_apn_lists_results : typing.List[str] = get_apn_results_per_digit()

    # List of all available APNs
    full_apn_array = []

    for apn_list_starting_with_digit in raw_apn_lists_results:
        apns_starting_with_common_digit = parse_apn_response(apn_list_starting_with_digit)
        full_apn_array.append([apn for apn in apns_starting_with_common_digit])
    
    apn_dataframe = pandas.DataFrame(data=[], columns=get_details_for_apn(0))

    pdb.set_trace()

    for apn in full_apn_array:
        print ("Currently parsing APN:", apn)
        row_data = get_details_for_apn(apn)
        apn_dataframe.append(row_data)

    # At this point, all APN data has been populated. Move on to getting map/survey info.
    map_survey_dataframe = pandas.read_csv("Parcel_Map_Index.csv")

    # Join map/survey DF with APN dataframe on the APN key

    apn_dataframe.join(map_survey_dataframe, on='APN')

    # Lastly, go through the map URLs for each database and download them
    for row in apn_dataframe.iterrows():
        map_url = row['Url']
        address_parsed = re.sub(r'\W+', '', row['Address'])
        map_file_path = os.path.join("maps", address_parsed + ".pdf")
        with open(map_file_path, 'wb') as map_pdf_file:
            map_pdf_file.write(requests.get(map_url).content)