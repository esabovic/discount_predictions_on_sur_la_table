#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 13:05:27 2019

@author: elizabeth sabovic
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import train_test_split

def add_deviation_feature(X, feature, category):
    
    # temp groupby object
    category_gb = X.groupby(category)[feature]
    
    # create columns of category means and standard deviations
    category_mean = category_gb.transform(lambda x: x.mean())
    category_std = category_gb.transform(lambda x: x.std())
    
    # compute stds from category mean for each feature value,
    # add to X as new feature
    deviation_feature = (X[feature] - category_mean) / category_std 
    X[feature + '_Dev_' + category] = deviation_feature


data = pd.read_csv('surlatable_completedata.csv')
data.drop('Unnamed: 0', axis=1,inplace=True)
data.drop(data[data.answers.str.isnumeric()==False].index,inplace=True)
numericaldata = ['actualPrice','suggPrice','numReviews','avgRating','questions','answers']
for i in numericaldata:
    try:
        data[i] = data[i].replace('[\$,]', '', regex=True).astype(float)
    except:
        continue

data=data.dropna()
data.brand=data.brand.replace(':','',regex=True)
data.brand=data.brand.str.strip()
data=data.drop_duplicates(subset='productLink',keep='last')
data=data.sort_index()

"""
Feature engineering
"""

data.suggPrice = np.where(data['suggPrice']==0, data.actualPrice, data.suggPrice)
data['priceDiff'] = data.suggPrice - data.actualPrice
data['percentSaved'] = data.priceDiff/data.suggPrice
data['answersPerQuestion'] = data.answers/data.questions
data.producedIn = np.where(data.producedIn.str.contains('USA|U.S.A'),'USA',data.producedIn)
data.producedIn = np.where(data.producedIn.str.contains('Czech Republic'),'Czech Republic',data.producedIn)
ratingExists = data[data.avgRating>0].copy()
brands = pd.DataFrame(ratingExists.brand.value_counts())
brands.sort_index(inplace=True)
lessthan20 = brands[brands.brand<=20]
brandslist = list(lessthan20.index)
ratingExists.brand = ratingExists.brand.apply(lambda x: "other" if x in brandslist else x)
categories = pd.DataFrame(ratingExists.productCategory.value_counts())
catlist = list(categories[categories.productCategory<=25].index)
ratingExists.productCategory = ratingExists.productCategory.apply(lambda x: "Other" if x in catlist else x)
ratingExists.producedIn = ratingExists.producedIn.apply(lambda x: x.strip())

countrydict = {
    'Denmark':'Other EMEA',
    'Portugal':'Other EMEA',
    'Belgium':'Other EMEA',
    'Taiwan':'Other APAC',
    'Thailand':'Other APAC',
    'Indonesia':'Other APAC',
    'Switzerland':'Other EMEA',
    'Vietnam':'Other APAC',
    'Hungary':'Other EMEA',
    'Poland':'Other EMEA',
    'Turkey':'Other EMEA',
    'The Philippines':'Other APAC',
    'Netherlands':'Other EMEA',
    'Mexico':'Other Americas',
    'Canada':'Other Americas',
    'Romania':'Other EMEA',
    'England':'Other EMEA',
    'Spain':'Other EMEA',
    'Israel':'Other EMEA',
    'Korea':'Other APAC',
    'United Kingdom':'Other EMEA',
    'Tahiti':'Other EMEA',
    'Chile':'Other Americas',
    'Pakistan':'Other APAC',
    'Nigeria':'Other EMEA',
    'Austria':'Other EMEA',
    'Sweden':'Other EMEA',
    'China':'China',
    'USA':'USA',
    'France':'France',
    'Germany':'Germany',
    'Japan':'Japan',
    'Italy':'Italy',
    'India':'India'
}

ratingExists['market'] = ratingExists.producedIn.map(countrydict)
ratingExists = ratingExists[ratingExists.actualPrice <= ratingExists.suggPrice]

add_deviation_feature(ratingExists,'actualPrice','productCategory')
add_deviation_feature(ratingExists,'percentSaved','productCategory')

marketdummies = pd.get_dummies(ratingExists.market)

ratingExists = pd.concat([ratingExists, marketdummies], axis=1, sort=False)
ratingExists.to_csv("cleaned_brand_data.csv")


