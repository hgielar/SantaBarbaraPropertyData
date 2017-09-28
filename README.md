# About

I was interested in seeing how expensive property is in Santa Barbara county so I used [Assessor Parcel Numbers](https://www.redfin.com/definition/apn) (APNs) to check. I used the [Santa Barbara County Clerk's website](http://www.sbcvote.com/assessor/AssessorParcelMap.aspx) to get every APN in the county.

The final output is a CSV containing 23 columns:

```
'APN', ' Address', ' City', ' State', ' ZIP code', ' Transfer Date', ' TRA', ' Document #', ' Transfer Tax Amount', ' Use Description', ' Jurisdiction', ' Acreage', ' Square Feet', ' Year Built', ' Bedrooms', ' Bathrooms', ' Fireplaces', ' Land & Mineral Rights', ' Improvements', ' Personal Property', ' Home Owner Exemption', ' Other Exemption', ' Net Assessed Value'
```

As of this writing, there's 130,951 APNs registered with the county.

In addition to this, I also downloaded the entire Parcel *Map* database from [the Public Works department](http://countyofsb.org/pwd/pmlookup.sbc).  You can review some maps for each parcel number, as these are stored in the Maps folder, but not all maps exist for every APN, so as of now there isn't much you can do with these, but they are interesting to look at if you want to see a map of your property (according to the county).

The map section is a work in progress and there is more to come.

# Layout

* The **output** data is the CSV file in the Results folder. It has 23 columns and 261903 rows (there is an empty line after each row.)

* The parcel **maps** are stored in the Maps folder. There is 3,606 map files (in PDF).

Since I was making large HTTP requests to the server (~300 MB+) I found it easier to cache the responses based on which number was searched (0 through 9). The *parsed* versions are found in the Data folder (the raw responses exceed Github's 100 MB size limit).
