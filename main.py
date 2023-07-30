from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import re
import random
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
catsArray=[]



def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="reed",        
    )


def get_random_job():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor

    # Construct the SQL query to select one random record from the 'jobs' table
    #sql_query = "SELECT * FROM jobs ORDER BY RAND() LIMIT 1"
    sql_query = "SELECT * FROM jobs where jobid=50820100"

    cursor.execute(sql_query)
    result = cursor.fetchone()
    db.close()

    return result

def encode_special_chars(xstr):
    return xstr.replace("#","1ozo1").replace("+","2ozo2").replace("++","3ozo3")

def decode_special_chars(xstr):
    return xstr.replace("1ozo1","#").replace("2ozo2","+").replace("3ozo3","++")
      

def load_categories():
    global catsArray
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("SELECT * FROM categories")
    result = cursor.fetchall()    
    catsArray = []
    for row in result:
        xrow = {
            "catId": row['catId'],
            "catname": row['catname'],
            "catvalue": encode_special_chars(row['catname'].strip()),  # for compare
        }
        catsArray.append(xrow)
        catgens=row['catgenerics'].split(",")
        for rgen in catgens:
            rgen=rgen.strip()
            if rgen!=row['catname'] and rgen!='':
                xrow = {
                    "catId": row['catId'],
                    "catname": row['catname'],
                    "catvalue": encode_special_chars(rgen),  # for compare
                }
                catsArray.append(xrow)
        
    catsArray.sort(key=lambda x: len(x["catvalue"]), reverse=True)
    

def convert_to_bootstrap_table(job_data):
    table_html = '<table class="table table-bordered table-hover">'    
    for field_name, field_value in job_data.items():
        table_html += '<tr>'
        table_html += f'<td>{field_name}</td>'
        if len(str(field_value)) > 5000:
            table_html += f'<td><textarea class="form-control" readonly>{field_value}</textarea></td>'
        else:
            table_html += f'<td>{field_value}</td>'
        table_html += '</tr>'
    table_html += '</table>'
    #table_html=str(job_data)
    return table_html

def case_insensitive_word_exists(html_string, search_term):
    # Convert the HTML string and search term to lowercase
    html_lower = encode_special_chars(html_string.lower())
    search_term_lower = search_term.lower()

    # Use regular expression to find all words in the HTML string
    words = re.findall(r'\b\w+\b', html_lower)
    # Check if the case-insensitive word exists in the HTML string
    exists = any(word == search_term_lower for word in words)
    
    return exists

def remove_case_insensitive_word(html_string, search_term):
    # Convert the HTML string and search term to lowercase
    html_lower = encode_special_chars(html_string.lower())
    search_term_lower = search_term.lower()

    # Use regular expression to find all words in the HTML string
    words = re.findall(r'\b\w+\b', html_lower)
    # Find the occurrences of the search term in the list of words
    occurrences = [i for i, word in enumerate(words) if word == search_term_lower]
    # Loop through the occurrences in reverse order and remove the words from the HTML string
    for index in reversed(occurrences):
        start = html_string.lower().find(words[index])
        end = start + len(words[index])
        html_string = html_string[:start] + html_string[end:]

    return html_string

def findkeywords(html):
    global catsArray
    keywords=[]
    for cat in catsArray:
        if case_insensitive_word_exists(html, cat['catvalue'])==True:            
           keywords.append(cat)
           html = remove_case_insensitive_word(html,cat['catvalue'])
    return keywords

@app.on_event("startup")
async def startup_event():
    db = connect_to_db()

@app.get("/top-skills")
def get_top_skills():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("SELECT `skill`, COUNT(`skill`) as `count` FROM `jobskills` GROUP BY `skill` ORDER BY `count` DESC LIMIT 10")
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['Skill', 'Count'])
    return df.to_dict(orient='records')

@app.get("/average-salary")
def get_average_salary():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("SELECT `title`, AVG((`salarymin`+`salarymax`)/2) as `avg_salary` FROM `jobs` GROUP BY `title` ORDER BY `avg_salary` DESC LIMIT 10")
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['Job Title', 'Average Salary'])
    return df.to_dict(orient='records')

@app.get("/top-skills-plot")
def get_top_skills_plot():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("SELECT `skill`, COUNT(`skill`) as `count` FROM `jobskills` GROUP BY `skill` ORDER BY `count` DESC LIMIT 10")
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['Skill', 'Count'])

    plt.figure(figsize=(10,6))
    sns.barplot(x='Count', y='Skill', data=df)
    plt.title('Top 10 Skills')
    plt.savefig('static/top_skills.png')
    return {"filepath": "static/top_skills.png"}
    
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    pagename='Job Statistic Home Page'
    content='Welcome to my job statistics page! '
    content+='<hr>'
    return templates.TemplateResponse("home.html", {"request": request,"pagename": pagename, "content": content})    

@app.get("/topbar", response_class=HTMLResponse)
async def get_home(request: Request):
    pagename='Job Statistic Home Page'
    image=get_top_skills_plot()
    content='Welcome to my job statistics page! '
    content+='<hr>'
    content+=f'<img src="{image["filepath"]}">'
    content+='<hr>'
    return templates.TemplateResponse("home.html", {"request": request,"pagename": pagename, "content": content})    

@app.get("/keywords", response_class=HTMLResponse)
async def keywords(request: Request):
    pagename = "Keywords"
    load_categories()
    job=get_random_job()    
    keywords=findkeywords(job['description'])        
    #content = json.dumps(keywords)
    content = json.dumps(keywords)+"<hr>"+convert_to_bootstrap_table(job)+"<hr>"+str(catsArray)
    return templates.TemplateResponse("home.html", {"request": request, "pagename": pagename, "content": content})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
