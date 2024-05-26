import datetime
import pandas as pd
# for zip file download and extract
from urllib.request import urlopen
from urllib.error import HTTPError

def date_issue_to_url(date,issue):
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    date = date.strftime('%Y%m%d')
    issuezip="http://audiocdn.economist.com/sites/default/files/AudioArchive/{0}/{2}/Issue_{1}_{2}_The_Economist_Full_edition.zip".format(year, issue, date)
    return issuezip

def issue_ready(url):
    if url is None:
        return False
    try:
        a=urlopen(url)
    except HTTPError as e:
        # "e" can be treated as a http.client.HTTPResponse object
        #print('Error: fetching {}: {}'.format(url,e))
        return False
    else:
        return True

# Range of issues to collect:
schedule_day = pd.date_range('20140104','20231223',freq='W-SAT') # a long list of saturdays
# You must manually set the first issue number so the program knows where to start incrementing.
# Jan 7, 2012 = 8766
# Jan 4, 2014 = 8868
# Dec 23, 2023 = 9377
issue=8868

for i in schedule_day:
    url=date_issue_to_url(i,issue)
    if i == pd.to_datetime('20190330'):
        url=url.replace('edition.zip','Edition.zip')
    ready=issue_ready(url)
    if ready:
        print('OK ',url)
        issue=issue+1
        continue
        #print('{} ({})  -  {}s'.format(i.strftime('%Y%m%d'),issue,time) )
    else:
        # maybe try +/- one issue?
        for j in [issue-1, issue+1]:
            url=date_issue_to_url(i,j)
            ready=issue_ready(url)
            if ready:
                print('OK ',url)
                issue=j+1
                continue

    print('Error: ',url)
