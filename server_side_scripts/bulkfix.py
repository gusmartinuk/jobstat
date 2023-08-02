# this module is for fixes that one time run, update data, tests, etc.
# modify, update, tests, etc.
import requests
from bs4 import BeautifulSoup
import re
import pymysql
import pymysql.cursors
import math
import os,sys

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent folder to the Python path
sys.path.append(parent_folder_path)
 
from config import *

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

#xurl = 'https://www.reed.co.uk/jobs/work-from-home-python-jobs?pageno='
#xurl = 'https://www.reed.co.uk/jobs/python-jobs?pageno='
#xurl = 'https://www.reed.co.uk/jobs/developer-jobs?pageno='   ## full scan
#xurl = 'https://www.reed.co.uk/jobs/developer-jobs?dateCreatedOffSet=lastthreedays&pageno='
#xurl = 'https://www.reed.co.uk/jobs/developer-jobs?dateCreatedOffSet=today&pageno='
"""
# scanning block 
page=1
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
            
    print("*****PAGE=",page,"  ****** total jobs=",total_jobs ,"***********total pages=",maxpage)

    pattern = re.compile(r'job-card_jobCard__body__\w+ card-body')

    # Find all div elements using the CSS selector with the regex pattern
    job_card_divs = soup.find_all('div', class_=lambda c: c and pattern.match(c))

    
    for job in job_card_divs:
        #anchor=job.find('a', class_='job-card_jobCard__blockLink__njSjS')
        job_url = job.find('a')['href']
        #print(job_url)
        get_page(job_url)  
    page+=1
    if page>maxpage:
        break
"""

def update_skills(jobid,jobtitle,description,deleteolds=False):
    skills=findkeywords(str(jobtitle)+" "+str(description))    
    #print(skills)
    if deleteolds:  # delete old skills before recalculate
        cursor.execute("delete from jobskills where jobid=%(jobid)s", {'jobid': jobid})
        conn.commit()
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



def dbloop():
    load_categories()
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    #cursor.execute("SELECT jobid,title,description FROM jobs where title like '%c++%'")
    #cursor.execute("SELECT jobid,title,description FROM jobs where jobid=50930180")
    #cursor.execute("SELECT jobs.jobid,title,description FROM jobs where title like '%drupal%' or title like '%wordpress%' or description like '%drupal%' or description like '%wordpress%'")
    #cursor.execute("SELECT jobs.jobid,title,description FROM jobs where title like '%sql%' or title like '%sql%'")
    cursor.execute("SELECT jobid,title,description FROM jobs") # full update periodic run will be nice
    result = cursor.fetchall()        
    for row in result:
        xcatarray=catsArray.copy()
        update_skills(row['jobid'],row['title'],row['description'],True)
        print(row['jobid'],row['title'])
        #break    

conn = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        db=DATABASE_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True)
cursor = conn.cursor()
dbloop()
cursor.close()
conn.close()

        