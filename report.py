from config import *
import pandas as pd
from itertools import combinations

activejobsqry="""select jobs.jobid,catname,catgroup,round((jobs.salarymin+jobs.salarymax)/2,0) averagesalary from jobskills 
left outer join categories on jobskills.skillcatId=categories.catId
left outer join jobs on jobskills.jobid=jobs.jobid
WHERE
                        jobs.salaryperiod = 'YEAR'
                        AND jobs.salarymin > 10000
                        AND jobs.salarymax > 10000
                        AND jobs.salarymin*3>jobs.salarymax
                        AND jobs.datevalid > CURRENT_DATE
                        AND jobs.currency="GBP"
                        AND EXISTS(select jobid from jobskills where jobs.jobid=jobskills.jobid limit 1)
                        AND jobs.address_country="GB"
                        AND not title like '%property%'
                        AND not title like '%construction%'
                        AND not title like '%underwriter%'
                        AND not title like '%recruitment%'
                        AND not title like '%chemist%'
                        AND not title like '%loan %'
                        AND not title like '%sales %'
                        AND not title like '%delivery manager %'
                        AND not title like '%team assistant%'
                        AND not title like '%business%'
                        AND not title like '%Residential Development%'
                        AND not title like '%Solicitor%'                        
                        AND not title like '%Environmental Consulting%'
                        AND not title like '%Financial Analyst%'
                        AND not title like '%Branch Manager%'
                        AND not title like '%Letting Consultant%'
                        AND not title like '%Tax Manager%'
                        AND not title like '%Account Executive%'
                        AND not title like '%Estate Agency%'
                        AND not title like '%Branch Manager%'
                        AND not title like '%tranie%'
                        AND not title like '%apprentice%'
                        AND hrcompany<>'Noir'
                        """

groupqry="""select catId,catname 'Skill',round(avg(averagesalary),0) 'Average Salary £',count(1) 'Active Ads' from (
                select catId,catname,round((jobs.salarymin+jobs.salarymax)/2,0) averagesalary from jobskills 
                left outer join categories on jobskills.skillcatId=categories.catId
                left outer join jobs on jobskills.jobid=jobs.jobid
                WHERE
                                        jobs.salaryperiod = 'YEAR'
                                        AND jobs.salarymin > 10000
                                        AND jobs.salarymax > 10000
                                        AND jobs.salarymin*3>jobs.salarymax
                                        AND jobs.datevalid > CURRENT_DATE
                                        AND jobs.currency="GBP"
                                        AND EXISTS(select jobid from jobskills where jobs.jobid=jobskills.jobid limit 1)
                                        AND jobs.address_country="GB"
                                        AND not title like '%property%'
                                        AND not title like '%construction%'
                                        AND not title like '%underwriter%'
                                        AND not title like '%recruitment%'
                                        AND not title like '%chemist%'
                                        AND not title like '%loan %'
                                        AND not title like '%sales %'
                                        AND not title like '%delivery manager %'
                                        AND not title like '%team assistant%'
                                        AND not title like '%business%'
                                        AND not title like '%Residential Development%'
                                        AND not title like '%Solicitor%'                        
                                        AND not title like '%Environmental Consulting%'
                                        AND not title like '%Financial Analyst%'
                                        AND not title like '%Branch Manager%'
                                        AND not title like '%Letting Consultant%'
                                        AND not title like '%Tax Manager%'
                                        AND not title like '%Account Executive%'
                                        AND not title like '%Estate Agency%'
                                        AND not title like '%Branch Manager%'
                                        AND not title like '%tranie%'
                                        AND not title like '%apprentice%'
                                        AND catgroup=%(catgroup)s
                                        AND hrcompany<>'Noir'
                    ) zzz group by catname order by count(1) desc"""

activejobmatrixqry="""select jobs.jobid, GROUP_CONCAT(skillcatId) skillset,count(1) from jobs
                left outer join jobskills on jobskills.jobid=jobs.jobid
                WHERE
                                        jobs.salaryperiod = 'YEAR'
                                        AND jobs.salarymin > 10000
                                        AND jobs.salarymax > 10000
                                        AND jobs.salarymin*3>jobs.salarymax
                                        AND jobs.datevalid > CURRENT_DATE
                                        AND jobs.currency="GBP"
                                        AND EXISTS(select jobid from jobskills where jobs.jobid=jobskills.jobid and jobskills.skillcatId=%(skillcatid)s limit 1)
                                        AND jobs.address_country="GB"
                                        AND not title like '%property%'
                                        AND not title like '%construction%'
                                        AND not title like '%underwriter%'
                                        AND not title like '%recruitment%'
                                        AND not title like '%chemist%'
                                        AND not title like '%loan %'
                                        AND not title like '%sales %'
                                        AND not title like '%delivery manager %'
                                        AND not title like '%team assistant%'
                                        AND not title like '%business%'
                                        AND not title like '%Residential Development%'
                                        AND not title like '%Solicitor%'                        
                                        AND not title like '%Environmental Consulting%'
                                        AND not title like '%Financial Analyst%'
                                        AND not title like '%Branch Manager%'
                                        AND not title like '%Letting Consultant%'
                                        AND not title like '%Tax Manager%'
                                        AND not title like '%Account Executive%'
                                        AND not title like '%Estate Agency%'
                                        AND not title like '%Branch Manager%'
                                        AND not title like '%tranie%'
                                        AND not title like '%apprentice%'                                        
                                        AND jobskills.skillcatId<>%(skillcatid)s
                                        AND hrcompany<>'Noir'
group by jobs.jobid order by count(1) desc"""

top10qry="""
select GROUP_CONCAT(catid) xgroup
from
(
select catid FROM
(
select catid,catname,catgroup,count(1),round((jobs.salarymin+jobs.salarymax)/2,0) averagesalary from jobskills 
left outer join categories on jobskills.skillcatId=categories.catId
left outer join jobs on jobskills.jobid=jobs.jobid
WHERE
                        jobs.salaryperiod = 'YEAR'
                        AND jobs.salarymin > 10000
                        AND jobs.salarymax > 10000
                        AND jobs.salarymin*3>jobs.salarymax
                        AND jobs.datevalid > CURRENT_DATE
                        AND jobs.currency="GBP"
                        AND EXISTS(select jobid from jobskills where jobs.jobid=jobskills.jobid limit 1)
                        AND jobs.address_country="GB"
                        AND not title like '%property%'
                        AND not title like '%construction%'
                        AND not title like '%underwriter%'
                        AND not title like '%recruitment%'
                        AND not title like '%chemist%'
                        AND not title like '%loan %'
                        AND not title like '%sales %'
                        AND not title like '%delivery manager %'
                        AND not title like '%team assistant%'
                        AND not title like '%business%'
                        AND not title like '%Residential Development%'
                        AND not title like '%Solicitor%'                        
                        AND not title like '%Environmental Consulting%'
                        AND not title like '%Financial Analyst%'
                        AND not title like '%Branch Manager%'
                        AND not title like '%Letting Consultant%'
                        AND not title like '%Tax Manager%'
                        AND not title like '%Account Executive%'
                        AND not title like '%Estate Agency%'
                        AND not title like '%Branch Manager%'
                        AND not title like '%tranie%'
                        AND not title like '%apprentice%'
                        AND hrcompany<>'Noir'
group by catname
order by count(1) desc
) zzz where catgroup=%(catgroup)s limit 10
) yyy;
"""

def result_to_table(result,header=False,rowno=False):
    table_html = '<table class="table table-bordered table-hover table-striped">'   
    cnt=0     
    for row in result:        
        cnt+=1
        if cnt==1 and header==True:
            table_html += '<tr>'
            if rowno==True:
                table_html += f'<th>No</th>'                 
            for key,value in row.items():
               table_html += f'<th>{key}</th>'                 
            table_html += '</tr>'
        table_html += '<tr>'
        if rowno==True:
            table_html += f'<td>{cnt}</td>'                 
        for key,value in row.items():
            table_html += f'<td>{value}</td>'     
        table_html += '</tr>'
    table_html += '</table>'
    #table_html=str(job_data)
    return table_html


def active_posts_skills():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("select distinct catgroup from categories")
    groups=cursor.fetchall()
    content='<div class="d-flex flex-wrap bg-light justify-content-center">'
    for group in groups:        
        content+='<div style="padding: 5px;"><h2>'+group['catgroup']+'</h2>'
        cursor.execute(groupqry+' limit 10',{"catgroup":group['catgroup']})
        result = cursor.fetchall()    
        content+=result_to_table(result,header=True,rowno=True)+'</div>'   
    return(content+'</div>')

def get_skill_names(skills):
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute('SELECT GROUP_CONCAT(catname) xcats FROM categories where catId in ('+skills+') ')
    result=cursor.fetchone() 
    cursor.close()
    db.close()
    return(result['xcats'])

def generate_html_table(data, table_title):
    table_html = f'<h4>{table_title}</h4><table class="table table-bordered table-hover">'
    table_html += '<tr><th>Skills</th><th>Count</th></tr>'
    for index, count in data.items():
        skills = ', '.join(index)
        skills = get_skill_names(skills).replace(",",", ")
        table_html += f'<tr><td>{skills}</td><td>{count}</td></tr>'
    table_html += '</table>'
    return table_html

def active_posts_skills_matrix():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute(groupqry+' limit 10',{"catgroup":'Language'})
    topresult=cursor.fetchall()
    content='<h2>Comparative Popularity: Programming Languages & Other Key Skills</h2>'
    content+='<div class="d-flex flex-wrap bg-light justify-content-center">'
    for row in topresult:
        cursor.execute(activejobmatrixqry,{'skillcatid': row['catId']}) 
        result=cursor.fetchall()
        df = pd.DataFrame(result, columns=['jobid', 'skillset'])
        # Assuming you have a DataFrame named 'df' with columns 'jobid' and 'skillset'
        # Convert the 'skillset' column from comma-separated strings to lists of skill ids
        df['skillset'] = df['skillset'].apply(lambda x: x.split(','))
        # Calculate the most preferred double skills
        cnt=3
        while cnt<4:
            qskills = df['skillset'].apply(lambda x: list(combinations(x, cnt))).explode().value_counts().head(10)
            skills_table = generate_html_table(qskills, row['Skill']+" with ...")
            content+='<div style="padding: 5px;">'+skills_table+'</div>'
            cnt+=1
    content+='</div>'
    return content
