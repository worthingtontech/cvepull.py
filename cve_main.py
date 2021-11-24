import requests
from datetime import datetime, timedelta
import json

# #==========================================================================================
# # user input section
# #==========================================================================================
day = 45 #number in days
apikey = 'Android' 
keywords = ["Android", "escalation of privilege", "denial of service"]
# #==========================================================================================
# # setting time variables in UTC -5hrs and -3ms digits
# #==========================================================================================
now = datetime.utcnow()
by_week = now - timedelta(days=day) 
this_filter_date = by_week
iso_last_week = f'{this_filter_date.strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'
iso_now = f'{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'
keys = ()
test_result = {'resultsPerPage': '2000',
               'keyword': apikey,
               'pubStartDate': iso_last_week,
               'pubEndDate': iso_now,
               'startIndex': '0'}
# #==========================================================================================
# # retrieve CVEs
# #==========================================================================================
response = requests.get(url='https://services.nvd.nist.gov/rest/json/cves/1.0', params=test_result)

nvd_data = response.json()

with open('1-initial_nvd.json', 'w+') as sourceFile:
    sourceFile.write(json.dumps(nvd_data, indent=2))

rawData = json.loads(response.text)

# #==========================================================================================
# # cherry-pick relevant keys
# #==========================================================================================
print("\n""cherry-picking relevant values...""\n","\n""Narrowing response with additional keywords""\n","\n""This may take a sec...")
cleanData = []
items = rawData['result']['CVE_Items']

for item in items:
    cve_data_meta_id = item["cve"]["CVE_data_meta"]["ID"]
    cvssV3 = ''
    pub_date = ''
    last_mod_date = ''
    description = ''

    try:
        cvssV3 = item["impact"]["baseMetricV3"]["cvssV3"]
    except KeyError:
        pass
    try:
        pub_date = item["publishedDate"]
    except KeyError:
        pass
    try:
        last_mod_date = item["lastModifiedDate"]
    except KeyError:
        pass

    for desc in item["cve"]["description"]["description_data"]:
        description = desc["value"]
        
    cleanData.append({"CVE_data_meta": cve_data_meta_id,
                     "description": description,
                     "impact": cvssV3,
                     "publishedDate": pub_date,
                     "lastModifiedDate": last_mod_date
                     })


with open('2-cleanData.json', 'w+') as outFile:
    outFile.write(json.dumps(cleanData, indent=2))

# # ==========================================================================================
# # narrow response with additional 'keywords'
# # ==========================================================================================
myResults = open("2-cleanData.json", "r")
scope = json.load(myResults)

output_json=[]
results = []
for k in keywords:
    counter = 0
    items = [x for x in scope if k in x['description']]
    for item in items: 
        output_json.append(item)
        counter += 1
    results.append(counter)

with open("3-Final CVEs.json", "w+") as outFile2:
    outFile2.write(json.dumps(output_json, indent=2, sort_keys=True))
# # ==========================================================================================
# # results logging per type
# # ==========================================================================================
resultObj = dict(zip(keywords, results))
total = len(output_json)

print("\n""{} total relevant vulnerabilities found!""\n".format(total))

for r in resultObj:
    print("{} {} vulnerabilities".format(resultObj[r], r))
