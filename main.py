from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import uvicorn
from config import *
from report import *
import time
import random


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


    
def get_random_job():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor

    # Construct the SQL query to select one random record from the 'jobs' table
    sql_query = "SELECT * FROM jobs ORDER BY RAND() LIMIT 1"
    #sql_query = "SELECT * FROM jobs where jobid=50820100"

    cursor.execute(sql_query)
    result = cursor.fetchone()
    db.close()

    return result


@app.on_event("startup")
async def startup_event():
    db = connect_to_db()

@app.get("/top-skills")
def get_top_skills():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("""SELECT catgroup,catname,count(1) ads FROM categories 
                        left outer join jobskills on catId=jobskills.skillcatId 
                        left outer join jobs on jobskills.jobid=jobs.jobid 
                        group by catgroup,catname order by count(1) desc""")
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['catgroup', 'catname','ads'])
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
    cursor.execute("""SELECT catgroup,catname,count(1) ads FROM categories 
                        left outer join jobskills on catId=jobskills.skillcatId 
                        left outer join jobs on jobskills.jobid=jobs.jobid 
                        group by catgroup,catname order by count(1) desc""")
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['catgroup', 'catname','ads'])

    plt.figure(figsize=(10,6))
    sns.barplot(x='ads', y='catname', data=df)
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
    start_time = time.time()
    pagename = "Keywords"
    load_categories()
    job=get_random_job()    
    keywords=findkeywords(job['description'])            
    #content = json.dumps(keywords)
    #content = json.dumps(keywords)+"<hr>"+convert_to_bootstrap_table(job)+"<hr>"+str(catsArray)
    content = json.dumps(keywords)+"<hr>"+convert_to_bootstrap_table(job)+"<hr>"
    end_time = time.time()
    # Calculate the time taken
    execution_time = end_time - start_time
    content += f"Function took {execution_time:.6f} seconds to execute."    
    return templates.TemplateResponse("home.html", {"request": request, "pagename": pagename, "content": content})


@app.get("/rap", response_class=HTMLResponse)
async def keywords(request: Request):
    start_time = time.time()
    pagename = "Report"
    content =  active_posts_skills()
    end_time = time.time()
    # Calculate the time taken
    execution_time = end_time - start_time
    content += f"Function took {execution_time:.6f} seconds to execute."    
    return templates.TemplateResponse("home.html", {"request": request, "pagename": pagename, "content": content})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
