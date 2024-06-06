import os
import nltk
import pandas as pd
import numpy as np
from nltk.stem.lancaster import LancasterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split as tts
from sklearn.preprocessing import LabelEncoder as LE
from sklearn.svm import SVC
from sentence_transformers import SentenceTransformer
import faiss
import pdb

import logging
#Define FaqEngine class
class FaqEngine:
    def __init__(self, faqslist, type='sentence-transformers'):
        self.faqslist = faqslist
        self.vectorizer = None
        self.stemmer = LancasterStemmer() 
        self.le = LE()
        self.classifier = None
        #Call build_model method
        self.build_model(type)

    #Cleanup method
    def cleanup(self, sentence):
        word_tok = nltk.word_tokenize(sentence)
        stemmed_words = [self.stemmer.stem(w) for w in word_tok]
        return ' '.join(stemmed_words)
    
    #Build_model method
    def build_model(self, type):
        if type == 'sentence-transformers':
            self.model = SentenceTransformer('./all-MiniLM-L6-v2')
        else:
            # Define your custom vectorizer here
            pass
        
        #Read CSV files from faqslist
        dataframeslist = [pd.read_csv(csvfile).dropna() for csvfile in self.faqslist]        
        self.data = pd.concat(dataframeslist, ignore_index=True)#Concatenate dataframes from CSV files
        self.data['Clean_Question'] = self.data['Question'].apply(lambda x : self.cleanup(x))
        self.embeds = self.model.encode(self.data['Clean_Question'].tolist())#Encode questions using SentenceTransformer model
       
    # Encode_sentence method
    def encode_sentence(self, sentence):
        return self.vectorizer.encode(sentence)
    
    #Query method
    def query(self, usr):
        try:
            cleaned_usr = self.cleanup(usr)
            usr_embed = self.model.encode(cleaned_usr)#Encode user query
            simillarity = usr_embed @ self.embeds.T#Compute similarity between user query and FAQ questions
            ind = np.argmax(simillarity)
            print(self.data.iloc[ind])
            # print(cleaned_usr,simillarity[ind])
            logging.info(f"{simillarity[ind]}")
                
            
            #If similarity above threshold:
            if simillarity[ind] > 0.3:  # Adjust threshold as needed
                print(self.data['class'].iloc[ind])
                return self.data['Answer'].iloc[ind],self.data['class'].iloc[ind]
            else:
                #If similarity below threshold Return default message
                return "Could not understand your query. Please rephrase it again","OutOfScope"
        except Exception as e:
            print(e)
            return "Could not follow your question [" + usr + "], Try again","Exception"


if __name__ == "__main__":
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    faqslist = [os.path.join(base_path, "Greetings.csv"), os.path.join(base_path, "sumasoft.csv"),os.path.join(base_path, "Information.csv"),os.path.join(base_path, "Acknowledgement.csv")]
    faqmodel = FaqEngine(faqslist, 'sentence-transformers')
    response = faqmodel.query("Hi")
    print(response)