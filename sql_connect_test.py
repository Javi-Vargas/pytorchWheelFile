#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install mysql-connector-python


# In[2]:


import mysql.connector


# In[3]:


# Replace the placeholders with your actual database credentials
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='javi4',
    database='sd2'
)


# In[4]:


cursor = cnx.cursor()


# In[9]:


# query = "select * from players;"
query = "select * from players where player_id=4;"
cursor.execute(query)
result = cursor.fetchall()
for row in result:
    print(row)

