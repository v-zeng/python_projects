# -*- coding: utf-8 -*-
"""

**Problem Definition**
Wisconsin breast cancer data set, which is considered a good data set for Machine Learning (ML). Aim is to predict whether cancer incidences in a population are benign or malignant, using 30 feature variables available on Kaggle (https://www.kaggle.com/uciml/breast-cancer-wisconsin-data). 
To do so 1) Performed the exploratory data analysis (EDA), to check general patterns of the data (description, type of data, presence of outliers and missing data, etc); 
2) Used different tools to decrease the dimension and not lose information from the data set; 
3) Created a classification model, and test it.
"""

#@title
#Please comment out this block of code when running as .py
# You will need the dataset saved as 'data.csv'
#upload dataset for google colab
from google.colab import files
uploaded = files.upload()

#@title
# import packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from sklearn import decomposition
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split
from matplotlib.pyplot import imshow  
import random
import sklearn.metrics as metrics
from sklearn import preprocessing



#@title
# Load dataset function to read csv files
def load_dataset(path):
    df = pd.read_csv(path)
    return df


# Separate predictions and response function
def make_predictors_response(data, response_name):
    predictors = data.drop(response_name, axis=1)
    response = data[response_name]
    return predictors, response


# Generate Classification Report and AUC-ROC
def make_predictions(model, predictors_test, response_test):
    clf_report = classification_report(response_test, model.predict(predictors_test))
    auc_score = roc_auc_score(response_test, model.predict_proba(predictors_test)[:, 1])
    print("\nResponse Test Values:")
    print(response_test.values)
    print("\nModel Prediction:")
    print(model.predict(predictors_test))
    print("\nNegative(0): Benign, Positive(1): Malignant\n")
    print("\nConfusion Matrix:")
    print(confusion_matrix(response_test.values, model.predict(predictors_test)))
    return clf_report + "The AUC score is: " + str(auc_score)


# Make Logistic Regression model
def run_logistic_regression(train_predictors, train_response):
    clf_lr = LogisticRegression(random_state=42, max_iter=500).fit(train_predictors, train_response)
    return clf_lr


# Make Decision Tree model
def run_decision_tree(train_predictors, train_response):
    clf_dt = DecisionTreeClassifier().fit(train_predictors, train_response)
    return clf_dt


# Make Random Forest model
def run_random_forest(train_predictors, train_response):
    clf_rf = RandomForestClassifier(n_estimators=100, oob_score=True, random_state=42).fit(train_predictors,
                                                                                           train_response)
    return clf_rf


# Implement Naive Bayes algortihm
def run_naive_bayes(train_predictors, train_response):
    clf_gnb = GaussianNB().fit(train_predictors, train_response)
    return clf_gnb


# Implement SVM model with linear kernel
def run_SVM(train_predictors, train_response):
    clf_svm = svm.SVC(kernel='linear', probability=True).fit(train_predictors, train_response)
    return clf_svm


# Draw PCA and scree plot for 31 iterations
def draw_pca_plot(train_predictors):
    explain_variance_arr = []
    for i in range(1, 31):
        pca = decomposition.PCA(n_components=i)
        pca.fit_transform(train_predictors)
        explained_variance = pca.explained_variance_ratio_.tolist()
        explain_variance_arr.append(sum(explained_variance))
        print(str(i) + "th iteration complete....!")

    plt.figure(figsize=(12, 6))
    plt.plot(range(1, 31), explain_variance_arr, color='red', linestyle='dashed', marker='o',
             markerfacecolor='blue', markersize=10)
    plt.title('Variance explained by different Principle Components')
    plt.xlabel('Number of Principle Components')
    plt.ylabel('Explained Variance')
    plt.show()

    return explain_variance_arr


# Run PCA on model with controlled Principal components
def run_pca(train_predictors, components):
    pca = decomposition.PCA(n_components=components)
    principalComponents = pca.fit_transform(train_predictors)
    explained_variance = pca.explained_variance_ratio_.tolist()
    print(sum(explained_variance))
    return principalComponents


# Make Voting Ensemble Model using others
def run_voting_ensemble(clf1, clf2, clf3, clf4, train_predictors, test_response):
    eclf1 = VotingClassifier(estimators=[('lr', clf1), ('rf', clf2), ('gnb', clf3), ('dt', clf4)],
                             voting='soft')
    eclf1 = eclf1.fit(train_predictors, test_response)
    return eclf1

"""**Below**

Take a look at the first 10 records.
"""

#@title
rawDF = load_dataset("data.csv")
# #look at first 10 records
(rawDF.head(n=10).T)

"""**Below**

Take a look at the last 10 records.
"""

#@title
# #look at last 10 records
(rawDF.tail(n=10).T)

"""**Below**

Except for diagnosis, our class label, the rest of the features are numeric variables. Drop "Unnamed: 32" and "id" columns. The "id" column will not contribute to our classification. The "Unnamed: 32" feature has NaN values and is therefore droppable. After dropping the two columns, check the number of records and columns in the dataframe, followed by the data schema.
"""

#@title
#drop Unnamed and id columns
droppedDF = rawDF.drop("Unnamed: 32", axis=1)
# print(droppedDF.columns)
data = droppedDF.drop("id", axis=1)
# #check number records and columns in df
print(data.shape)
# #check column names
print(data.columns)
# #check data schema
print(data.info()) #
# # 'id' = int64, 'diagnosis' = object, all other columns = float64

"""**Below**

Check the number of Nulls (empty) in each column and print the rows containing zero values.
"""

#@title
# #check number of Nulls (Empty) in each column
print(data.isnull().sum())
# 569 nulls in "Unnamed: 32" <-- remove this column
# print the row containing 0 
data[(data == 0).any(axis=1)]

"""**Below**

Calculate some statistics for the numeric attributes.

We can see that there several ranges of values for the features. Most notable is the area_mean feature, which has a min of 143.5, a max of 2501, and a mean of approximately 654.89. That feature has much higher values than a feature such as fractal_dimension_se, which has a min of 0.000895, a max of 0.02984, and a mean of 0.020542. We'll need to transform the data by standardizing it before feature selection or PCA.
"""

#@title
# #calculate statistics for numeric attributes 
(data.describe().T)

#@title
#Distribution of diagnosis

# diagnosis countplot
sns.countplot(data=data,x='diagnosis')
plt.show()
#diagnosis (percentages)
data.diagnosis.value_counts(normalize=True).plot(kind="bar", alpha=0.5)
plt.show()

"""**Diagnosis distribution**

There are more benign tumor records than malignant (benign: 62.7%, malignant: 37.3%). Data imbalanced, and therefore may be more biased towards benign class due to this.
"""

#@title
#Univariate analysis
#group variables
cleanDFmean = data.iloc[:,1:11] # only mean variables
cleanDFse = data.iloc[:,11:21] # only standard error (se) variables
cleanDFworst = data.iloc[:,-10:] # only worst or largest (mean of the three largest values) variables
# mean distributions
fig, axes = plt.subplots(2, 5, figsize=(20,15))
for i, ax in zip(cleanDFmean, axes.flat):
    sns.histplot(data=data, x=i, kde=True, hue='diagnosis', ax=ax)
plt.suptitle("Distribution of 'mean' variables")
plt.show()
# se distributions
fig, axes = plt.subplots(2, 5, figsize=(20,15))
for i, ax in zip(cleanDFse, axes.flat):
    sns.histplot(data=data, x=i, kde=True, hue='diagnosis', ax=ax)
plt.suptitle("Distribution of standard error variables")
plt.show()
# worst distributions
fig, axes = plt.subplots(2, 5, figsize=(20,15))
for i, ax in zip(cleanDFworst, axes.flat):
    sns.histplot(data=data, x=i, kde=True, hue='diagnosis', ax=ax)
plt.suptitle("Distribution of 'worst' variables")
plt.show()

"""**Histograms**

Means subset: Histogram for mean of features  showing the peaks and spreads of mean variables for the two conditions 'benign' (B) and 'malignant' (M). For some variables, the peaks and spreads of benign class and malignant class are slightly different. But some variables, the two classes have similar spreads and peaks that overlapping with each other (e.g. texture_mean, smoothness_mean, symmetry_mean and fractal_dimension_mean), thereby, they may not be good for estimating the differences between 'benign' and 'malignant'.
(all the distributions are almost normal distributions; applying statistical methods will yield good results due to the Central Limit Theorem. Data may need to be transformed (e.g., log).)

SE subset: Histogram showing the distribution of standard error variables (se). Peaks and spreads are overlapping extensively for most of the variables. The distribution is right-skewed - so maybe these variables have exponential distribution or lognormal distribution, rather than normal distribution.

Worst subset: Similarly to the histogram of means. Histogram showing the peaks and spreads of 'worst' variables for the two conditions 'benign' (B) and 'malignant' (M). Variables have similar peaks and spreads are symmetry_worst and fractal_dimension_worst. For some variables, the spreads are highly overlapping (e.g. texture_worst, and compactness_worst). They may not be good for estimating the differences between 'benign' and 'malignant'.
"""

#@title
# mean distributions(scatterplots)
# means
fig, axes = plt.subplots(2, 5, figsize=(25,15))
for i, ax in zip(cleanDFmean, axes.flat):
    sns.scatterplot(x=data['diagnosis'], y=data[i], ax=ax)
plt.suptitle("Scatterplots of 'mean' variables vs diagnosis")
plt.show()
# se
fig, axes = plt.subplots(2, 5, figsize=(25,15))
for i, ax in zip(cleanDFse, axes.flat):
    sns.scatterplot(x=data['diagnosis'], y=data[i], ax=ax)
plt.suptitle("Scatterplots of 'se' variables vs diagnosis")
plt.show()
# worst
fig, axes = plt.subplots(2, 5, figsize=(25,15))
for i, ax in zip(cleanDFworst, axes.flat):
    sns.scatterplot(x=data['diagnosis'], y=data[i], ax=ax)
plt.suptitle("Scatterplots of 'worst' variables vs diagnosis")
plt.show()

"""**Scatterplots**

Here we see the features and their measurements for benign and malignant tumours. If we look at the radius, we see the malignant tumours, which are classified as 1 and the benign tumours are classified as 0. Generally the radius of malignant tumours are larger than the benign tumours. We see this trend for most of the measurements of features in the mean subgroup, except for fractal dimension. There are also similar observations in the standard error 'se' and 'worst' subgroups.
"""

#@title
# boxplot
features = ['radius_mean', 'texture_mean', 'perimeter_mean',
       'area_mean', 'smoothness_mean', 'compactness_mean', 'concavity_mean',
       'concave points_mean', 'symmetry_mean', 'fractal_dimension_mean',
       'radius_se', 'texture_se', 'perimeter_se', 'area_se', 'smoothness_se',
       'compactness_se', 'concavity_se', 'concave points_se', 'symmetry_se',
       'fractal_dimension_se', 'radius_worst', 'texture_worst',
       'perimeter_worst', 'area_worst', 'smoothness_worst',
       'compactness_worst', 'concavity_worst', 'concave points_worst',
       'symmetry_worst', 'fractal_dimension_worst']

#Boxplot
# y includes our labels and x includes our features
y = data.diagnosis
x = data.drop('diagnosis',axis = 1)

# Some variables have very different ranges, for example perimeter_mean and compactness_mean. Therefore we need standirdization or normalization before visualization
data_dia = y
data1 = x
data_n_2 = (data1 - data1.mean()) / (data1.std())      

# boxplot
data1 = pd.concat([y,data_n_2.iloc[:,0:30]],axis=1)
data1 = pd.melt(data1,id_vars="diagnosis",
                    var_name="features",
                    value_name='value')
plt.figure(figsize=(20,20))
sns.boxplot(x="features", y="value", hue="diagnosis", data=data1)
plt.xticks(rotation=90)

"""**Boxplots**

The boxplots show the median, IQR, range, and outliers for each variable grouped by diagnosis (M = malignant, B = benign). Before plotting the values are normalised to ensure that variables with large value do not skew the rest of the chart. After normalisation we see that some variables are skewed (radius_mean 'M', concavity_mean 'B', perimeter_worst 'M', etc.). As well we see that many of the variables have outliers, as visualised with the dots outside of the boxplots upper/lower fences. Visualisation of the data through the boxplot informes us that the data will need to be transformed to ensure there is more normality before we can use it for further analytics/ modelling.
"""

#@title
#create data subsets

cleanDFmeanPairplot = data[[
      'diagnosis',
      'radius_mean',
      'texture_mean',
      'perimeter_mean',
      'area_mean',
      'smoothness_mean',
      'compactness_mean',
      'concavity_mean',
      'concave points_mean',
      'symmetry_mean',
      'fractal_dimension_mean'
      ]]
cleanDFsePairplot = data[[
      'diagnosis',
      'radius_se',
      'texture_se',
      'perimeter_se',
      'area_se',
      'smoothness_se',
      'compactness_se',
      'concavity_se',
      'concave points_se',
      'symmetry_se',
      'fractal_dimension_se'
      ]]
cleanDFworstPairplot = data[[
    'diagnosis',
    'radius_worst',
    'texture_worst',
    'perimeter_worst',
    'area_worst',
    'smoothness_worst',
    'compactness_worst',
    'concavity_worst',
    'concave points_worst',
    'symmetry_worst',
    'fractal_dimension_worst'
    ]]

#pairplot for 'mean' subset
sns.pairplot(cleanDFmeanPairplot, hue='diagnosis', corner=True)
plt.show()
#pairplot for 'se' subset
sns.pairplot(cleanDFsePairplot, hue='diagnosis', corner=True)
plt.show()
#pairplot for 'worst' subset
sns.pairplot(cleanDFworstPairplot, hue='diagnosis', corner=True)
plt.show()

"""**Pairplots**

We wanted to conduct bivariate analyses through scatterplots and by doing this through pairplots we are able to see the general relationship for all the numeric variables in our dataset. The relationships between numeric variables are shown, with the marginal distribution along the diagonal as well.

We immediately see that the radius, area, and perimeter variables have obvious linear relationships from the distinctly linear plots. Looking at the scatterplot for radius and perimeter, we see a strong, positive relationship. As the radius of a tumour increases, so does the perimeter of the tumour. Similarly, as the perimeter of a tumour increases, so does the area. The slope of the scatterplot for these variables, such as between radius and perimeter appears to indicate that they are highly correlated. The third variable, the diagnosis, which is shown by the very obvious colour grouping, (orange for benign, blue for malignant) actually makes this a multivariate analysis. Going back to radius and perimeter, we see that there is a clear division between the malignant and benign tumours.

Looking at radius mean and texture mean, we see a less obvious relationship when compared to the previous examples. As radius increases, the texture goes up slightly, but the points are a bit sparse on the right side. The radius mean and texture mean variables have a more moderate relationship, but still a positive one. Now if we consider the diagnosis again we actually see that the clusters of points are grouped fairly distinctly. We may consider that these two features are good variables to consider for our prediction model for classifying tumours, but we'll likely need more reliable information, such as in the form of a coefficient, to be more precise.

If we take a look at the smoothness of a tumour in relation to the texture of a tumour, we see that the points take on a round shape and have no clear direction. Similarly, the scatterplot for symmetry and texture shows points that take on a round shape and have no clear direction. It's likely these variables have no correlation with one another.

This subset of data is for the 'mean' data group, there are similar observations in the other two subsets of data. For example, we see fairly strong correlations between radius, area, and perimeter in the 'se' pairplots, and again in the 'worst' pairplots.

The pairplots here provide excellent insight into some of the linear relationships within the data.It gives us information about what features we might want to consider for feature selection or dimensionality reduction. In addition, there appears to be some multicollinearity, meaning that one independent variable can be predicted from another independent variable in a regression model. We would not be able to see the individual effects on the dependent variable if we use both the highly correlated variables as they are.
"""

#@title
# # Make a correlation matrix and plot it on a heatmap
corrMatrix = data.corr()
# print(corrMatrix)
# sns.heatmap(corrMatrix, annot=True)
# plt.show()

#mask redundant squares
mask = np.triu(np.ones_like(corrMatrix, dtype=bool))
#adjust dataframe and mask
mask = mask[1:, :-1]
corrDF = corrMatrix.iloc[1:,:-1].copy()

fig, ax = plt.subplots(figsize=(20,20))

#colour for heatmap
cmap = sns.diverging_palette(220,20,as_cmap=True)
#heatmap
sns.heatmap(
    corrDF,
    mask=mask,
    annot=True,
    fmt=".2f",
    linewidths=5,
    cmap=cmap,
    vmin=-1,
    vmax=1,
    cbar_kws={"shrink": .8},
    square=True
    )
#ticks
xticks = [i for i in corrDF.index]
yticks = [i for i in corrDF.columns]

#title
title = "Correlation Matrix\nWisconsin Breast Cancer Dataset\n"
plt.title(title, loc='left', fontsize=18)

plt.show()

"""**Correlation Heatmap**

The correlation heatmap shows the correlation value between features. If correlation is equal 1, means that the features are higly correlated and therefore, it is better to drop one of them to not inflate the analysis. For example, radius_mean, perimeter_mean and area_mean are correlated with each other. The question is, which variable we should drop, and what it is going to be the threshold?

**Challenges**

Outliers: With box plots seen from the EDA, we can see a lot of outliers which means that there are some variables that are skewed. This means that the variance in the data would be very high with data that is very sparse and spread out. We must consider this as it will affect our machine learning algorithms by introducing noise to the model and decrease accuracy.

Data Transformation: In the EDA we can see that the range of some features like the area mean is really large dealing in the 1000s. Meanwhile, other features are in a narrow range from 1s to 10s. This may imply a high variance if left unaddressed as it needs to be scaled or it will affect our model by giving it unnecessary noise. 

Zero Values in Data Set: Some rows of benign data rows contain missing values or 0 values. We must investigate these before proceeding to see if they were actually 0 values. It is also important to note that other values in the columns of ones containing 0 values have low values closer to 0.

Dimensionality Reduction: As we have too many features with high variance, it’s difficult for the model to converge. It will be good to reduce the dimensionality of our model, as removing multicollinearity improves machine learning model accuracy.

Imbalanced Data - There are more benign cases than Malignant cases. This may cause some bias in results.

**Data Preparation**

Outliers are dealt with using StandardScaler standardization. From each data point, the mean is subtracted and divided by the standard deviation, causing the mean to be 0 and the standard deviation to be unit/1. On the other hand, this transforms the range of the data points to about [-3, 3], reducing noise and improving performance of machine learning algorithms.
 
After researching from the source and improving on business understanding, the zeros are deemed as real values. Therefore, zero values are kept in the dataset.
 
PCA were selected as the means to reduce the number of features without feature selection. For PCA, the highly correlated variables would load out on the same principal component (PC1), thus removing highly correlated variables prior to doing PCA is redundant. 
The given data reflects on real world statistics. 

In order to keep it authentic, no manipulation was done to balance the dataset. However, since imbalanced data can cause bias during machine learning, evaluation metrics such as precision, recall, and AUC were looked at to evaluate the model performance instead of accuracy, which is more subjective to bias. Confusion matrix was also generated to check the number of misclassifications made by each model.

**Why use precision, recall, and AUC instead of accuracy?**

Due to our imbalanced dataset, we use precision to score our correctness in identifying patients being positive (malignant tumour) and them actually being positive. Precision is the ratio between the true positives and all positives (true positive + false positive). Although it is important that we do not subject a patient without a malignant tumour to treatment, it may at the very least raise a flag for a second opinion.

Recall measures a model’s correctness for identifying true positives. This is very important in our context because a false positive means that a patient that requires treatment will not receive it. False negatives and recall are the most important measures if we are prediction between a benign and malignant class.

Area under curve (AUC) is the area under the Receiver Operating Characteristic (ROC) curve. Due to our imbalanced class distribution, we do not want our model to overfit to a particular class. For our ROC curve, we want to have a high true positive rate and low false positive rate threshold because we do not want to predict a malignant tumour as benign. The AUC is scored between 0 and 1, which is a value we wish to maximize so, again, we can have the highest true positive rate and lowest false positive rate for some threshold. A higher AUC score indicates better performance of a model at separating classes.
"""

#@title
# Feature standardization 
predictors, response = make_predictors_response(data, 'diagnosis')
colnames = predictors.columns

# Apply scalar transformation to predictors
scaler = preprocessing.StandardScaler().fit(predictors)
scaler = pd.DataFrame(scaler.transform(predictors))
scaler.columns = colnames

# Plot PCA results using PCA plot
pca_variance_arr = draw_pca_plot(scaler)

final_df = pd.concat([scaler.reset_index(drop=True), response], axis=1)
print(final_df.head())
final_df.to_csv(path_or_buf="processed_data.csv", sep=",", index=False)

"""**Above**

Plot of Variance Explained by Different Principal Components. Data was standadized before performing the PCA. The first ten principal components account for 95% of the total variation in our dataset. If we consider the first two principal components, that actually contain most the variation, it will accumulate about 65% of the total variation. It means that we do not need to work with a high dimensional data, and can use the first two principal components on our model training. 

**Below**

Basic information after the standardization
"""

#@title
# Set pandas output to max rows and columns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Load pre-processed data from main file
data = load_dataset("processed_data.csv")
data['diagnosis'] = data.diagnosis.map(dict(M=1, B=0))
# # Print all the column names and remove Id and index variable
# data = data.drop("id", axis=1)
#
# # Standardization of featured data
# scaler = StandardScaler()
predictors, response = make_predictors_response(data, 'diagnosis')

# colnames = predictors.columns
# predictors = pd.DataFrame(scaler.fit_transform(predictors))

# Basic information after the standardization
pca_predictors = pd.DataFrame(run_pca(predictors, 2)) #2 principal components
print(pca_predictors.info())
print(pca_predictors.head())
print(pca_predictors.shape)

"""**Classification models used below**: logistic regression, random forest, naive bayes, decision tree. Last model is voting ensemble."""

#@title
# Train Test split of dataset for model evaluation
X_train, X_test, y_train, y_test = train_test_split(pca_predictors, response, test_size=0.2, random_state=42) #split 80/20

# y_train = y_train.astype(bool)
# y_test = y_test.astype(bool)

# Make classification models

# logistic regression and prediction
print("==========================================================================")
print("Running Logistic Regression")
lr_clf = run_logistic_regression(X_train, y_train)
print(make_predictions(lr_clf, X_test, y_test))
# logistic regression ROC
lr_clf.fit(X_train, y_train)
metrics.plot_roc_curve(lr_clf, X_test, y_test) 
plt.title("Logistic Regression ROC Curve") 
plt.show()

# Random Forest and prediction
print("==========================================================================")
print("Running Random Forest")
rf_clf = run_random_forest(X_train, y_train)
print(make_predictions(rf_clf, X_test, y_test))
# Random Forest ROC
rf_clf.fit(X_train, y_train)
metrics.plot_roc_curve(rf_clf, X_test, y_test)
plt.title("Random Forest ROC Curve") 
plt.show()  

# Naive Bayes algorithm implementation and prediction
print("==========================================================================")
print("Running Naive Bayes")
nb_clf = run_naive_bayes(X_train, y_train)
print(make_predictions(nb_clf, X_test, y_test))
# Naive Bayes ROC
nb_clf.fit(X_train, y_train)
metrics.plot_roc_curve(nb_clf, X_test, y_test)  
plt.title("Naive Bayes ROC Curve") 
plt.show()  

# Decision tree model
print("==========================================================================")
print("Running Decision Tree")
dt_clf = run_decision_tree(X_train, y_train)
print(make_predictions(dt_clf, X_test, y_test))
# Decision Tree ROC
dt_clf.fit(X_train, y_train)
metrics.plot_roc_curve(dt_clf, X_test, y_test) 
plt.title("Decision Tree ROC Curve")  
plt.show()  

# Voting Ensemble models with logistic, random forest, naive bayes, and decision tree
print("==========================================================================")
print("Running Voting Ensemble")
ensemble_clf = run_voting_ensemble(lr_clf, rf_clf, nb_clf, dt_clf, X_train, y_train)
print(make_predictions(ensemble_clf, X_test, y_test))
# Ensemble ROC
ensemble_clf.fit(X_train, y_train)
metrics.plot_roc_curve(ensemble_clf, X_test, y_test)  
plt.title("Ensemble ROC Curve") 
plt.show()
# #votingEnsembleSoft
# img = mpimg.imread('voteEnsembleSoftExample.png') # only for presentation use
# plt.imshow(img)
# plt.show()

"""Before modeling, the data was splited into training and testing subsets. 80% of data was used as training set and 20% data was used as a testing set.

**Model 1: Logistic Regression**

Binary logictic regression is perfect to use when dealing with a binary reponse variable. Maligant is set to 1 and Benign is set to 0 before any analysis are carried out.

Comparing predicted values with ground true values of the testing set. response test values represnes ground truth. model prediction represents predicted values. The majority of them match, only one data point (in the middle of the first row) that is supossed to be malignant, the model predicts falsely as benign.

By comparing the predicted values with the actual values of the tesing set. A confusion matrix was generated. There is no false positive and 1 false negative in the model as the classifier missclassfies 1 malignant as benign.
In the classification report, the average precision and recall both equal to 0.99 where precision measures the misclassifications and recall(true positive rate) measures the ability of capturing true positivevlass. These values are the same for weighted average of precision and recall.  
AUC score calculates the area under ROC curve. The AUC here is very high(close to 1), indicating that logistic regression model almost perfectly classify benign and malignant classes. 

This can be visulized in ROC curve which shows the trade-off between sensitivity and specificity. The curve is very close to the top left corner indicating that predictive performance of the classifier is excellent.

**Model 2: Random Forest**

Random forest is a collection of decision trees, vote for the majority.
In the Confusion matrix, there is no false positive but there are 2 false negative. 

From the classification report, the average precision and recall are 0.99 and 0.98 respectively, after adjusting for the weights, the avarage prcision and recall are 0.98, which is 0.1 lower than the scores of logistic regression because there is additional false negative in this model.

AUC is also slightly lower than AUC of logistic regression, thereby, logistic regression may be a better classifier than random forest.


In ROC curve, the best performance of the model shifts rightward and the false positive rate(represented by the x-axis) increases compared to logistic regression, indicating a reduction in specificity.

**Model 3: Naive Bayes**

Naive Bayes is a classifier based on probablity.
One of its assumption is that there is no correlation bewteen predictors, in other words, predictors are independent of each other. In the previous steps, to reduce the dimension of our dataset, we performed PCA which converts a set of correlated variables into linearly uncorrelated variables. Therefore, the independence assumption for Naive Bayes can be satisfied.

In the confusion matrix, we observed 1 false positive and 5 false negative, so there are more misclassifications of both maglinant and benign classes compared to the two previous models. 
The precisions and recalls are also lower than the 2 previous models and this is also true after adjusting for the weights. 

AUC score is very close to 1 and from ROC curve, we observed that the specificity is higher than Random forest model.

**Model 4: Decision Tree**

Here we see our decision tree classifier, which is outperformed by our 
random forest classifier, but we decided to use it to see how it would perform.

Looking at the confusion matrix, we see that there are 3 false negatives, which is actually one more than the 2 found in our random forest model. We would consider this fairly significant in the context of our objective.

The precision for the malignant class is 0.98 vs 1 in random forest, 0.96 vs 0.97 for benign precision, 0.99 vs 1 for benign recall, and 0.93 vs 0.95 for malignant recall. All of these scores are outperformed by the random forest model.

The AUC score is approximately 0.958 vs 0.994, and again the random forest does indeed outperform our decision tree classifier.

Typically, we would prefer random forest over decision tree to reduce the variance and for better predictions, but might want to use a decision tree as a simple model or in situations where we have limited computational power with larger datasets.

**Model 5: Voting Ensemble**

Our fifth model is a voting classifier, a model of models, which encompasses the logistic regression, random forest, naïve bayes, and decision tree models we discussed.

This is a soft voting ensemble, which predicts the class using the average of probability given to that class. We have 4 classifiers from which the model uses the average probability to predict the output. 

From the confusion matrix we see that there are only two false negatives, which is not bad, but is actually one more false negative than our logistic regression model. 
We have a good precision and recall scores and the second highest AUC score after logistic regression, which was marginally better
Although we used the "power" of each algorithm to classify the same thing and average it out, some models don't capture the variance as well, so the entire power of the voting ensemble is decreased. This is the reason why our logistic regression model outperforms this voting ensemble

To improve our voting ensemble we could consider using a larger dataset, if available, to ensure that the model is well trained. Additionally, using more models could help to correct mistakes from other models.
"""

#@title
# define X, y by predictors and response variables
X = pca_predictors
y = response

kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
kf.get_n_splits(X, y)

# perform Stratified K-Folds cross-validation on Logistic model
for train_index, test_index in kf.split(X, y):
    score = cross_val_score(LogisticRegression(random_state=42), X, y, cv=kf, scoring="accuracy")
print(f'Scores for each fold are: {score}')
print(f'Average score: {"{:.2f}".format(score.mean())}')
print(f'Standard deviation: {"{:.2f}".format(score.std())}')

# (changed scoring value to 'balanced_accuracy'): 'balanced_accuracy' deals with imbalanced dataset, but I am not sure if it's necessary to use it after Stratified K Folds
print('-----------------------------------------------------------------------------------')
for train_index, test_index in kf.split(X, y):
    score = cross_val_score(LogisticRegression(random_state=42), X, y, cv=kf, scoring="balanced_accuracy")
print(f'Scores for each fold are: {score}')
print(f'Average balanced accuracy: {"{:.2f}".format(score.mean())}')
print(f'Standard deviation: {"{:.2f}".format(score.std())}')

"""**Stratified K-Fold Cross Validation above:**

After modelling, we used k-fold cross validation to confirm that good evaluation scores produced are not due to randomness. Specifically, Stratified k-fold cross validation is used to preserve the imbalanced class distribution in each fold and to ensure that there are enough examples in the training and testing sets to evaluate the model. Use parameter “scoring = balanced accuracy” to account for the imbalanced dataset. 
"""

#@title
# k fold cross validation ROC - logistic regression
tprs = []
aucs = []
mean_fpr = np.linspace(0, 1, 100)

fig, ax = plt.subplots()
for i, (train, test) in enumerate(kf.split(X, y)):
    lr_clf.fit(X.iloc[train], y.iloc[train])
    viz = metrics.plot_roc_curve(lr_clf, X.iloc[test], y.iloc[test],
                         name='ROC fold {}'.format(i),
                         alpha=0.3, lw=1, ax=ax)
    interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
    interp_tpr[0] = 0.0
    tprs.append(interp_tpr)
    aucs.append(viz.roc_auc)

ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
        label='Chance', alpha=.8)

mean_tpr = np.mean(tprs, axis=0)
mean_tpr[-1] = 1.0
mean_auc = metrics.auc(mean_fpr, mean_tpr)
std_auc = np.std(aucs)
ax.plot(mean_fpr, mean_tpr, color='b',
        label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
        lw=2, alpha=.8)

std_tpr = np.std(tprs, axis=0)
tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                label=r'$\pm$ 1 std. dev.')

ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05],
       title="Receiver operating characteristic example")
ax.legend(loc="lower right")
plt.show()

"""**Above**

Another ROC was performed on each trainning and testing subset generated by k-fold cross validation in orther to visulize the overall performance and performance of each fold. As observed from the figure, the ROC fold 0 and ROC fold 4 yield the maximum performances. Also, the mean ROC curve is smoother than ROC curve for each fold.

**Considerations for Further Reduction of False Negatives**

In order to effectively diagnosis malignant tumours and further reduce the incidence of false negatives we considered several methods which we did not ultimately use due to our high performing models:

1) Lower the threshold for our logistic regression algorithm (e.g., 0.25 vs 0.5).

2) Use probabilistic classifications instead of hard 0-1 classifications. That is, predict the probability for an instance to be positive. Use proper scoring rules to assess these predicted probabilities.

3) Modify class weight in logistic regression. For example, in our logistic regression model, using class_weight = {0:1, 1:4} results in 0 false negatives, but an increase in false positives. However, considering the consequences of diagnosing a malignant tumour as a benign one, we think it may be feasible to adjust our logistic regression classifier in this manner.

**Conclusion**

Once evaluation of the 5 models are complete it is necessary to compare how well they perform and decide which is the preferred model. Due to the goal of the model in our project is for application in clinical diagnosis of disease, it is important that the performance and specificity is high. That is the model must be accurate, and minimize the risk of false negatives as much as possible. The two highest performing models were found to be the logistic regression model and the ensemble model. Both had an AUC score of 0.998 signifying strong classifying performance. Both also had a specificity of 1.0, which was calculated from their confusion matrix. However, the logistic model only created one false negative, while the ensemble model creates two false negatives. In practicality both models work very well, however for the sake of picking just one the logistic model is chosen as the best performing, and ultimately the preferred model to classify breast cancer tumors as either benign or malignant.

**Future Steps**

After completion of this project we find that there are improvements that can be made and areas we can expand upon. One improvement would be to gather more data and increase our database. Given that the initial data set is only about 500 entries in length, our resulting models could be overfitted. Having a larger database would allow us to test the validity further and ensure that this is not the case. Another room for improvement would be to alter our methodology to enable the classification output to be justified using features found in the original data set. This is an issue due to the use of PCA, which combines the features into unrecognizable components. To do this we could utilise cluster analysis to group the classifying outputs (malignant or benign) then look at the commonalities within the group. This will help us discover the features that the PCA utilises during classification. This change is important if the model were to be implemented clinically because it allows for the models methodology to be transparent to the practitioner and allow them to use its classification results responsibly.
"""
