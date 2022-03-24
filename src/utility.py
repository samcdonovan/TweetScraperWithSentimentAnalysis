import pandas as pd
import re
from nltk.corpus import stopwords  # Import stopwords from nltk.corpus
import csv  # Import the csv module to work with csv files
import nltk
import sys
import unicodedata
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
wordnet.ensure_loaded()
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')


def get_stop_words():
    stop_list = []
    with open('data/stop_words.csv', 'r') as file:
        stop_list = file.read().strip().split(",")

    return stop_list


stop_words = get_stop_words()


def clean_and_lemmatize(text):
    wnl = WordNetLemmatizer()
    converted_tweet = convert_to_list(text)

    tagged = nltk.pos_tag(converted_tweet)
    wordnet_tagged = list(
        map(lambda x: (x[0], pos_tagger(x[1])), tagged))

    lemmatized_sentence = []
    for word, tag in wordnet_tagged:
        if tag is None:
            # if there is no available tag, append the token as is
            lemmatized_sentence.append(word.lower())
        else:
            # else use the tag to lemmatize the token
            lemmatized_sentence.append(wnl.lemmatize(word, tag).lower())

    cleaned_text = " ".join(lemmatized_sentence)
    return cleaned_text


def pos_tagger(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def create_csv():

    stop_words = stopwords.words('english')
    with open('data/stop_words.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(stop_words)


def convert_to_list(sentence):
    converted_list = []
    re.sub('[0-9]+', '', sentence)
    re.sub('((www.[^s]+)|(https?://[^s]+))',' ',sentence)

    for word in sentence.split():
        
        stop_check = bool(False)

        if word in stop_words:
            stop_check = True

        """
        for stop_word in stop_words:
            if word.lower() in stop_word:
                stop_check = bool(True)
        """
        if not stop_check and "http" not in word and "@" not in word:
            word = word.translate(dict.fromkeys(i for i in range(sys.maxunicode)
                                                if unicodedata.category(chr(i)).startswith('P')))
          
            converted_list.append(word)

    return converted_list


def tokenize(text):
    return text.split()


def get_training_data():
    df = pd.read_csv('./data/sentiment_140_dataset.csv', encoding='ISO-8859-1',
                     names=['target', 'ids', 'date', 'flag', 'user', 'text'])

    training_data = df[['text', 'target']]

    training_data['target'] = training_data['target'].replace(4, 2)
    training_data['target'] = training_data['target'].replace(0, -2)
    training_data['target'] = training_data['target'].replace(2, 1)

    training_positive = training_data[training_data['target'] == 2]
    training_negative = training_data[training_data['target'] == -2]
    training_neutral = training_data[training_data['target'] == 1]

    training_positive = training_positive.iloc[:int(3333)]
    training_negative = training_negative.iloc[:int(3333)]
    training_neutral = training_neutral.iloc[:int(3333)]

    training_set = pd.concat([training_neutral, training_negative, training_positive])

    for i in range(0, len(training_set)):
        training_set[i]['text'] = clean_and_lemmatize(training_set[i]['text'])