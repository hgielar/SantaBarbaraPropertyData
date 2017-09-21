# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 13:49:10 2017

@author: raleigh-littles
"""
import requests, time, re, csv
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
    # Test a single request
    testing_url = 'http://sbcassessor.com/assessor/Results.aspx?APN=07506200&HN=&SN=&UN=&SB=SB_APN'
    payload = {'APN': '07506200', 'HN': '', 'SN': '', 'UN': '', 'SB': 'SB_APN'}

    response = requests.get(testing_url)

    reply = response.text
    print(reply)
    '''
    print ('Request finished')
    return response_array

    
def parse_apn_response(file):
    """ Returns an array of APNs found in the full HTML contained in the file that was passed to it. """
    
    # Really need to work on your regex here. 
    regex_string = 'apn=\d\d\d\d\d\d\d\d\d'
    apns_from_file = []
    with open(file, 'r') as input_file:
        text_to_parse = input_file.read()
        print ("Input file read")
        
    # Use regex to parse the APNs and write them to an array
    apn_matches = re.findall(regex_string, text_to_parse)
    print ("Matches found for regex:", len(apn_matches))
        
    # Remove everything before the = sign so its just a nice list of APNs
    for match in apn_matches:
        apns_from_file.append( match.split('=')[1] )
    
    return apns_from_file
    

def get_details_for_apn(apn):
    """
    Takes an APN, returns the data for it in a comma separated string consisting of:
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
    main_url = 'http://www.sbcvote.com/assessor/details.aspx?apn='
    response = requests.get(main_url + apn)
    values = []
    search_tags = ['LblAPN', 'LblAddress', 'LblCity', 'LblTransferDate', 'LblTRA', 'LblDocNum', 'LblStampAmt', 'LblUseCode',
                   'LblJurisdiction', 'LblAcreage', 'LblSqrFt', 'LblYearBuilt', 'LblBedrooms', 'LblBathrooms', 'LblFireplaces',
                   'LblLand', 'LblImprove', 'LblPersonal', 'LblHomeOwnerExem', 'LblOtherExem', 'LblNetVal']


    reply = response.text
    for search_string in search_tags:
        # Once the seach tag is found, go to the end of it (after the closing quote), and grab everything until the '</span',
        # thats the value we need!
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
        print ("It looks like an error occured in parsing your data, since your headers have:", len(headers), \
               "elements, but your data only passed in", len(values), " variables.")
        
        for i in range(0, 24): # There are 23 headers
            try:
                print( headers[i], " <--> ", values[i])
                
            except:
                pass
    return values


def main():
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
            print("APNs saved to file.")
    
    print ("Before removing duplicates, there are ", len(full_apn_array), "APNs.")
    full_apn_set = set(full_apn_array)
    print ("After removing duplicates, there are", len(full_apn_set), "APNs.")
    full_apn_string = ', '.join(full_apn_set)
    
    with open("Full-APN-list.txt", 'w') as apn_file_list:
        apn_file_list.write(full_apn_string)
    
    # Contains a string of strings holding in 
    #apn_details = []
    
    with open('Property_Data.csv', 'w') as my_csv_file:
        csv_writer = csv.writer(my_csv_file, delimiter =',')
        # Write headers to csv file first
        header_data = get_details_for_apn('0')
        csv_writer.writerow(header_data)
        for apn in full_apn_set:
            print ("Currently parsing APN:", apn)
            row_data = get_details_for_apn(apn)
            csv_writer.writerow(row_data)
            
            
main()

t1 = time.time()

print("TIME ELAPSED -- ", str(round(t1-t0, 3)))
        



            
            
        
        
        
        
        
        
        
        
    
    