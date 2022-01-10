# -*- coding: utf-8 -*-

import bs4
import functools
import operator
import os
import pandas
import random
import re
import requests
import time
import typing


main_base_url = "https://sbcassessor.com/assessor/"

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
'Referer':'https://sbcassessor.com/assessor/AssessorParcelMap.aspx?ER=NoResults',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    response_array = []
    
    for i in range(0, 10): # Change to 1 for debugging only
        while True: 
            search_url = "APN=" + str(i) + "&HN=&SN=&UN=&SB=SB_APN"

            response = requests.get(apn_results_search_url + search_url, verify=False) # needed for HTTPs

            # Sleep even in case of success so that you don't get hit with the max retry error
            time.sleep(random.randint(1, 10))
            
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


    return response_array

    
def parse_apn_response(raw_apn_results):
    """ Returns a de-duplicated array of APNs found in the full HTML contained in the file that was passed to it. """
    # APNs don't have a strict format required, but they're all usually at least 3 digits
    apn_regex = "apn=([\d]{3,})"

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

    headers = ['APN', ' Address', ' City', ' State', ' ZIP code', ' Transfer Date', ' TRA', ' Document #', ' Transfer Tax Amount', ' Use Description', ' Jurisdiction', ' Acreage', ' Square Feet', ' Year Built', ' Bedrooms', ' Bathrooms', ' Fireplaces', ' Land & Mineral Rights', ' Improvements', ' Personal Property', ' Home Owner Exemption', ' Other Exemption', ' Net Assessed Value'] 

    if ( apn == 0 ): # use this to return the column headings
        return headers

    # The return value array. Will match length with the 'headers' (above)
    details_list = []

    ## Given an APN, make a request to the server to get its details
    apn_detail_url = main_base_url + "details.aspx?apn="
    response = requests.get(apn_detail_url + apn, verify=False)

    # Sleep after query, to avoid overloading server
    time.sleep(random.randint(1, 5))
    
    html_parser = bs4.BeautifulSoup(response.text, 'html.parser')

    search_tags = ['LblAPN', 'LblAddress', 'LblCity', 'LblTransferDate', 'LblTRA', 'LblDocNum', 'LblStampAmt', 'LblUseCode',
                   'LblJurisdiction', 'LblAcreage', 'LblSqrFt', 'LblYearBuilt', 'LblBedrooms', 'LblBathrooms', 'LblFireplaces',
                   'LblLand', 'LblImprove', 'LblPersonal', 'LblHomeOwnerExem', 'LblOtherExem', 'LblNetVal']

    for property_tag in search_tags:
        parser_result = html_parser.find("span", id=property_tag)

        if parser_result is not None:
            value_for_tag = parser_result.text

        else:
            # For some reason, that tag isn't present at all for the given APN
            # Not sure why this happens, likely just missing data.
            details_list.append("")
            continue

        if (property_tag == "LblAPN"):
            # Strip any dashes from the APN to get just an integer
            details_list.append(int(value_for_tag.replace("-", "")))
            
       # Confusingly, the 'City' field *sometimes* also contains the state and zip code, so strip these elements out
       # The 'City' field looks like: "LOS ANGELES, CA 11111"
        elif (property_tag == 'LblCity'):
            # City names don't have commas in them
            city = value_for_tag.split(",")[0]

            # Last 5 digits are zip code, but sometimes the zip code isn't included
            # (as some properties can span multiple zip codes)
            zip_code = value_for_tag[-5:]
            if not zip_code.isdigit():
                zip_code = ""

            # cheating a little bit here... (TODO)
            state = 'CA'

            # Order must match the headers list!
            details_list.extend([city, state, zip_code])

        else:
            details_list.append(value_for_tag)

    if (len(details_list) != len(headers)):
        print(f"Incorrect number of data! Expected {len(headers)}, received {len(details_list)}")
        return []
        
    return details_list

if __name__ == "__main__":

    # Start by getting the 'master' list of APN responses.
    # Then filter each of those responses down until you have a list of all APNs registered.
    # Lastly, query details of each APN and then write that to the final spreadsheet.

    raw_apn_lists_results : typing.List[str] = get_apn_results_per_digit()

    # List of all available APNs
    full_apn_array = []

    for apn_list_starting_with_digit in raw_apn_lists_results:
        apns_starting_with_common_digit = parse_apn_response(apn_list_starting_with_digit)
        #full_apn_array.append([apn for apn in apns_starting_with_common_digit])
        full_apn_array.append(apns_starting_with_common_digit)

    # You have a list of lists, now flatten it
    full_apn_array = functools.reduce(operator.concat, full_apn_array)
    
    apn_dataframe = pandas.DataFrame(columns=get_details_for_apn(0))

    # Build up the apn dataframe one row at a time
    for apn in full_apn_array:
        row_data = get_details_for_apn(apn)
        if len(row_data) != 0:
            apn_dataframe.loc[len(apn_dataframe)] = row_data

    # At this point, all APN data has been populated. Move on to getting map/survey info
    map_survey_dataframe = pandas.read_csv("Parcel_Map_Index.csv")

    # If there's no APN, you won't be able to get address info, so don't even bother downloading the map for it later
    map_survey_dataframe = map_survey_dataframe.dropna(subset=['APN'])


    # Strip hyphens from APN column! Needed for join later
    map_survey_dataframe["APN"] = map_survey_dataframe["APN"].apply(lambda x: x.replace("-", ""))

    # Join map/survey dataframe with APN dataframe on the APN key

    combined_dataframe = pandas.merge(apn_dataframe, map_survey_dataframe, on="APN")

    # Write the full dataframe out to a file
    combined_dataframe.to_csv("Full-APN-Dataframe.csv", encoding='utf-8')

    # Lastly, go through the map URLs for each database and download them
    for index, row in combined_dataframe.iterrows():
        map_url = row['Url']
        address_parsed = re.sub(r'\W+', '', row['Address'])
        map_file_path = os.path.join("maps", address_parsed + ".pdf")
        with open(map_file_path, 'wb') as map_pdf_file:
            # Again, sleep so that you're not just repeatedly spamming the server
            time.sleep(random.randint(5,10))
            map_pdf_file.write(requests.get(map_url).content)