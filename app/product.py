from groq import Groq
import os
import re
import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()

GROQ_MODEL = os.getenv('GROQ_MODEL')

project_root = Path(__file__).resolve().parent.parent
db_path = project_root / "resources"/"db.sqlite"


client_sql = Groq()

sql_prompt = """You are an expert in understanding the database schema and generating SQL queries for a natural language question asked
pertaining to the data you have. The schema is provided in the schema tags. 
<schema> 
table: product 

fields: 
product_link - VARCHAR(300) (hyperlink to product) 
product_img - VARCHAR(200) (hyperlink to product image) 
product_name - VARCHAR(100) (name of the product) 
price - INTEGER (price of the product in Bangladeshi Taka)
sold_amount - INTEGER (total number of products sold)
number_of_rating - INTEGER    (total number of ratings for the product)   
rating - DECIMAL(2,1)  (average rating of the product. Range 0-5, 5 is the highest.)
shop_location - VARCHAR(15)   (location of the shop in Bangladesh)
product_category - VARCHAR(45)   (category of the product, e.g. "Men", "Jewellery","Sports","Electronic Device","Computer Accessories","Women","Home appliance")
sub_category - VARCHAR(45)   (sub-category of the product, e.g. "Shoe","Womens Jewellery"(category for this is Jewellery), "Dumbbells,"Smartphone","Keyboard","Clothing","Air Conditioner")

</schema>
Make sure whenever you try to search for the name or sub category, the name can be in any case.
product category and sub category is given to you so you need to apply logic based on that. 
So, make sure to use %LIKE% to find Never use "ILIKE". 
When the question includes specific product names or brand names (e.g., iPhone, Fantech), use the product_name field to search for those terms.
Create a single SQL query for the question provided. 
When asked to list or show men shirt or women shirt the product category is "Men and Boys Fashion" and sub_category is "Clothing" and for women shirt product category is Women's and Girl's Fashion and sub_category is Clothing.
The query should have all the fields in SELECT clause (i.e. SELECT *)

Just the SQL query is needed, nothing more. Always provide the SQL in between the <SQL></SQL> tags."""


comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
Product title, price in bangladeshi taka, sold amount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Women Running Shoes: 1104tk, 39 sold, Rating: 4.4 <link>
2. Keyboard: 2104tk, 10 sold, Rating: 4.0 <link>

"""


def generate_sql_query(question):
    ## passing the prompt template and user prompt to the model
    ## then model will generate sql query based on the prompt and user question
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt,
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,
        max_tokens=1024
    )

    return chat_completion.choices[0].message.content


##run sql quey on the db and return the records as df
def run_query(query):
    if query.strip().upper().startswith('SELECT'):
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)
            return df

#passing the question and context to the model
#context(df as list of dictionaries containing desired records)
# and then model will generate the answer based on the context provided
## also giving a prompt template to the model so that it can understand how to answer the question
def data_comprehension(question, context):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": f"QUESTION: {question}. DATA: {context}",
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,
        # max_tokens=1024
    )

    return chat_completion.choices[0].message.content



def sql_chain(question):
    sql_query = generate_sql_query(question)
    pattern = "<SQL>(.*?)</SQL>"
    ##re.DOTALL allows the dot to match newlines as well
    ## so that we can match the entire SQL query even if it spans multiple lines
    matches = re.findall(pattern, sql_query, re.DOTALL)

    if len(matches) == 0:
        return "Sorry, LLM is not able to generate a query for your question"

    ## prints the sql query generated by the model
    print(matches[0].strip())

    response = run_query(matches[0].strip())
    if response is None:
        return "Sorry, there was a problem executing SQL query"

    #convert the response to a list of dictionaries
    context = response.to_dict(orient='records')

    answer = data_comprehension(question, context)
    return answer


if __name__ == "__main__":
    question = "All shoes with rating higher than 4.5 and total number of reviews greater than 500"
    sql_query = generate_sql_query(question)
    print(sql_query)
    question = "Show top 3 shoes in descending order of rating"
    answer = sql_chain(question)
    print(answer)
