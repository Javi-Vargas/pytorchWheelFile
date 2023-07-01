#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install pytesseract')


# In[3]:


import pytesseract
from PIL import Image


# In[4]:


image_path = 'Modern-house-number-sign.png'
image = Image.open(image_path)


# In[11]:


get_ipython().system('pip install tesseract-ocr')


# In[7]:


text = pytesseract.image_to_string(image)

