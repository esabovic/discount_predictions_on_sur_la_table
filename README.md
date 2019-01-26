# Predicting discount rates on https://SurLaTable.com
Scraping Sur La Table product pages and predicting a discount rate on their products

As an avid home cook, I thought it would be useful to try to predict how much of a discount I can get at Sur La Table based on product attributes

I used BeautifulSoup to scrape the site for all of its products to obtain:
 - the MSRP
 - actual price
 - number of reviews
 - number of questions
 - number of answers
 - the average rating
 - brand
 - country of production
 - product category
 
There were quite a few product pages that were 404s as well as had missing data, so my dataset shrunk from 7600 product links to ~2400 product pages. Ultimately, I decided to look at products that were at least $100 (where a discount would strongly encourage someone to buy an item previously thought to be a steep expenditure). This left me with only around 900 items (a disappointing amount of data, unfortunately).
 
 # EDA
 
 While doing some intial EDA, I found that discounts were distributed in a mix of a Bernoulli and Gaussian distribution:
 
 ![discount distribution](https://github.com/esabovic/discount_predictions_on_sur_la_table/blob/master/discount_distribution.png?raw=true "discount distribution")
 
 After grouping countries of production together based on volume of products produced, I looked at a heatmap of the average discount by product category by region of production:
 
 ![discount means](https://github.com/esabovic/discount_predictions_on_sur_la_table/blob/master/category_market_heatmap.png?raw=true "discount means")
In other words, Chinese-produced Kitchen Tools were, on average, more heavily discounted than say, US-made knives.

Given some of these initial findings, I set out to find a linear model that might predict how these discounts are constructed. Prior to fitting a model, I didn't find an correlations between any of the variables. Although these averages were more or less telling, it didn't look like there was any specific linear pattern. I created the following interaction variables:

- answersPerQuestion
- priceDiff (MSRP or suggPrice - actualPrice)
- averageRating (average of 5 star, 4 star, 3 star, 2 star, and 1 star ratings)

While I didn't see any correlations between discount rate and averageRating or answersPerQuestion, I completely ignored priceDiff because it was entirely dependent on the same variables that I used to calculate discount rate (so that didn't really matter).

I created dummy variables for country of production and saw there were very small correlations as well, so ultimately I wasn't expecting to find much luck, but I was ultimately pleasantly surprised.

## Linear regression modeling

Using skLearn, I created a training and test set using the train_test_split function and ran a regression analysis and resulted in a .15 r2 score. Since using Lasso and Ridge didn't improve my score, I ended up putting my data through statsmodels' OLS() and removed the variables with p-values of their tscores of greater than .05. Ultimately, I was able to increase my r2 score for both my train and test data to .21. The features that I was able to keep in my model were:

- suggPrice (or MSRP) with a coefficient of 0.0002
- answers with a coefficient of 0.0016
- France (dummy) with a coefficient of -0.0560
- Germany (dummy) with a coefficient of 0.060
- USA (dummy) with a coefficient of -0.1356

## In conclusion

- French or USA produced things don't go on sale as much as German-produced items.
- The higher the value, the more discounted the item will be.
- The more answers a product has, the more of a discount the item will have.

How I actually interpret this:

- Although my model doesn't have TOO much predictive capability, it ultimately does say, with a 21% explanation of variance, certain items are in fact discounted more heavily. In retrospect, I should re-imagine this problem as "what is the likely that an item will go on sale?", especially because of the distribution of discounts. Here are the residual plots:

# Residuals vs Y-predicted:
![residual plot](https://github.com/esabovic/discount_predictions_on_sur_la_table/blob/master/residuals_ypredicted_scatter.png?raw=true "residual plot")

That "line" of residuals essentially say that I'm predicting a discount when there shouldn't be on in the first place. This was my second hint to re-framing this as a classification problem.

# Distribution of residuals:
![dist of residuals](https://github.com/esabovic/discount_predictions_on_sur_la_table/blob/master/residuals_distribution.png?raw=true "dist of residuals")

Since the residuals were relatively normally distributed, I could also re-frame this problem as "given there IS a discount, how big is the discount?"


 
