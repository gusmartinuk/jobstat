import requests
from bs4 import BeautifulSoup
import re
import pymysql
import pymysql.cursors
import math
 
from config import DATABASE_NAME, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST

conn = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        db=DATABASE_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True)

cursor = conn.cursor()

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

    skills = []    
    try:       
        skills_div = soup.find('div', class_='skills')
        
        for li in skills_div.find_all('li', class_='lozenge skill-name'):
            skills.append(li.text)
        #print(skills)
    except:
        pass

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

    query = """INSERT INTO jobskils
                (jobid,skill)
            VALUES 
                (%(jobid)s, %(skill)s)
            ON DUPLICATE KEY UPDATE
            skill = VALUES(skill)
            """
    for skill in skills:        
        cursor.execute(query, {'jobid': jobid, 'skill':skill})
    conn.commit()

#xurl = 'https://www.reed.co.uk/jobs/work-from-home-python-jobs?pageno='
xurl = 'https://www.reed.co.uk/jobs/python-jobs?pageno='
page=1
while True:
    url=xurl+str(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    header = soup.find('header', class_='pagination_pagination__heading__Sjbaq pagination_pageNumbers__c73jS card-header')
    parts = header.text.split(' of ')
    total_jobs = int(parts[1].split(' ')[0].replace(',',''))
    maxpage=math.ceil(total_jobs/25)
    print("*****PAGE=",page,"  ****** total jobs=",total_jobs ,"***********total pages=",maxpage)
    for job in soup.find_all('div', class_='job-card_jobCard__body__8tp1S card-body'):
        #anchor=job.find('a', class_='job-card_jobCard__blockLink__njSjS')
        job_url = job.find('a')['href']
        #print(job_url)
        get_page(job_url)  
    page+=1
    if page>maxpage:
        break

cursor.close()
conn.close()
        