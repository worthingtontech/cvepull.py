import requests
from datetime import datetime, timedelta
import json

# TODO: query = ?
# TODO: Return data format to json
# 1. "startIndex"
# 2. "addOns"
# 3. "pubEndDate"
# 4. "pubStartDate"
# 5. "cvssV3Severity"
# 6. "resultsPerPage"

# answer = input("What is it that you want? ")
# for now, no input function, just edit line 25 'keyword' pair for accurate response

now = datetime.utcnow()
by_week = now - timedelta(days=7) #change amount of days to expand search
this_filter_date = by_week
# yyyy-MM-dd'T'HH:mm:ss:SSS UTC-05:00
iso_last_week = f'{this_filter_date.strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'
iso_now = f'{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'

test_result = {'resultsPerPage': '2000',
               'keyword': ['Android'], # only one keyword works at the moment with the API parameters
               # 'addOns': 'dictionaryCpes',      # API param not accepted at the moment
               'pubStartDate': iso_last_week,
               'pubEndDate': iso_now,
               'startIndex': '0'}

### beging response parsing

response = requests.get(url='https://services.nvd.nist.gov/rest/json/cves/1.0', params=test_result)

nvd_data = response.json()

with open('initial_nvd.json', 'w+') as sourceFile:
    sourceFile.write(json.dumps(nvd_data, indent=2))

ds = json.loads(response.text)
# print(ds["result"])

final_ds = []

for a_key in ds["result"]["CVE_Items"]:
    cve_data_meta_id = a_key["cve"]["CVE_data_meta"]["ID"]
    cvssV3 = ''
    pub_date = ''
    last_mod_date = ''
    description = ''
    try:
        cvssV3 = a_key["impact"]["baseMetricV3"]["cvssV3"]
    except KeyError:
        pass
    try:
        pub_date = a_key["publishedDate"]
    except KeyError:
        pass
    try:
        last_mod_date = a_key["lastModifiedDate"]
    except KeyError:
        pass

    for desc in a_key["cve"]["description"]["description_data"]:
        description = desc["value"]
    # Append to the final_ds results
    final_ds.append({"CVE_data_meta": cve_data_meta_id,
                     "description": description,
                     "impact": cvssV3,
                     "publishedDate": pub_date,
                     "lastModifiedDate": last_mod_date
                     })

print(json.dumps(final_ds, indent=2))

with open('my_results.json', 'w+') as outFile:
    outFile.write(json.dumps(final_ds, indent=2))
