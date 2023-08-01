import requests
from bs4 import BeautifulSoup
import re
import pymysql
import pymysql.cursors
import math
import os,sys
import argparse

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent folder to the Python path
sys.path.append(parent_folder_path)
 
from config import *

def get_job_id_from_url(url):
    pattern = r"/(\d+)\?"
    # Search for the job ID in the URL
    match = re.search(pattern, url)
    if match:
        job_id = match.group(1)
        return job_id
    return 0

def get_page(purl):
    pattern = re.compile(r'/jobs/.*/(.*)\?')
    match = pattern.search(purl)
    jobid = match.group(1)
    print("jobid=",jobid)
    response = requests.get('https://www.reed.co.uk'+purl)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        jobtitle=soup.find('h1').text
    except:     
        jobtitle=''
    print("title:",jobtitle)    
    try:    
        value_span = soup.find('span', itemprop='value')
        try:      
            # Get the minValue 
            min_value = value_span.find('meta', itemprop='minValue')['content']
        except:
            min_value = ''    
        try:
            # Get the maxValue
            max_value = value_span.find('meta', itemprop='maxValue')['content'] 
        except:
            max_value = ''
        try:
            # Get the unitText 
            unit_text = value_span.find('meta', itemprop='unitText')['content']
        except: 
            unit_text = ''    
            
        #print("min salary:",min_value)
        #print("max salary:",max_value)
        #print("salary for per :",unit_text)
    except:
        pass

    #skills = []    
    #try:       
    #    skills_div = soup.find('div', class_='skills')
    #    
    #    for li in skills_div.find_all('li', class_='lozenge skill-name'):
    #        skills.append(li.text)
    #    #print(skills)
    #except:
    #    pass

    try:
        date_posted = soup.find('meta', itemprop='datePosted')['content']
    except:    
        date_posted = ''

    try:        
        valid_through = soup.find('meta', itemprop='validThrough')['content']
    except:
        valid_through = ''    
    try:    
        recruiter_name = soup.find('span', itemprop='name').text
    except:
        recruiter_name =''    

    #print(date_posted)
    #print(valid_through)
    #print(recruiter_name)

    try:
        currency = soup.find('meta', itemprop='currency')['content']
    except:
        currency = ''

    try:    
        salary_lbl = soup.find('span', {'data-qa': 'salaryLbl'}).text
    except:
        salary_lbl =''    
    try:
        job_country = soup.find('span', id='jobCountry').get('value') 
    except:
        job_country = ''    
    try:
        address_region = soup.find('meta', itemprop='addressRegion')['content']
    except:
        address_region = ''    

    try:    
        address_locality = soup.find('span', itemprop='addressLocality').text
    except:
        address_locality = ''    

    try:
        address_country = soup.find('meta', itemprop='addressCountry')['content']
    except:    
        address_country = ''

    try:
        employment_type = soup.find('span', itemprop='employmentType')['content']
    except:
        employment_type = ''    

    try:
        job_location_type = soup.find('meta', itemprop='jobLocationType')['content']
    except:
        job_location_type = ''    

    try:
        description = soup.find('span', itemprop='description')        
    except:
        description = ''    

    #print(currency)
    #print(job_country)
    #print(salary_lbl) 
    #print(address_region)
    #print(address_locality)
    #print(address_country)
    #print(employment_type)
    #print(job_location_type)
    #print(description)
    data = {
    'jobid': jobid,
    'title': jobtitle.encode('utf-8', errors='ignore'), 
    'salarymin': min_value,
    'salarymax': max_value,
    'salaryperiod': unit_text,
    'dateposted': date_posted,
    'datevalid': valid_through,
    'hrcompany': recruiter_name.encode('utf-8', errors='ignore'),
    'currency': currency.encode('utf-8', errors='ignore'),
    'job_country': job_country.encode('utf-8', errors='ignore'),
    'address_region': address_region.encode('utf-8', errors='ignore'),
    'address_locality': address_locality.encode('utf-8', errors='ignore'),
    'address_country': address_country.encode('utf-8', errors='ignore'),
    'employment_type': employment_type.encode('utf-8', errors='ignore'),
    'job_location_type': job_location_type.encode('utf-8', errors='ignore'),
    'description': description.encode('utf-8', errors='ignore'), 
    }

    # Insert or update query
    query = """INSERT INTO jobs
                (jobid, title, salarymin, salarymax, salaryperiod, dateposted, 
                datevalid, hrcompany, currency, job_country, address_region,
                address_locality, address_country, employment_type, 
                job_location_type, description)
            VALUES 
                (%(jobid)s, %(title)s, %(salarymin)s, %(salarymax)s, %(salaryperiod)s,
                %(dateposted)s, %(datevalid)s, %(hrcompany)s, %(currency)s,
                %(job_country)s, %(address_region)s, %(address_locality)s,  
                %(address_country)s, %(employment_type)s, %(job_location_type)s,
                %(description)s)
            ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            salarymin = VALUES(salarymin), 
            salarymax = VALUES(salarymax),
            datevalid = VALUES(datevalid),
            description = VALUES(description)
            """
            
    cursor.execute(query, data)
    conn.commit() 
    skills=findkeywords(str(jobtitle)+" "+str(description))    
    #skills=findkeywords(str(data['description']))    

    query = """INSERT IGNORE INTO jobskills
                (jobid,skillcatid)
            VALUES 
                (%(jobid)s, %(skillcatid)s)
            ON DUPLICATE KEY UPDATE
            skillcatid = VALUES(skillcatid)
            """
            
    for skill in skills:        
        cursor.execute(query, {'jobid': jobid, 'skillcatid':skill['catId']})
    conn.commit()



conn = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        db=DATABASE_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True)

cursor = conn.cursor()
load_categories()

parser = argparse.ArgumentParser(description="required some parameters.")
    
# Add arguments to the parser
parser.add_argument("--page", type=int, default=1, help="Crawl start page")
parser.add_argument("--endpage", type=int, default=999999, help="Crawl end page")
parser.add_argument("--newonly", type=str,default="yes", help="yes: new pages only, no: update")
parser.add_argument("--offset", type=str,default="", help="today, lastthreedays, lastweek, default empty (anytime) ")
parser.add_argument("--keyword", type=str,default="developer", help="any keyword to crawl jobs, developer ")
parser.add_argument("--statsonly", type=str,default="no", help="yes:statistic only without crawl")
    
# Parse the command-line arguments
args = parser.parse_args()

print(args)

xurl = f'https://www.reed.co.uk/jobs/{args.keyword.replace(" ","-").strip()}-jobs?page={args.page}'
if args.offset != '':
    xurl += f'&dateCreatedOffSet={args.offset}'

print(xurl)   

#xurl = 'https://www.reed.co.uk/jobs/work-from-home-python-jobs?pageno='
#xurl = 'https://www.reed.co.uk/jobs/python-jobs?pageno='
#xurl = 'https://www.reed.co.uk/jobs/developer-jobs?pageno='   ## full scan
#xurl = 'https://www.reed.co.uk/jobs/developer-jobs?dateCreatedOffSet=lastthreedays&pageno='
#xurl = 'https://www.reed.co.uk/jobs/developer-jobs?dateCreatedOffSet=today&pageno='

page=args.page
skipcounter=0
scancounter=0

while True:
    if page>1:
        url=xurl+str(page)
    else:
        url=xurl.replace("?pageno=","")
        url=xurl.replace("&pageno=","")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Define a regex pattern to match the consistent part of the class name
    pattern = re.compile(r'pagination_pagination__heading__\w+ pagination_pageNumbers__\w+ card-header')

    # Find the header element using the CSS selector with the regex pattern
    header = soup.select_one('header[class*="pagination_pagination__heading__"][class*="pagination_pageNumbers__"][class*="card-header"]')

    print(header)
    try:
        parts = header.text.split(' of ')
        total_jobs = int(parts[1].split(' ')[0].replace(',',''))
        maxpage=math.ceil(total_jobs/25)
    except Exception as e:
        maxpage=1
        total_jobs=0
        print(str(e))
            
    if args.statsonly=='yes':
       print(f"statsonly, other parameters ignored :   Total Job Ads: {total_jobs},  Total Pages: {maxpage} ")     
       break 
    print("*****PAGE=",page,"  ****** total jobs=",total_jobs ,"***********total pages=",maxpage)
           
    pattern = re.compile(r'job-card_jobCard__body__\w+ card-body')

    # Find all div elements using the CSS selector with the regex pattern
    job_card_divs = soup.find_all('div', class_=lambda c: c and pattern.match(c))
    
    for job in job_card_divs:
        #anchor=job.find('a', class_='job-card_jobCard__blockLink__njSjS')
        job_url = job.find('a')['href']
        #print(job_url)
        if args.newonly=='yes':
            jobid=get_job_id_from_url(str(job_url))
            cursor.execute("select jobid from jobs where jobid=%(jobid)s",{'jobid': jobid})       
            result = cursor.fetchone()    
            if result!=None:  # old ad
               skipcounter+=1     
               continue  # skip, the id is already in jobs table                                                     

        get_page(job_url)  
        scancounter+=1
    page+=1
    if page>maxpage or page>args.endpage:
        break

print("Results:")
print(f"Total crawled ads: {scancounter}")
print(f"Total skipped ads: {skipcounter}")
print("parameters:",args)
cursor.close()
conn.close()
        