#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 13:05:27 2019

@author: elizabeth sabovic
"""
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

from slt_cleaning_fe.py import add_deviation_feature


data = pd.read_csv('cleaned_brand_data.csv')
data = data.drop('Unnamed: 0',axis=1)
data.drop('producedIn',axis=1,inplace=True)

data['sku']=data.apply(lambda x: x['productLink'].split('-')[1].split('/')[0],axis=1)
data.drop('productLink',axis=1,inplace=True)
data.brand = data.brand.apply(lambda x: x.lower().replace('[\$,]',''))

data.set_index('sku',inplace=True)

data['twoPlusReviews'] = np.where(data.numReviews>1,1,0)

linear = LinearRegression()

x = ['actualPrice','suggPrice','avgRating','answers','questions','twoPlusReviews','numReviews','twoPlusReviews']
y = ['percentSaved']
X_train, X_test, y_train, y_test = train_test_split(data[x], data[y], test_size=0.30, random_state=42)
linear.fit(X_train,y_train)
print(linear.score(X_train,y_train))
print (linear.score(X_test,y_test))
print (linear.coef_)

add_deviation_feature(data,'percentSaved','market')
add_deviation_feature(data,'priceDiff','market')
add_deviation_feature(data,'actualPrice','market')
add_deviation_feature(data,'suggPrice','market')

datapivot = pd.pivot_table(data,values='percentSaved',index='market',columns='productCategory',aggfunc=np.mean)
plt.figure(figsize = (20,10))
sns.heatmap(datapivot,cmap='YlGnBu')
plt.xlabel('Product Category', color='black',size=10)
plt.ylabel('Made in', color='black',size=10)
plt.xticks(size=20)
plt.yticks(size=20)

data['avgRating_zscore'] = (data['avgRating'] - data['avgRating'].mean())/data['avgRating'].std()

noOutliers = data[~(np.abs(data.suggPrice-data.suggPrice.mean()) > (3*data.suggPrice.std()))]

numMask = ['suggPrice','numReviews','avgRating','questions','answers','answersPerQuestion','percentSaved','France','Germany','India','Italy','Japan','Other APAC','Other Americas','Other EMEA','USA']
pvalMask = ['suggPrice','answers','percentSaved','France','Germany','USA']

testData = noOutliers[(noOutliers.suggPrice > 99)][pvalMask]

x = testData.drop('percentSaved',axis=1)
y = testData['percentSaved']

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=100)

linear=LinearRegression()
# poly = PolynomialFeatures(degree=2)
# X_trpoly = poly.fit_transform(X_train)
# X_tepoly = poly.transform(X_test)

# scaler = StandardScaler()
# X_trscaled = scaler.fit_transform(X_train)
# X_tescaled = scaler.transform(X_test)

linear.fit(X_train,y_train)
print(linear.score(X_train,y_train))
print (linear.score(X_test,y_test))
print (linear.coef_)

X_sm = sm.add_constant(X_train)
model = sm.OLS(y_train,X_sm)
results = model.fit()
print (results.summary())

sns.distplot(testData.percentSaved);
df1 = X_test

df2 = pd.Series(linear.predict(X_test))
df1.reset_index(inplace=True)
df1['y predicted'] =df2
df1['residuals'] = df1['Y actual'] - df1['y predicted']

zero = [0 for i in df1['y predicted']]


bg_color = '#E1DBB0'
fg_color = 'black'

fig = plt.figure(facecolor=bg_color, edgecolor=fg_color,figsize=(20,10))
axes = fig.add_subplot(111)
axes.patch.set_facecolor(bg_color)
axes.xaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
axes.yaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
for spine in axes.spines.values():
    spine.set_color(fg_color)

x = df1['y predicted']
y = df1['residuals']

plt.scatter(x, y,c='black',axes=axes)
plt.plot(df1['y predicted'],zero,c='red')
plt.xlabel('y predicted', color=fg_color,size=40)
plt.ylabel('residuals', color=fg_color,size=40)
plt.grid(None)
#plt.figure(figsize=(20,10))
plt.show()



#sns.distplot(df1['residuals'],color='#ffdb58')

plt.figure(figsize = (20,10))
ax = sns.distplot(df1.residuals, fit=norm, kde=False,color='#ffb158')
ax.grid(False)
#ax.fig(figsize=(20,10));



