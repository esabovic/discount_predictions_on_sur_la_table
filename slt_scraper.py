#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 12:37:31 2019

@author: elizabeth sabovic
"""

"""
This contains all of the functions used to scrape the homepage for all of
the product categories, all product links on each category page, and all necessary
info on each product page
"""


import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import numpy as np


def getPageData(url):
    response = requests.get(url)
    page = response.text
    return page

def actual_price(soupfile):
    price = 0
    try:
        price = (soupfile.find("span",class_="hide", itemprop="price").next_element)
    except:
        return price
    return price

def sugg_price(soupfile):
    price = '0'
    try:
        price = str(soupfile.find("span", id="product-priceList")).split("\"")[1]
    except:
        return price
    return price

def reviews(soupfile):
    allreviews = [0,0,0,0,0]
    try:
        five_ = int(soupfile.find("div", id="TTreviewSummaryBreakdown-5").next_element)
        four_ = int(soupfile.find("div", id="TTreviewSummaryBreakdown-4").next_element)
        three_ = int(soupfile.find("div", id="TTreviewSummaryBreakdown-3").next_element)
        two_ = int(soupfile.find("div", id="TTreviewSummaryBreakdown-2").next_element)
        one_ = int(soupfile.find("div", id="TTreviewSummaryBreakdown-1").next_element)
        allreviews = [one_, two_, three_, four_, five_]
    except:
        return allreviews
    return allreviews

def avg_review(fiveratings):
    val = 0
    avg = 0
    try:
        for i in range(0,5):
            val += (fiveratings[i]*(i+1))
        avg = val/sum(fiveratings)
    except:
        return avg
    return avg

def ques_ans_list(soupfile):
    ques_ans = ['0','0','0','0','0']
    try:
        ques_ans = str(soupfile.find_all("span", class_="TTrespDesktopLandscapeDisp")).split(" ")
    except:
        return ques_ans
    return ques_ans

def manufacturer(soupfile):
    s = 'Manufacturer'
    x = (soupfile.find("div", id='product-moreInfo-specs').find('li'))
    while True:
        c = str(x)
        if s in c or not x:
            break
        x = x.next_sibling
    if len(c)>0:
        parse = c.split("Manufacturer")[1].split("<")[0]
        return parse
    return c

def country(soupfile):
    s = 'Made in'
    x = (soupfile.find("div", id='product-moreInfo-specs').find('li'))
    try:
        while True:
            c = str(x)
            if s in c or not x:
                break
            x = x.next_sibling
        if len(c)>0:
            parse = c.split("Made in ")[1].split("<")[0]
            return parse
        return c
    except:
        return None

def category(soupfile):
    s = str(soupfile.find('div', id='product-breadcrumbs').find('a').next_element)
    return s

def products_param(catlink):
    x = str(catlink).split("\"")[5]
    add_string = '?&No=0&Nrpp=10000'
    return (x + add_string)



slt = 'https://www.surlatable.com'
homePage = BeautifulSoup(getPageData(slt), "lxml")
mainCats = [(slt + products_param(x)) for x in (homePage.find_all('a', class_="SCAHeader"))]
productPages = pd.DataFrame(columns = ['productLink','category'])

for cat in mainCats:
    soupCat = BeautifulSoup(getPageData(cat), "lxml")
    products = [(slt + str(x).split("\"")[3]) for x in soupCat.find_all('a', class_="name")]
    for p in products:
        df = pd.DataFrame([[p,cat]],columns = ['productLink','category'])
        productPages = productPages.append(df)

data = (pd.DataFrame(columns=['productLink',
                              'actualPrice',
                              'suggPrice',
                              'numReviews',
                              'avgRating',
                              'questions',
                              'answers',
                              'brand',
                              'producedIn',
                              'productCategory']))

for p in products.productLink:
    filename = str(len(data.productLink))+"_surlatabledata.csv"
    if len(data.productLink)%100==0:
        data.to_csv(filename)
    try:
        q = BeautifulSoup(getPageData(p), "lxml")
        temp = (pd.DataFrame([[p,
                           actual_price(q),
                           sugg_price(q),
                           sum(reviews(q)),
                           avg_review(reviews(q)),
                           ques_ans_list(q)[2],
                           ques_ans_list(q)[4],
                           manufacturer(q),
                           country(q),
                           category(q)]],
                         columns=['productLink',
                                  'actualPrice',
                                  'suggPrice',
                                  'numReviews', 
                                  'avgRating',
                                  'questions',
                                  'answers',
                                  'brand',
                                  'producedIn',
                                  'productCategory']))
        data = data.append(temp)
    except:
        temp = (pd.DataFrame([[p,
                           '',
                           '',
                           '',
                           '',
                           '',
                           '',
                           '',
                           '',
                           '']],
                         columns=['productLink',
                                  'actualPrice',
                                  'suggPrice',
                                  'numReviews', 
                                  'avgRating',
                                  'questions',
                                  'answers',
                                  'brand',
                                  'producedIn',
                                  'productCategory']))
        data = data.append(temp)

data.to_csv('surlatable_completedata.csv')
