# %% [markdown]
# # Amazon Alexa Review - Sentiment Analysis
# 
# Analyzing the Amazon Alexa dataset and building classification models to predict if the sentiment of a given input sentence is positive or negative.

# %% [markdown]
# ### Importing required libraries

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.stem.porter import PorterStemmer
nltk.download('stopwords')
from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words('english'))

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
from wordcloud import WordCloud
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
import pickle
import re

# %%
%pip install wordcloud

# %% [markdown]
# ### Exploratory Data Analysis

# %%
#Load the data

data = pd.read_csv(r"Data\amazon_alexa.tsv", delimiter = '\t', quoting = 3)

print(f"Dataset shape : {data.shape}")

# %%
data.head()

# %%
#Column names

print(f"Feature names : {data.columns.values}")

# %%
#Check for null values

data.isnull().sum()

# %% [markdown]
# There is one record with no 'verified_reviews' (null value)

# %%
#Getting the record where 'verified_reviews' is null 

data[data['verified_reviews'].isna() == True]

# %%
#We will drop the null record

data.dropna(inplace=True)

# %%
print(f"Dataset shape after dropping null values : {data.shape}")

# %%
#Creating a new column 'length' that will contain the length of the string in 'verified_reviews' column

data['length'] = data['verified_reviews'].apply(len)

# %%
data.head()

# %% [markdown]
# The 'length' column is new generated column - stores the length of 'verified_reviews' for that record. Let's check for some sample records

# %%
#Randomly checking for 10th record

print(f"'verified_reviews' column value: {data.iloc[10]['verified_reviews']}") #Original value
print(f"Length of review : {len(data.iloc[10]['verified_reviews'])}") #Length of review using len()
print(f"'length' column value : {data.iloc[10]['length']}") #Value of the column 'length'

# %% [markdown]
# We can see that the length of review is the same as the value in the length column for that record

# %% [markdown]
# Datatypes of the features

# %%
data.dtypes

# %% [markdown]
# * rating, feedback and length are integer values <br>
# * date, variation and verified_reviews are string values

# %% [markdown]
# ### Analyzing 'rating' column
# 
# This column refers to the rating of the variation given by the user

# %%
len(data)

# %%
#Distinct values of 'rating' and its count  

print(f"Rating value count: \n{data['rating'].value_counts()}")

# %% [markdown]
# Let's plot the above values in a bar graph

# %%
#Bar plot to visualize the total counts of each rating

data['rating'].value_counts().plot.bar(color = 'red')
plt.title('Rating distribution count')
plt.xlabel('Ratings')
plt.ylabel('Count')
plt.show()

# %%
#Finding the percentage distribution of each rating - we'll divide the number of records for each rating by total number of records

print(f"Rating value count - percentage distribution: \n{round(data['rating'].value_counts()/data.shape[0]*100,2)}")

# %% [markdown]
# Let's plot the above values in a pie chart

# %%
fig = plt.figure(figsize=(7,7))

colors = ('red', 'green', 'blue','orange','yellow')

wp = {'linewidth':1, "edgecolor":'black'}

tags = data['rating'].value_counts()/data.shape[0]

explode=(0.1,0.1,0.1,0.1,0.1)

tags.plot(kind='pie', autopct="%1.1f%%", shadow=True, colors=colors, startangle=90, wedgeprops=wp, explode=explode, label='Percentage wise distrubution of rating')

from io import  BytesIO

graph = BytesIO()

fig.savefig(graph, format="png")

# %% [markdown]
# ### Analyzing 'feedback' column
# 
# This column refers to the feedback of the verified review

# %%
#Distinct values of 'feedback' and its count 

print(f"Feedback value count: \n{data['feedback'].value_counts()}")

# %% [markdown]
# There are 2 distinct values of 'feedback' present - 0 and 1. Let's see what kind of review each value corresponds to.

# %% [markdown]
# feedback value = 0

# %%
#Extracting the 'verified_reviews' value for one record with feedback = 0

review_0 = data[data['feedback'] == 0].iloc[1]['verified_reviews']
print(review_0)

# %%
#Extracting the 'verified_reviews' value for one record with feedback = 1

review_1 = data[data['feedback'] == 1].iloc[1]['verified_reviews']
print(review_1)

# %% [markdown]
# From the above 2 examples we can see that feedback **0 is negative review** and **1 is positive review**

# %% [markdown]
# Let's plot the feedback value count in a bar graph

# %%
#Bar graph to visualize the total counts of each feedback

data['feedback'].value_counts().plot.bar(color = 'blue')
plt.title('Feedback distribution count')
plt.xlabel('Feedback')
plt.ylabel('Count')
plt.show()

# %%
#Finding the percentage distribution of each feedback - we'll divide the number of records for each feedback by total number of records

print(f"Feedback value count - percentage distribution: \n{round(data['feedback'].value_counts()/data.shape[0]*100,2)}")

# %% [markdown]
# Feedback distribution <br>
# * 91.87% reviews are positive <br>
# * 8.13% reviews are negative

# %%
fig = plt.figure(figsize=(7,7))

colors = ('red', 'green')

wp = {'linewidth':1, "edgecolor":'black'}

tags = data['feedback'].value_counts()/data.shape[0]

explode=(0.1,0.1)

tags.plot(kind='pie', autopct="%1.1f%%", shadow=True, colors=colors, startangle=90, wedgeprops=wp, explode=explode, label='Percentage wise distrubution of feedback')

# %% [markdown]
# Let's see the 'rating' values for different values of 'feedback'

# %%
#Feedback = 0
data[data['feedback'] == 0]['rating'].value_counts()

# %%
#Feedback = 1
data[data['feedback'] == 1]['rating'].value_counts()

# %% [markdown]
# ##### If rating of a review is 1 or 2 then the feedback is 0 (negative) and if the rating is 3, 4 or 5 then the feedback is 1 (positive).

# %% [markdown]
# ### Analyzing 'variation' column
# 
# This column refers to the variation or type of Amazon Alexa product. Example - Black Dot, Charcoal Fabric etc.

# %%
#Distinct values of 'variation' and its count 

print(f"Variation value count: \n{data['variation'].value_counts()}")

# %%
#Bar graph to visualize the total counts of each variation

data['variation'].value_counts().plot.bar(color = 'orange')
plt.title('Variation distribution count')
plt.xlabel('Variation')
plt.ylabel('Count')
plt.show()

# %%
#Finding the percentage distribution of each variation - we'll divide the number of records for each variation by total number of records

print(f"Variation value count - percentage distribution: \n{round(data['variation'].value_counts()/data.shape[0]*100,2)}")

# %% [markdown]
# Mean rating according to variation

# %%
data.groupby('variation')['rating'].mean()

# %% [markdown]
# Let's analyze the above ratings

# %%
data.groupby('variation')['rating'].mean().sort_values().plot.bar(color = 'brown', figsize=(11, 6))
plt.title("Mean rating according to variation")
plt.xlabel('Variation')
plt.ylabel('Mean rating')
plt.show()

# %% [markdown]
# ### Analyzing 'verified_reviews' column
# 
# This column contains the textual review given by the user for a variation for the product.

# %%
data['length'].describe()

# %% [markdown]
# Length analysis for full dataset

# %%
sns.histplot(data['length'],color='blue').set(title='Distribution of length of review ')

# %% [markdown]
# Length analysis when feedback is 0 (negative)

# %%
sns.histplot(data[data['feedback']==0]['length'],color='red').set(title='Distribution of length of review if feedback = 0')

# %% [markdown]
# Length analysis when feedback is 1 (positive)

# %%
sns.histplot(data[data['feedback']==1]['length'],color='green').set(title='Distribution of length of review if feedback = 1')

# %% [markdown]
# Lengthwise mean rating

# %%
data.groupby('length')['rating'].mean().plot.hist(color = 'blue', figsize=(7, 6), bins = 20)
plt.title(" Review length wise mean ratings")
plt.xlabel('ratings')
plt.ylabel('length')
plt.show()

# %%
cv = CountVectorizer(stop_words='english')
words = cv.fit_transform(data.verified_reviews)

# %%
# Combine all reviews
reviews = " ".join([review for review in data['verified_reviews']])
                        
# Initialize wordcloud object
wc = WordCloud(background_color='white', max_words=50)

# Generate and plot wordcloud
plt.figure(figsize=(10,10))
plt.imshow(wc.generate(reviews))
plt.title('Wordcloud for all reviews', fontsize=10)
plt.axis('off')
plt.show()

# %% [markdown]
# Lets find the unique words in each feedback category

# %%
# Combine all reviews for each feedback category and splitting them into individual words
neg_reviews = " ".join([review for review in data[data['feedback'] == 0]['verified_reviews']])
neg_reviews = neg_reviews.lower().split()

pos_reviews = " ".join([review for review in data[data['feedback'] == 1]['verified_reviews']])
pos_reviews = pos_reviews.lower().split()

#Finding words from reviews which are present in that feedback category only
unique_negative = [x for x in neg_reviews if x not in pos_reviews]
unique_negative = " ".join(unique_negative)

unique_positive = [x for x in pos_reviews if x not in neg_reviews]
unique_positive = " ".join(unique_positive)


# %%
wc = WordCloud(background_color='white', max_words=50)

# Generate and plot wordcloud
plt.figure(figsize=(10,10))
plt.imshow(wc.generate(unique_negative))
plt.title('Wordcloud for negative reviews', fontsize=10)
plt.axis('off')
plt.show()

# %% [markdown]
# Negative words can be seen in the above word cloud - garbage, pointless, poor, horrible, repair etc

# %%
wc = WordCloud(background_color='white', max_words=50)

# Generate and plot wordcloud
plt.figure(figsize=(10,10))
plt.imshow(wc.generate(unique_positive))
plt.title('Wordcloud for positive reviews', fontsize=10)
plt.axis('off')
plt.show()

# %% [markdown]
# Positive words can be seen in the above word cloud - good, enjoying, amazing, best, great etc

# %% [markdown]
# # Preprocessing and Modelling

# %% [markdown]
# To build the corpus from the 'verified_reviews' we perform the following - <br>
# 1. Replace any non alphabet characters with a space
# 2. Covert to lower case and split into words
# 3. Iterate over the individual words and if it is not a stopword then add the stemmed form of the word to the corpus

# %%
corpus = []
stemmer = PorterStemmer()
for i in range(0, data.shape[0]):
  review = re.sub('[^a-zA-Z]', ' ', data.iloc[i]['verified_reviews'])
  review = review.lower().split()
  review = [stemmer.stem(word) for word in review if not word in STOPWORDS]
  review = ' '.join(review)
  corpus.append(review)

# %% [markdown]
# Using Count Vectorizer to create bag of words

# %%
cv = CountVectorizer(max_features = 2500)

#Storing independent and dependent variables in X and y
X = cv.fit_transform(corpus).toarray()
y = data['feedback'].values

# %%
#Saving the Count Vectorizer
pickle.dump(cv, open('Models/countVectorizer.pkl', 'wb'))

# %% [markdown]
# Checking the shape of X and y

# %%
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")

# %% [markdown]
# Splitting data into train and test set with 30% data with testing.

# %%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 15)

print(f"X train: {X_train.shape}")
print(f"y train: {y_train.shape}")
print(f"X test: {X_test.shape}")
print(f"y test: {y_test.shape}")

# %%
print(f"X train max value: {X_train.max()}")
print(f"X test max value: {X_test.max()}")

# %% [markdown]
# We'll scale X_train and X_test so that all values are between 0 and 1.

# %%
scaler = MinMaxScaler()

X_train_scl = scaler.fit_transform(X_train)
X_test_scl = scaler.transform(X_test)

# %%
#Saving the scaler model
pickle.dump(scaler, open('Models/scaler.pkl', 'wb'))

# %% [markdown]
# #### Random Forest

# %%
#Fitting scaled X_train and y_train on Random Forest Classifier
model_rf = RandomForestClassifier()
model_rf.fit(X_train_scl, y_train)

# %%
#Accuracy of the model on training and testing data
 
print("Training Accuracy :", model_rf.score(X_train_scl, y_train))
print("Testing Accuracy :", model_rf.score(X_test_scl, y_test))

# %%
#Predicting on the test set
y_preds = model_rf.predict(X_test_scl)

# %%
#Confusion Matrix
cm = confusion_matrix(y_test, y_preds)

# %%
cm_display = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=model_rf.classes_)
cm_display.plot()
plt.show()

# %% [markdown]
# K fold cross-validation

# %%
accuracies = cross_val_score(estimator = model_rf, X = X_train_scl, y = y_train, cv = 10)

print("Accuracy :", accuracies.mean())
print("Standard Variance :", accuracies.std())

# %% [markdown]
# Applying grid search to get the optimal parameters on random forest

# %%
params = {
    'bootstrap': [True],
    'max_depth': [80, 100],
    'min_samples_split': [8, 12],
    'n_estimators': [100, 300]
}

# %%
cv_object = StratifiedKFold(n_splits = 2)

grid_search = GridSearchCV(estimator = model_rf, param_grid = params, cv = cv_object, verbose = 0, return_train_score = True)
grid_search.fit(X_train_scl, y_train.ravel())

# %%
#Getting the best parameters from the grid search


print("Best Parameter Combination : {}".format(grid_search.best_params_))

# %%
print("Cross validation mean accuracy on train set : {}".format(grid_search.cv_results_['mean_train_score'].mean()*100))
print("Cross validation mean accuracy on test set : {}".format(grid_search.cv_results_['mean_test_score'].mean()*100))
print("Accuracy score for test set :", accuracy_score(y_test, y_preds))

# %% [markdown]
# #### XgBoost

# %%
model_xgb = XGBClassifier()
model_xgb.fit(X_train_scl, y_train)

# %%
#Accuracy of the model on training and testing data
 
print("Training Accuracy :", model_xgb.score(X_train_scl, y_train))
print("Testing Accuracy :", model_xgb.score(X_test_scl, y_test))

# %%
y_preds = model_xgb.predict(X_test)

# %%
#Confusion Matrix
cm = confusion_matrix(y_test, y_preds)
print(cm)

# %%
cm_display = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=model_xgb.classes_)
cm_display.plot()
plt.show()

# %%
#Saving the XGBoost classifier
pickle.dump(model_xgb, open('Models/model_xgb.pkl', 'wb'))

# %% [markdown]
# #### Decision Tree Classifier

# %%
model_dt = DecisionTreeClassifier()
model_dt.fit(X_train_scl, y_train)

# %%
#Accuracy of the model on training and testing data
 
print("Training Accuracy :", model_dt.score(X_train_scl, y_train))
print("Testing Accuracy :", model_dt.score(X_test_scl, y_test))

# %%
y_preds = model_dt.predict(X_test)

# %%
#Confusion Matrix
cm = confusion_matrix(y_test, y_preds)
print(cm)

# %%
cm_display = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=model_dt.classes_)
cm_display.plot()
plt.show()

# %%



