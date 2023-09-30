# -*- coding: utf-8 -*-
"""MLfakenews_(Combined_Version).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PuTVacchFOhBfYoRdheFseW0Fd_1HNPK

# IMPORTS

First, let's **import** the **models** and the **functions** that we will use.
"""

# Libraries to manage datasets
import pandas as pd
import numpy as np

# Libraries to process natural language
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer

# Libraries to plot graphics and scores
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report, accuracy_score

# Classifiers
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense

# Libraries useful to feature representations
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, CountVectorizer

# Libraries useful to classification process
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

nltk.download('wordnet') #WordNet Lemmatizer
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt') #tokenizer to divide a text into a list of sentences
nltk.download('stopwords') #download english stopwords from nltk

stopwords_list = set(stopwords.words('english')) # saves the stopwords vocabulary as a python set

from google.colab import drive
drive.mount('/content/drive')

"""Previously we had **downloaded**  the **datasets** (with a registered account, at this link https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset), then, for the sake of simplicity, we stored them into our Google Drive folder.


> Using **pandas**, we can read these two datasets.


"""

ds_true = pd.read_csv("/content/drive/MyDrive/MLfakenews/True.csv")
ds_fake = pd.read_csv("/content/drive/MyDrive/MLfakenews/Fake.csv")

"""Since we could have already saved our composed **dataset** with text preprocess already applied, we check if it is **already existing**, otherwise proceed to create it"""

# if we have saved the preprocessed dataset we can import it to save time with preprocessing phase
create_db_news = False
try:
  ds_news = pd.read_csv("/content/drive/MyDrive/MLfakenews/News.csv")
  print("Preprocessed dataset charged!")
except:
  print("Preprocessed dataset not charged. Creating it...")
  create_db_news = True

"""# LOAD DATASET

Previously we had **downloaded**  the **datasets** (with a registered account, at this link https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset), then, for the sake of simplicity, we stored them into our Google Drive folder.


> Using **pandas**, we can read these two datasets.
"""

ds_true = pd.read_csv("/content/drive/MyDrive/MLfakenews/True.csv")
ds_fake = pd.read_csv("/content/drive/MyDrive/MLfakenews/Fake.csv")

"""Since we could have already saved our composed **dataset** with text preprocess already applied, we check if it is **already existing**, otherwise proceed to create it."""

# if we have saved the preprocessed dataset we can import it to save time with preprocessing phase
create_db_news = False
try:
  ds_news = pd.read_csv("/content/drive/MyDrive/MLfakenews/News.csv")
  print("Preprocessed dataset charged!")
except:
  print("Preprocessed dataset not charged. Creating it...")
  create_db_news = True

"""# PREPROCESSING - CREATE OR RESTORE THE PREPROCESSED DATASET"""

#adds a label feature in the two datasets
ds_true['label'] = 0 #0 = true news
ds_fake['label'] = 1 #1 = fake news

ds_true.head()

ds_fake.head()

"""This will be the **preprocessing_text** function."""

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

def preprocessing_text(text): # function that performs the preprocessing step
  text2 = text.casefold() # converts to lower case
  text3 = re.sub(r"[^A-Za-z0-9\s]", " ", text2) # substitutes symbols into blank spaces
  filtered_text = [
        stemmer.stem(lemmatizer.lemmatize(word)) # does stemming and lemmatizing
        for word in word_tokenize(text3)
        if (word not in stopwords_list and len(word) > 3) # excludes words inside the stopwords list and words shorter than three characters
    ]
  return filtered_text

"""If we have to create the complete dataset from scratch, concatenate the two datasets, then create the column containing the cleaned text. Now we can save the created dataset, to save up the time of preprocessing in the next execution.


Instead, if we can load the dataset, we simply have to restore the dropped columns during the saved process.
> At the end of the process, **ds_news['filtered']** will contain the result of **preprocessing** applied on the **articles' content**
"""

if create_db_news:  # need to preprocess the data
    # merge the 2 datasets
    ds_news = pd.concat([ds_true, ds_fake]).reset_index(drop = True)

    # removes the 'date' feature because it doesn't give us any useful information
    ds_news.drop(columns = ['date'], inplace = True)

    # adds a feature made up by merging 'title' and 'text' features
    ds_news['title_text'] = ds_news['title'] + ' ' + ds_news['text']

    # applies for each row of the dataset the preprocessing_text function
    ds_news['filtered'] = ds_news['title_text'].apply(preprocessing_text)

    # converts the list of words into a single string
    ds_news['filtered_string'] = ds_news['filtered'].apply(lambda x: " ".join(x))

    # adds feature that is a list of every unique words for each row of the dataset
    ds_news['filtered_unique'] = ds_news['filtered'].apply(lambda x: list(set(x)))

    # export the dataset with applied preprocess, since we haven't already saved before,  to save time with the next preprocessing phase execution
    # Please note that we have to use drop since arrays are saved as string in csv format
    ds_news.drop(columns = ['filtered','filtered_unique'], inplace = True)
    ds_news.to_csv("/content/drive/MyDrive/MLfakenews/News.csv")

# Whether we already have the dataset with preprocessed applied or it has been created now,
# we have to restore the filtered and filtered_string series, because of the drop during saving

ds_news['filtered'] = ds_news['filtered_string'].apply(lambda x: word_tokenize(x))

ds_news['filtered_unique'] = ds_news['filtered'].apply(lambda x: list(set(x)))

"""# ADDITIONAL PREPROCESSING INFORMATION

Here we retrieve useful **information** about the preprocessing, such as the **total words** that compose our features and the **Max** and **Min** number of **words/unique words** in any document
"""

ds_news.head()

"""## MIN MAX WORDS"""

# Obtains the total number of unique words (in the whole dataset)
wordlist = []
for i in ds_news.filtered:
    for j in i:
        wordlist.append(j)

total_words = len(list(set(wordlist)))
print("Total unique words =",total_words)

#gets the max and min number of words in any document
maxlen = -1
i=0
for doc in ds_news.filtered:
    if(maxlen<len(doc)):
        maxlen = len(doc)
        imax=i
    i+=1

minlen = maxlen
i=0
for doc in ds_news.filtered:
    if(minlen>len(doc)):
        minlen = len(doc)
        imin=i
    i+=1

print(f"Max number of words in any document = {maxlen} (index={imax})")
print(f"Min number of words in any document = {minlen} (index={imin})")

#gets the max and min unique number of words i any document
maxdim = -1
i=0
for doc in ds_news.filtered_unique:
    unique_length = len(doc)
    if(maxdim<unique_length):
      maxdim = unique_length
      imaxu=i
    i+=1

mindim = maxdim
i=0
for doc in ds_news.filtered_unique:
    unique_length = len(doc)
    if(mindim>unique_length):
      mindim = unique_length
      iminu=i
    i+=1

print(f"Max number of words in any document = {maxdim} (index={imaxu})")
print(f"Min number of words in any document = {mindim} (index={iminu})")

"""# DIAGRAMS AND GRAPHS

In this section we provide different **insigths** about our dataset.
"""

ds_true.head() # shows True.csv

ds_fake.head() # shows Fake.csv

ds_news.head() # show the entire dataset

"""First of all, we could check if the data is **balanced**:

> And that is, since the number of **true** and **fake** news it's quite the **same**.


Then we can show the data calculated in "ADDITIONAL PREPROCESSING INFORMATION" section.
"""

# showing some information
print('true n_rows =', len(ds_true))
print('fake n_rows =', len(ds_fake))
print('total n_rows =', len(ds_news))
print("the number of total unique words in the dataset is =",total_words)
print("The biggest document is =", maxlen, "words (index=",imax,")")
print("The smallest document is =", minlen, "words (index=",imin,")")
print(f"the largest unique entry is {maxdim} (index={imaxu})")
print(f"the smallest unique entry is {mindim} (index={iminu})")

# count-plot of True.csv subjects
plt.figure(figsize = (8, 8))
plt.title("subject count true")
sns.countplot(y = "subject", data = ds_true)
plt.show()

# count-plot of Fake.csv subjects
plt.figure(figsize = (8, 8))
plt.title("subject count fake")
sns.countplot(y = "subject", data = ds_fake)
plt.show()

# count-plot of the entire dataset subjects
plt.figure(figsize = (8, 8))
plt.title("subject count total")
sns.countplot(y = "subject", data = ds_news)
plt.show()

# count-plot of label values
plt.figure(figsize = (8, 8))
plt.title("label count")
sns.countplot(y = "label", data = ds_news)
plt.show()

# showing a word-cloud graph of the fake news
plt.figure(figsize = (10,10))
plt.title("Fake news")
wc = WordCloud(max_words = 300 , width = 1600 , height = 800).generate(" ".join(ds_news[ds_news.label == 1].filtered_string))
plt.imshow(wc, interpolation = 'bilinear')
plt.show()

# showing a word-cloud graph of the true news
plt.figure(figsize = (10,10))
plt.title("Real news")
wc = WordCloud(max_words = 300 , width = 1600 , height = 800).generate(" ".join(ds_news[ds_news.label == 0].filtered_string))
plt.imshow(wc, interpolation = 'bilinear')
plt.show()

"""# DEFINE POSSIBLE DATA REPRESENTATIONS"""

num_words = 500 # vocabulary length
pad_length = 100 # padding length

#TOKENIZER
def to_tokens(train, test):
  tokenizer = Tokenizer(num_words=num_words) # consider only the first num_words more frequent
  tokenizer.fit_on_texts(train)

  train_sequences_t = tokenizer.texts_to_sequences(train)
  test_sequences_t = tokenizer.texts_to_sequences(test)

  #Adds the padding
  padded_train_t = pad_sequences(train_sequences_t,maxlen = pad_length, padding = 'post', truncating = 'post') #post means add 0s at the end, truncating means that truncate after the maxlen number of elements specified
  padded_test_t = pad_sequences(test_sequences_t,maxlen = pad_length, padding = 'post', truncating = 'post')

  print("First train element: \n", train.iloc[0])
  print("\n")
  print("First train element, without padding: \n", train_sequences_t[0])
  print("\n")
  print("First train element, with padding: \n",padded_train_t[0])

  return padded_train_t, padded_test_t

def to_vectorize(train, test):
  #VECTORIZER
  tvectorizer = tf.keras.layers.TextVectorization(
  max_tokens=num_words,
  output_mode='int')

  tvectorizer.adapt(train)

  train_sequences_v = tvectorizer(train).numpy()
  test_sequences_v = tvectorizer(test).numpy()

  #Adds the padding
  padded_train_v = pad_sequences(train_sequences_v,maxlen = pad_length, padding = 'post', truncating = 'post')
  padded_test_v = pad_sequences(test_sequences_v,maxlen = pad_length, padding = 'post', truncating = 'post')

  print("First train element: \n", train.iloc[0])
  print("\n")
  print("First train element, before padding: \n", train_sequences_v[0])
  print("\n")
  print("First train element, after padding: \n", padded_train_v[0])

  return padded_train_v, padded_test_v

def to_tfidf_vect(train, test):
  #converts to list because CountVectorizer and TFIDFVectorizer works on pure list

  x_train_c = train.tolist()
  x_test_c = test.tolist()
  #TFIDF-VECTORIZER
  tfvectorizer = TfidfVectorizer(max_features=num_words)

  # Fit the vectorizer on the training data
  tfvectorizer.fit(x_train_c)

  # Transform the training and testing data
  tf_train = tfvectorizer.transform(x_train_c).toarray()
  tf_test = tfvectorizer.transform(x_test_c).toarray()

  print("First train element: \n", x_train_c[0])
  print()
  print("First train element, with tfidf: \n", tf_train[0][:100]) # Truncated to 100 numbers, because it generates long output
  print()

  return tf_train, tf_test

"""Build the lists of all possible data representation formats and names."""

data_representation = [to_tokens, to_vectorize, to_tfidf_vect]
data_representation_name = ['tokenizer','vectorizer','tfidf']

"""# TRAINING AND TESTING CLASSIFIERS

First, let's **import** the **Models** and the **Functions** that we will use
"""

# Classifiers
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from tensorflow.keras.models import Sequential, Model


# Useful functions
from sklearn.model_selection import GridSearchCV, ShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

"""Define all **classifiers**, constructing then a **list** containing all of them."""

########## Stochastic Gradient Descent ##########
sgd = make_pipeline(StandardScaler(),SGDClassifier(loss='hinge', penalty="l2", alpha=1e-3,
                             random_state=42, max_iter=2000, tol=1e-4))

########## Random forest ##########
rf =  RandomForestClassifier(n_estimators=20, max_depth=10, random_state=42)


########## BIDIRECTIONAL-LSTM ##########
blstm_model = Sequential()
# Embedding layer
blstm_model.add(Embedding(num_words, output_dim=8))
blstm_model.add(Bidirectional(LSTM(8)))

# Dense layers
blstm_model.add(Dense(4, activation = 'relu'))
blstm_model.add(Dense(1,activation= 'sigmoid'))
blstm_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
blstm_model.summary()

########## LOGISTIC REGRESSION ##########
lrmodel = LogisticRegression()

# Building list of classifiers
classifiers = [ sgd,  rf, blstm_model, lrmodel]
classifiers_names = ["SGD", "RF", "Bidirectional LSTM", "Logistic Regression"]

"""Now we can retrive either the features and the labels, then do **k-folding**."""

# Retrieve all targets and labels
x = ds_news.filtered_string
y = ds_news.label
# Define number of splits and random seed
n_splits = 10
seed = 42

# split the data
splitter = KFold(n_splits=n_splits, random_state=seed, shuffle=True)

"""Before starting with training and testing, we initialize useful variables and a function to **calculate** and **visualize** the **classification errors**."""

# Initialize variables to keep track of cumulative metrics
average_precision = np.zeros(shape=(len(classifiers), len(data_representation)))
average_recall = np.zeros(shape=(len(classifiers), len(data_representation)))
average_f1_score = np.zeros(shape=(len(classifiers), len(data_representation)))
# Dimension appropriate to store each classifier's averaged confusion matrix, for each data representation (2 classes* 2 possible predictions)
average_confusion_matrix = np.zeros(shape=(len(classifiers), len(data_representation),  2, 2))

"""## Now we are finally **ready**!

> **Training** and **classification** processes can start.


"""

for i, (train_index, test_index) in enumerate(splitter.split(x)):
    print(f"--------------------------- Split n.{str(i)} ---------------------------")

    # split labels of train and test
    y_test, y_train = y[test_index], y[train_index]

    for k, represent_data in enumerate(data_representation):
      print("Data representation: ", data_representation_name[k])
      x_train, x_test = represent_data(train=x[train_index], test=x[test_index])

      for j, clf in enumerate(classifiers):

        print(f"\n******************* {classifiers_names[j]} with {data_representation_name[k]} *******************")

        if classifiers_names[j] == ("Bidirectional LSTM"):
          # Train the classifier
          clf.fit(x_train, y_train, batch_size=256, validation_split=0.1, epochs=3)
          # Prediction on test data
          y_pred_prob = clf.predict(x_test)[:, 0]  # Get the probability of the positive class

          # Applying threshold for binary classification
          threshold = 0.98
          y_pred = (y_pred_prob > threshold).astype(int)


        else:  # other than LSTM classifiers
          # Train the classifier
          clf.fit(x_train, y_train)
          # Prediction on test data
          y_pred = clf.predict(x_test)
        # Retrieve the classification report
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        # Print the classification as a string, since the previous one was a dict useful for retrieve the values
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, output_dict=False))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        # Accumulate the confusion matrix for this classifier
        average_confusion_matrix[j][k] += confusion_matrix(y_test, y_pred)

        # Accumulate the precision, recall, and F1-score for this classifier
        average_precision[j][k] += report['macro avg']['precision']
        average_recall[j][k] += report['macro avg']['recall']
        average_f1_score[j][k] += report['macro avg']['f1-score']

for clf_index, clf in enumerate(classifiers):
    for data_rep_index, data_rep in enumerate(data_representation):
        average_precision[clf_index, data_rep_index] /= n_splits
        average_recall[clf_index, data_rep_index] /= n_splits
        average_f1_score[clf_index, data_rep_index] /= n_splits
        average_confusion_matrix[clf_index, data_rep_index] /= n_splits

"""Let's clearly see the results, in terms of classification report and confusion matrix of each classifier, in each split done."""

fig, axes = plt.subplots(len(data_representation), len(classifiers), figsize=(30, 15), sharey='row')

# Print the average metrics for each classifier and data representation
for clf_index, clf in enumerate(classifiers):
    for data_rep_index, data_rep in enumerate(data_representation):
        print(f"\n******* Average metrics for {classifiers_names[clf_index]} and data representation {data_representation_name[data_rep_index]} *******")
        print(f"Average Precision: {average_precision[clf_index, data_rep_index]:.2f}")
        print(f"Average Recall: {average_recall[clf_index, data_rep_index]:.2f}")
        print(f"Average F1-score: {average_f1_score[clf_index, data_rep_index]:.2f}")
        print("\nAverage Confusion Matrix:")
        print(average_confusion_matrix[clf_index, data_rep_index])

        # Fill the subplot of the confusion matrix
        cm = ConfusionMatrixDisplay(average_confusion_matrix[clf_index, data_rep_index], display_labels=['true news', 'fake news'])
        cm.plot(ax=axes[data_rep_index, clf_index], xticks_rotation=45, values_format='', cmap="Blues")

        cm.ax_.set_title(f"{classifiers_names[clf_index]} - {data_representation_name[data_rep_index]}")

# Fill the figure with the combined averaged confusion matrices
fig.text(0.43, 0.05, 'Predicted label', ha='left')
plt.subplots_adjust(wspace=0.5, hspace=0.5)


# Plot the metrics for each classifier and data representation
fig, axes_metrics = plt.subplots(nrows=len(data_representation), ncols=len(classifiers), figsize=(30, 15), sharey='row')

# Metrics labels
metrics_labels = ['Precision', 'Recall', 'F1-score']

for i, data_rep in enumerate(data_representation):
    for j, clf in enumerate(classifiers):
        # Get the averaged metrics for the specific data representation and classifier
        avg_precision = average_precision[j, i]
        avg_recall = average_recall[j, i]
        avg_f1_score = average_f1_score[j, i]

        # Create a subplot for the specific data representation and classifier
        ax = axes_metrics[i, j]

        # Plot the metrics
        ax.bar(['Precision', 'Recall', 'F1-score'], [avg_precision, avg_recall, avg_f1_score], color=['red', 'green', 'blue'])

        # Set the subplot title and limits
        ax.set_title(f'{classifiers_names[j]} - {data_representation_name[i]}')
        ax.set_ylim(0, 1)

        # Annotate bars with metric values
        for x, val in enumerate([avg_precision, avg_recall, avg_f1_score]):
            ax.annotate(f'{val:.2f}', (x, val), ha='center', va='bottom')

# Adjust the layout and show the plots
plt.tight_layout()
plt.show()