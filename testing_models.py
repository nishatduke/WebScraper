#https://huggingface.co/distilbert/distilroberta-base#training-details


import pandas as pd
import numpy as np
import time
import json

import logging,os
import pymssql
import configparser
import pypyodbc as obdc
import transformers, torch
from transformers import  pipeline, LlamaForSequenceClassification,AutoTokenizer,LlamaTokenizer, AutoModelForSequenceClassification,AutoModelForCausalLM, GenerationConfig,LongformerForSequenceClassification
from dotenv import load_dotenv

load_dotenv()

input_path = os.getenv("MAIN_DIR")
tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-mnli')
model = AutoModelForSequenceClassification.from_pretrained('facebook/bart-large-mnli')
super_good_text = '''

GOOD GOOD GOOD GOOD GOOD GOOD GOOD GOOD SUPER POSITIVE WORDS

'''
document_text_positive = '''
the money at our company is super high. 
Our business is fantastic. Life has never been better! 
I love everything so much!! Im so happy!!!'''
testNamePositive = "Positive Test"


document_text_negative = '''
the money at our company is super low. 
Our business is crap. Life has never been worse! 
I hate everything so much!! Im so sad!!!'''

testNameNegative = "Negative Test"


classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

candidate_labels = ["very positive","slightly positive","neutral", "slightly negative", "very negative"]
def run_main_model(text):
    results = classifier(text, candidate_labels)

    def calculate_score(results):
        def get_label_value(label):
            return {
                "very positive": 1,
                "slightly positive": 0.5,
                "neutral": 0,
                "slightly negative": -0.5,
                "very negative": -1
            }.get(label, 0)  # default to 0 if label not found

        label_values = [get_label_value(label) for label in results["labels"]]
        final_score = np.dot(label_values, results["scores"]) * 100
        return final_score

    print("Classification Results:")
    print(results)
    final_score= calculate_score(results)
    print(final_score) 
    return final_score
run_main_model(super_good_text)