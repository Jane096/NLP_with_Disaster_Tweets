# -*- coding: utf-8 -*-
"""Model_sample_RandomForest의 사본

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NzWK6XVST2RuTxkQISOPLsDhBw0qqZWe
"""

# Commented out IPython magic to ensure Python compatibility.
import string
import nltk
import re
import xgboost as xgb
import seaborn as sns
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score,make_scorer
import matplotlib.pyplot as plt

#Baseline 모델 및 측정지표
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
# %matplotlib inline

#STOPWORDS = set(stopwords.words('english')) # 일반 스톱워드 목록
ps = PorterStemmer() # 유사단어 패턴기반 데이터 압축 기능 제공

# Bayes
from sklearn.naive_bayes import MultinomialNB

nltk.download('stopwords')

test = pd.read_csv('/content/drive/My Drive/Data/test.csv')
train = pd.read_csv('/content/drive/My Drive/Data/train.csv')

test.head()

from google.colab import drive
drive.mount('/content/drive')

train.head(3)

# 전처리 함수
sw = set(stopwords.words('english'))
def text_preprocessing(data):
  """
  data 는 dataframe 통째를 넣어주어야 함
  """
  corpus = []
  length = data.shape[0]
  for i in range(length):
    text = re.sub('[^a-zA-Z]',' ', data['text'][i])  # 알파벳이 아닌 글자(문법기호 포함)로만 구성된 단어를 배제
    text = text.lower()
    text = text.split()
    text = [ps.stem(word) for word in text if not word in sw] #remove stop words
    text = ' '.join(text)
    corpus.append(text)
  return corpus

abbreviations = {
    "$" : " dollar ",
    "€" : " euro ",
    "4ao" : "for adults only",
    "a.m" : "before midday",
    "a3" : "anytime anywhere anyplace",
    "aamof" : "as a matter of fact",
    "acct" : "account",
    "adih" : "another day in hell",
    "afaic" : "as far as i am concerned",
    "afaict" : "as far as i can tell",
    "afaik" : "as far as i know",
    "afair" : "as far as i remember",
    "afk" : "away from keyboard",
    "app" : "application",
    "approx" : "approximately",
    "apps" : "applications",
    "asap" : "as soon as possible",
    "asl" : "age, sex, location",
    "atk" : "at the keyboard",
    "ave." : "avenue",
    "aymm" : "are you my mother",
    "ayor" : "at your own risk",
    "b&b" : "bed and breakfast",
    "b+b" : "bed and breakfast",
    "b.c" : "before christ",
    "b2b" : "business to business",
    "b2c" : "business to customer",
    "b4" : "before",
    "b4n" : "bye for now",
    "b@u" : "back at you",
    "bae" : "before anyone else",
    "bak" : "back at keyboard",
    "bbbg" : "bye bye be good",
    "bbc" : "british broadcasting corporation",
    "bbias" : "be back in a second",
    "bbl" : "be back later",
    "bbs" : "be back soon",
    "be4" : "before",
    "bfn" : "bye for now",
    "blvd" : "boulevard",
    "bout" : "about",
    "brb" : "be right back",
    "bros" : "brothers",
    "brt" : "be right there",
    "bsaaw" : "big smile and a wink",
    "btw" : "by the way",
    "bwl" : "bursting with laughter",
    "c/o" : "care of",
    "cet" : "central european time",
    "cf" : "compare",
    "cia" : "central intelligence agency",
    "csl" : "can not stop laughing",
    "cu" : "see you",
    "cul8r" : "see you later",
    "cv" : "curriculum vitae",
    "cwot" : "complete waste of time",
    "cya" : "see you",
    "cyt" : "see you tomorrow",
    "dae" : "does anyone else",
    "dbmib" : "do not bother me i am busy",
    "diy" : "do it yourself",
    "dm" : "direct message",
    "dwh" : "during work hours",
    "e123" : "easy as one two three",
    "eet" : "eastern european time",
    "eg" : "example",
    "embm" : "early morning business meeting",
    "encl" : "enclosed",
    "encl." : "enclosed",
    "etc" : "and so on",
    "faq" : "frequently asked questions",
    "fawc" : "for anyone who cares",
    "fb" : "facebook",
    "fc" : "fingers crossed",
    "fig" : "figure",
    "fimh" : "forever in my heart",
    "ft." : "feet",
    "ft" : "featuring",
    "ftl" : "for the loss",
    "ftw" : "for the win",
    "fwiw" : "for what it is worth",
    "fyi" : "for your information",
    "g9" : "genius",
    "gahoy" : "get a hold of yourself",
    "gal" : "get a life",
    "gcse" : "general certificate of secondary education",
    "gfn" : "gone for now",
    "gg" : "good game",
    "gl" : "good luck",
    "glhf" : "good luck have fun",
    "gmt" : "greenwich mean time",
    "gmta" : "great minds think alike",
    "gn" : "good night",
    "g.o.a.t" : "greatest of all time",
    "goat" : "greatest of all time",
    "goi" : "get over it",
    "gps" : "global positioning system",
    "gr8" : "great",
    "gratz" : "congratulations",
    "gyal" : "girl",
    "h&c" : "hot and cold",
    "hp" : "horsepower",
    "hr" : "hour",
    "hrh" : "his royal highness",
    "ht" : "height",
    "ibrb" : "i will be right back",
    "ic" : "i see",
    "icq" : "i seek you",
    "icymi" : "in case you missed it",
    "idc" : "i do not care",
    "idgadf" : "i do not give a damn fuck",
    "idgaf" : "i do not give a fuck",
    "idk" : "i do not know",
    "ie" : "that is",
    "i.e" : "that is",
    "ifyp" : "i feel your pain",
    "IG" : "instagram",
    "iirc" : "if i remember correctly",
    "ilu" : "i love you",
    "ily" : "i love you",
    "imho" : "in my humble opinion",
    "imo" : "in my opinion",
    "imu" : "i miss you",
    "iow" : "in other words",
    "irl" : "in real life",
    "j4f" : "just for fun",
    "jic" : "just in case",
    "jk" : "just kidding",
    "jsyk" : "just so you know",
    "l8r" : "later",
    "lb" : "pound",
    "lbs" : "pounds",
    "ldr" : "long distance relationship",
    "lmao" : "laugh my ass off",
    "lmfao" : "laugh my fucking ass off",
    "lol" : "laughing out loud",
    "ltd" : "limited",
    "ltns" : "long time no see",
    "m8" : "mate",
    "mf" : "motherfucker",
    "mfs" : "motherfuckers",
    "mfw" : "my face when",
    "mofo" : "motherfucker",
    "mph" : "miles per hour",
    "mr" : "mister",
    "mrw" : "my reaction when",
    "ms" : "miss",
    "mte" : "my thoughts exactly",
    "nagi" : "not a good idea",
    "nbc" : "national broadcasting company",
    "nbd" : "not big deal",
    "nfs" : "not for sale",
    "ngl" : "not going to lie",
    "nhs" : "national health service",
    "nrn" : "no reply necessary",
    "nsfl" : "not safe for life",
    "nsfw" : "not safe for work",
    "nth" : "nice to have",
    "nvr" : "never",
    "nyc" : "new york city",
    "oc" : "original content",
    "og" : "original",
    "ohp" : "overhead projector",
    "oic" : "oh i see",
    "omdb" : "over my dead body",
    "omg" : "oh my god",
    "omw" : "on my way",
    "p.a" : "per annum",
    "p.m" : "after midday",
    "pm" : "prime minister",
    "poc" : "people of color",
    "pov" : "point of view",
    "pp" : "pages",
    "ppl" : "people",
    "prw" : "parents are watching",
    "ps" : "postscript",
    "pt" : "point",
    "ptb" : "please text back",
    "pto" : "please turn over",
    "qpsa" : "what happens", #"que pasa",
    "ratchet" : "rude",
    "rbtl" : "read between the lines",
    "rlrt" : "real life retweet",
    "rofl" : "rolling on the floor laughing",
    "roflol" : "rolling on the floor laughing out loud",
    "rotflmao" : "rolling on the floor laughing my ass off",
    "rt" : "retweet",
    "ruok" : "are you ok",
    "sfw" : "safe for work",
    "sk8" : "skate",
    "smh" : "shake my head",
    "sq" : "square",
    "srsly" : "seriously",
    "ssdd" : "same stuff different day",
    "tbh" : "to be honest",
    "tbs" : "tablespooful",
    "tbsp" : "tablespooful",
    "tfw" : "that feeling when",
    "thks" : "thank you",
    "tho" : "though",
    "thx" : "thank you",
    "tia" : "thanks in advance",
    "til" : "today i learned",
    "tl;dr" : "too long i did not read",
    "tldr" : "too long i did not read",
    "tmb" : "tweet me back",
    "tntl" : "trying not to laugh",
    "ttyl" : "talk to you later",
    "u" : "you",
    "u2" : "you too",
    "u4e" : "yours for ever",
    "utc" : "coordinated universal time",
    "w/" : "with",
    "w/o" : "without",
    "w8" : "wait",
    "wassup" : "what is up",
    "wb" : "welcome back",
    "wtf" : "what the fuck",
    "wtg" : "way to go",
    "wtpa" : "where the party at",
    "wuf" : "where are you from",
    "wuzup" : "what is up",
    "wywh" : "wish you were here",
    "yd" : "yard",
    "ygtr" : "you got that right",
    "ynk" : "you never know",
    "zzz" : "sleeping bored and tired"
}

def convert_abbrev(word):
    return abbreviations[word.lower()] if word.lower() in abbreviations.keys() else word

# 함수적용 후 전처리 데이터 기존 데이터프레임에 추가
train['text_processed'] = text_preprocessing(train)
test['text_processed'] = text_preprocessing(test)

train['text_processed'] = train['text_processed'].apply(lambda x: convert_abbrev(x))
test['text_processed'] = test['text_processed'].apply(lambda x: convert_abbrev(x))

train.head(3)

test.head(3)

X = train['text_processed']
y = train['target']

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1,random_state=42)

vectorizer = TfidfVectorizer(ngram_range=(1,3),min_df=3,strip_accents='unicode', use_idf=1,smooth_idf=1, sublinear_tf=1,max_features=None)
vectorizer.fit(list(train['text_processed'])+list(test['text_processed'])) # 왜합치지??
print('vocab length',len(vectorizer.vocabulary_))

X_train_onehot = vectorizer.transform(X_train).todense()
X_val_onehot = vectorizer.transform(X_val).todense()

# 일반 회귀분석
lr_clf = LogisticRegression(max_iter=150,penalty='l2',solver='lbfgs',random_state=0) # 페널티 종류: https://scikit-learn.org/stable/auto_examples/linear_model/plot_logistic_l1_l2_sparsity.html
lr_clf.fit(X_train_onehot, y_train)
lr_pred = lr_clf.predict(X_val_onehot)

print('accuracy score: ', accuracy_score(lr_pred,y_val))
print(classification_report(y_val, lr_pred))

logloss_lr = log_loss(y_val,lr_clf.predict_proba(X_val_onehot)) # Kaggle 에서 빈번히 사용되는 측정지표. 틀릴 수록 민감하게 내려간다
print('logloss_lr:',logloss_lr)

# 일반 Bayes
mnb_clf = MultinomialNB()
mnb_clf.fit(X_train_onehot, y_train)
mnb_pred = mnb_clf.predict(X_val_onehot)

print('accuracy score: ',accuracy_score(mnb_pred,y_val))
print(classification_report(y_val, mnb_pred))

logloss_mnb = log_loss(y_val,mnb_clf.predict_proba(X_val_onehot)) 
print('logloss_lr:',logloss_mnb)

# RandomForest
rf_clf = RandomForestClassifier(random_state=0,n_estimators=100,
                                max_depth=None, verbose=0,n_jobs=-1)
rf_clf.fit(X_train_onehot, y_train)
rf_pred = rf_clf.predict(X_val_onehot)

print('accuracy score: ',accuracy_score(rf_pred,y_val))
print(classification_report(y_val, rf_pred))

logloss_rf = log_loss(y_val,rf_clf.predict_proba(X_val_onehot))
print('logloss_rf:',logloss_rf)

# 적용모델 결정
rf_predictions_val = rf_clf.predict_proba(X_val_onehot)
predictions_val = rf_predictions_val[:, 1] # random forest 로 적용 # 모델 결과값 누적될수록 Averaging 통해 ensemble 효과 부여 가능
predictions_val = np.where(predictions_val>0.5, 1, 0)

print('accuracy score: ',accuracy_score(predictions_val,y_val))
print(classification_report(y_val, predictions_val))

# 테스트 데이터 예측
test.head()

X_test = test['text_processed']
X_test_onehot = vectorizer.transform(X_test).todense()

# 적용모델 결정
rf_predictions = rf_clf.predict_proba(X_test_onehot)
predictions = rf_predictions_val[:, 1] # random forest 로 적용 # 모델 결과값 누적될수록 Averaging 통해 ensemble 효과 부여 가능
predictions = np.where(predictions_val>0.5, 1, 0)

#결과파일 출력
submission = pd.read_csv('/content/drive/My Drive/Colab Notebooks/final/team/sample_submission.csv')
submission['target'] = predictions
submission.to_csv('submission_rf.csv', index=False)