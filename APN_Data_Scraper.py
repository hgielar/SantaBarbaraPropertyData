# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 13:49:10 2017

@author: raleigh-littles
"""
import requests, time
t0 = time.time()

def get_apn_list():
    main_url = "http://sbcassessor.com/assessor/Results.aspx?"
    
    # Make a request to get all APNS with a 0, then a 1, then a 2, ... until 9. 
    # The Union of all of these is the entire list of APNs.
    
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
    # Multiple requests
    
    for i in range(0, 10):
        search_url = "APN=" + str(i) + "&HN=&SN=&UN=&SB=SB_APN"

        print("Making request to url: ", main_url + search_url)

        response = requests.get(main_url + search_url)
        reply = response.text
        
        if "The Website is down for maintenance" not in reply:
            print("Successful response received.")
            response_array.append(reply)
            # Save the response to a text file too
            with open("APN data - " + str(i) + ".txt", "w") as text_file:
                text_file.write(reply)
                
            print(reply)
            
            
        else:
            print("Website down -- try again later.")

    


    '''
    # test single request?
    testing_url = 'http://sbcassessor.com/assessor/Results.aspx?APN=07506200&HN=&SN=&UN=&SB=SB_APN'
    payload = {'APN': '07506200', 'HN': '', 'SN': '', 'UN': '', 'SB': 'SB_APN'}

    response = requests.get(testing_url)

    reply = response.text
    print(reply)
    '''
    print ('Request finished')
    return response_array

    


def parse_apn_response(file):
    ''' Returns an array of APNs found in the full HTML passed into it '''
    t0 = time.time()
    print('Parsing APNs from file:', file)

    apn_array = []
                      
    search_string = "<a href='details.aspx?apn="
    #response_array = []
    #for i in range(0, len(file_list)):
    '''
    for file in file_list:
        #file = file_list[i]
        f = open(file)
        response_array.append(f.read())
    '''

    response_file = open(file)
    response = response_file.read()

    #for response in response_array:
    '''
    for i in range(0, len(response_array)):
        t0 = time.time()
        #current_apn_array = []
        response = response_array[i]
        print("Currently parsing from the ", i, "-th file")
        while (response.find(search_string) != -1):
            starting_index = response.find(search_string)
            #print("Starting index: ", starting_index)
            apn = response[starting_index + len(search_string): starting_index + len(search_string) + 9]
            #print("apn found: ", apn)
            full_apn_array.append(apn)

            response = response[starting_index + len(search_string) + 10:] # Trim the beginning of 'response'

        print("Finished parsing APNs from one file. Time elapsed:", str(time.time() - t0), "seconds.")
    '''

    while ( response.find(search_string) != -1):
        starting_index = response.find(search_string)
        apn = response[starting_index + len(search_string): starting_index + len(search_string) + 9]
        apn_array.append(apn)

        response = response[starting_index + len(search_string) + 10:] # Trim the beginning of 'response'
            
    '''
    #print(full_apn_set)
    print("Finished parsing APNs from 10 files.")
    full_apn_set = set(full_apn_array)
    with open("Full APN List.txt", 'w') as apn_file_list:
        full_apn_set_string = ', '.join(str(s) for s in full_apn_set)
        apn_file_list.write(full_apn_set_string)
    '''

    t1 = time.time()
    print("Finished parsing APNs from file. Time elapsed:", str(round(t1-t0, 3)), 'seconds')
    return apn_array


    def get_details_for_apn(apn):
        """
        Takes an APN, returns the data for it in a comma separated string consisting of:
        APN, Address, City, State, ZIP code, Transfer Date, TRA, Document #, Transfer Tax Amount, Use Description,
        Jurisdiction, Acreage, Square Feet, Year Built, Bedrooms, Bathrooms, Fireplaces,
        Land & Mineral Rights, Improvements, Personal Property, Home Owner Exemption, Other Exemption,
        Net Assessed Value
         """

        ## Given an APN, make a request to the server to get its details
        main_url = 'http://www.sbcvote.com/assessor/details.aspx?apn='
        response = requests.get(main_url + apn)
        values = []
        search_tags = ['LblAPN', 'LblAddress', 'LblCity', 'LblTransferDate', 'LblTRA', 'LblDocNum', 'LblStampAmt', 'LblUseCode',
                       'LblJurisdiction', 'LblAcreage', 'LblSqrFt', 'LblYearBuilt', 'LblBedrooms', 'LblBathrooms', 'LblFireplaces',
                       'LblLand', 'LblImprove', 'LblPersonal', 'LblHomeOwnerExem', 'LblOtherExem']

        for search_string in search_tags:
            # Once the seach tag is found, go to the end of it (after the closing quote), and grab everything until the '</span',
            # thats the value we need!
            starting_index = response.find(search_string) + len(search_string) + 1 # to accont for the extra quote
            value = response[starting_index: starting_index + 15] # get the next 15 characters, no input will ever be longer than this
            ending_index = value.find('</span>')
            value = value[:ending_index]
            print("The value found for the tag", search_string, "is: ", value)
            values.append(value) 

        # Now write the data to CSV format?



file_list = []
for i in range(0, 10):
    file_name = "APN Data - " + str(i) + ".txt"
    file_list.append(file_name)

full_apn_array = []
for file in file_list:
    #full_apn_array.append( parse_apn_response(file) )
    apns_in_file = parse_apn_response(file)
    for apn in apns_in_file:
        full_apn_array.append(apn)
    with open(file + "_parsed.txt", 'w') as parsed_file:
        parsed_file.write(str(apns_in_file))
        print("APNs saved to file:", str(parsed_file))

full_apn_set = set(full_apn_array)
full_apn_string = ', '.join(full_apn_set)

with open("Full-APN-list.txt", 'w') as apn_file_list:
    apn_file_list.write(full_apn_string)





            
            
        
        
        
        
        
        
        
        
    
    