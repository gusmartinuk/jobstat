import mysql.connector
import re


DATABASE_NAME = 'reed'
DATABASE_USERNAME = 'root'
DATABASE_PASSWORD = ''
DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306

catsArray=[]

def connect_to_db():
    return mysql.connector.connect(
        host=DATABASE_HOST,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,        
    )


def encode_special_chars(xstr):
    return xstr.replace("#","1ozo1").replace("+","2ozo2").replace("++","3ozo3").replace(".","4ozo4")

def decode_special_chars(xstr):
    return xstr.replace("1ozo1","#").replace("2ozo2","+").replace("3ozo3","++").replace("4ozo4",".")
      

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
                    "catvalue": encode_special_chars(rgen.lower()),  # for compare
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
    #html_lower = encode_special_chars(html_string.lower())
    search_term_lower = search_term.lower()

    # Use regular expression to find all words in the HTML string
    words = re.findall(r'\b\w+\b', html_string)
    # Check if the case-insensitive word exists in the HTML string
    exists = any(word == search_term_lower for word in words)
    
    return exists

def remove_case_insensitive_word(html_string, search_term):
    # Convert the HTML string and search term to lowercase
    #html_lower = encode_special_chars(html_string.lower())
    search_term_lower = search_term.lower()

    # Use regular expression to find all words in the HTML string
    words = re.findall(r'\b\w+\b', html_string)
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
    html=encode_special_chars(html.lower())
    for cat in catsArray:
        qcat=cat.copy() # IMPORTANT original catsArray can change if use cat I am using copy of the element to protect original value.
        if case_insensitive_word_exists(html, qcat['catvalue'])==True:            
           removeit=qcat['catvalue'] 
           qcat['catvalue']=decode_special_chars(qcat['catvalue'])
           if qcat not in keywords:
              keywords.append(qcat)
           html = remove_case_insensitive_word(html,removeit)
    return keywords
