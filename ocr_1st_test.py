#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip install keras-ocr')


# In[3]:


import matplotlib.pyplot as plt
import keras_ocr


# In[4]:


import cv2


# In[5]:


pipeline = keras_ocr.pipeline.Pipeline()


# In[6]:


img = cv2.imread('Modern-house-number-sign.png')
img2 = cv2.imread('WIN_20230524_12_22_27_Pro.jpg')
img3 = cv2.imread('WIN_20230524_12_24_00_Pro.jpg')
#img = cv2.imread('WIN_20230524_12_22_27_Pro.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))


# In[7]:


images = [
    img,
    img2,
    img3
]


# In[ ]:


# Each list of predictions in prediction_groups is a list of
# (word, box) tuples.
prediction_groups = pipeline.recognize(img)


# In[11]:


# # Plot the predictions
# fig, axs = plt.subplots(nrows=len(img), figsize=(20, 20))
# # for ax, image, predictions in zip(axs, images, prediction_groups):
# #     keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
# keras_ocr.tools.drawAnnotations(image = img, predictions=predictions, ax=ax)

