import asyncio
import csv
import httpx
import re


API_LINK = "https://api.presence.io/ucmerced/v1/grid/portal-view/Organization/"
CATEGORIES_LINK = "https://api.presence.io/ucmerced/v1/organizations/"

page = httpx.get(CATEGORIES_LINK).json()
ORG_NAMES = [page[i]['name'] for i in range(len(page))]
ORG_DOMAINS = [page[i]['uri'] for i in range(len(page))]

# Options: "Org_Description", "Contact_Name", "Contact_Email"
OPTIONS = ["Contact_Name", "Contact_Email"]

'''Categories:  "Academic", "Art", "Community_Service", "Cultural", "Dance",
                "Faith Based", "Fraternity_and_Sorority", "Gaming",
                "Graduate_Student_Organization", "Leadership", "Music",
                "Professional", "Recreation_and_Athletics", "Social", "Special Interest",
                "Student_Government", "UC_Merced_Department_Or_Area",
                "Undergraduate_Student_Organization", "Wellness"
'''

CATEGORIES = ["Academic", "Cultural"]


async def get_data(options: list[str]) -> list[list[str]]:
    organizations_list = []

    async with httpx.AsyncClient(timeout=None) as client:
        tasks = (client.get(API_LINK + domain)
                 for domain in ORG_DOMAINS)
        reqs = await asyncio.gather(*tasks)

    for i, req in enumerate(reqs):
        req = req.json()
        temp_lst = [ORG_NAMES[i]]

        if "Org_Description" in options:
            try:
                data = req["fieldData"][3]["items"][6]["value"]
                data = re.sub('<[^<]+?>|\xa0', '', data)
                temp_lst.append(data)
            except:
                temp_lst.append("NO DATA")

        if "Contact_Name" in options:
            try:
                temp_lst.append(req["fieldData"][4]["items"][1]["value"])
            except:
                temp_lst.append("NO DATA")

        if "Contact_Email" in options:
            try:
                temp_lst.append(req["fieldData"][4]["items"][2]["value"])
            except:
                temp_lst.append("NO DATA")

        organizations_list.append(temp_lst)

    return organizations_list


async def get_categories(categories: list[str]) -> list[list[str]]:
    categories_list = []
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = (client.get(CATEGORIES_LINK + domain)
                 for domain in ORG_DOMAINS)
        reqs = await asyncio.gather(*tasks)
    for i, req in enumerate(reqs):
        req = req.json()
        temp_lst = [ORG_NAMES[i]]
        temp_lst.append(req["categories"])
        categories_list.append(temp_lst)
    return categories_list

ORGANIZATIONS_LIST = asyncio.run(get_data(OPTIONS))
ORGANIZATIONS_LIST.sort(key=lambda x: x[0].lower())
CATEGORIES_LIST = []
OUTPUT_LIST = []
if CATEGORIES:
    CATEGORIES_LIST = asyncio.run(get_categories(CATEGORIES))
    CATEGORIES_LIST.sort(key=lambda x: x[0].lower())
    for i, org in enumerate(CATEGORIES_LIST):
        for category in org[1]:
            if category in CATEGORIES:
                OUTPUT_LIST.append(ORGANIZATIONS_LIST[i])
                break

else:
    OUTPUT_LIST = ORGANIZATIONS_LIST
with open("Student_Groups.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Organization Name"] + OPTIONS)
    for org in OUTPUT_LIST:
        writer.writerow(org)
