#!/usr/bin/env python
# coding: utf8

"""Example of training spaCy's custom company name recognizer from copyright text.

For more details for training, see the documentation:
* Training: https://github.com/explosion/spaCy/blob/master/examples/training/train_ner.py
* NER: https://spacy.io/usage/linguistic-features#named-entities

Compatible with: spaCy v2.0.0+

"""

from __future__ import unicode_literals, print_function
import random
from pathlib import Path
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import pandas as pd
import traceback


def main(TRAIN_DATA, iterations, model=None, output_dir=None):

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    if 'ner' not in nlp.pipe_names:
        # ner = nlp.create_pipe('ner')
        nlp.add_pipe('ner', last=True)
        ner = nlp.get_pipe("ner")
    
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(iterations):
            print("Statring iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=8)
            for batch in batches:
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    examples.append(example)
                nlp.update(
                    examples,
                    drop=0.2,  # dropout - make it harder to memorise data
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


"""
It convert data into required spacy format
Example:
	# training data
	TRAIN_DATA = [
		('FootFall © Silicon Practice 2019', {'entities': [(11, 27, 'CompanyName')]}),
		('HTML5 Audio v3.1.0 Copyright 2013 Joe Workman',{'entities': [(34, 45, 'CompanyName')]}),
		('Copyright © 2019 by aDigital Solutions All international Rights Reserved',{'entities': [(20, 56, 'CompanyName')]})
	]
"""
def transform_data(row):
    result = None
    try:
        annotations = row['annotations']
        if len(annotations)>0 and annotations[0]['start_offset']>= 0 and annotations[0]['end_offset']>= 0: 
            result = (row['text'], {"entities": [(annotations[0]['start_offset'], annotations[0]['end_offset'],"CompanyName")]})
        return result
    except:
        traceback.print_exc()
        return result

TESTING_DATA = []
SAMPLE_ANSWERS = []

def test_saved_model(output_dir):
	global TESTING_DATA, SAMPLE_ANSWERS
	# test the saved model
	print("Loading from", output_dir)
	nlp2 = spacy.load(output_dir)
	correct = 0
	total = 0
	for index, text in enumerate(TESTING_DATA):
		doc = nlp2(text)
		if SAMPLE_ANSWERS[index] in [ ent.text for ent in doc.ents ]:
			correct += 1
		elif SAMPLE_ANSWERS[index] is not None:
			print(text, [ ent.text for ent in doc.ents ], SAMPLE_ANSWERS[index])
		if SAMPLE_ANSWERS[index] is not None:
			total += 1
		# print([ ent.text for ent in doc.ents ], SAMPLE_ANSWERS[index])
		# print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        
		# print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])
	print(correct, total)

if __name__ == "__main__":
	try:


		# Load training data
		df = pd.read_json('./Data/training_data.json', lines=True)
		df = df[['text', 'annotations']] # filter all column which not required
		print('df',df.columns, df.shape)
		for index, row in df.iterrows():
			TESTING_DATA.append(row['text'])
			SAMPLE = None
			if len(row['annotations']) > 0:
				# print(row['annotations'][0]['start_offset'])
				SAMPLE = row['text'][row['annotations'][0]['start_offset'] : row['annotations'][0]['end_offset']]
			SAMPLE_ANSWERS.append(SAMPLE)
		
		print('Testing data is ready now model testing started')
		print('Total Testing data size: ', len(TESTING_DATA))

		test_saved_model('./Model/')# change path if model stored in other loction
	except:
		traceback.print_exc()

# Command to run 
# python train_model.py
