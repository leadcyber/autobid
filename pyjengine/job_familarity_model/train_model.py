from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding
from keras.layers import GRU, LSTM
from keras.layers import Conv1D, MaxPooling1D
import numpy as np
from keras.preprocessing.text import Tokenizer
import random
import math

from utils.skills import get_skill_list, get_required_skill_groups
from utils import db
from job import get_jd_score

from gensim.models.keyedvectors import KeyedVectors
word_vect = KeyedVectors.load_word2vec_format("./job_familarity_model/Model/SO_vectors_200.bin", binary=True)


EMBEDDING_DIM = word_vect['react'].shape[0]
MAX_SEQUENCE_LENGTH = 40
alternative = {
    "spa-framework": "singlepageapplication",
    "ethersjs": "ethers",
    "nestjs": "expressjs",
    "design-system": "design",
    "design-tool": "design",
    "collaboration-tool": "collaboration",
    "frontend-architecture": "architecture",
    "backend-architecture": "architecture",
    "dailystandup": "standup",
    "uniswap": "ethereum"
}

def Build_Model_RCNN_Text(word_index, embeddings_index, nclasses):
    global EMBEDDING_DIM, MAX_SEQUENCE_LENGTH
    print("Building model...")
    kernel_size = 2
    filters = 256
    pool_size = 2
    gru_node = 128

    embedding_matrix = np.random.random((len(word_index) + 1, EMBEDDING_DIM))
    for word, i in word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            if len(embedding_matrix[i]) != len(embedding_vector):
                print("could not broadcast input array from shape", str(len(embedding_matrix[i])),
                      "into shape", str(len(embedding_vector)
                                        ), " Please make sure your"
                      " EMBEDDING_DIM is equal to embedding_vector file ,GloVe,")
                exit(1)

            embedding_matrix[i] = embedding_vector

    model = Sequential()
    model.add(Embedding(len(word_index) + 1,
                        EMBEDDING_DIM,
                        weights=[embedding_matrix],
                        input_length=MAX_SEQUENCE_LENGTH,
                        trainable=False))
    model.add(Dropout(0.25))
    model.add(Conv1D(filters, kernel_size, activation='relu'))
    model.add(MaxPooling1D(pool_size=pool_size))
    model.add(LSTM(gru_node, return_sequences=True, recurrent_dropout=0.2))
    model.add(LSTM(gru_node, recurrent_dropout=0.2))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(nclasses))
    model.add(Activation('softmax'))


    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    print("Model built")
    return model

def to_understandable_skill(full_name):
    skill_name = full_name.lower().replace(" ", "-").replace(".", "")
    if skill_name in alternative:
        skill_name = alternative[skill_name]
    return skill_name

def load_data():
    print("Loading training data...")
    word_index = {}
    embeddings_index = {}

    skills = get_skill_list()
    skill_name_list = []
    for index, full_name in enumerate(skills):
        skill_name = to_understandable_skill(full_name)
        skill_name_list.append(skill_name)
    skill_name_list = list(set(skill_name_list))
    
    for index, skill_name in enumerate(skill_name_list):
        word_index[skill_name] = index + 1
        if skill_name in word_vect:
            embeddings_index[skill_name] = word_vect[skill_name]
            # print("-----", skill_name)
            # print(word_vect.most_similar(skill_name))
        else:
            print("unknown", skill_name)


    x_data = []
    y_data = []

    jobs = db.job_collection.find({"pageData.description": {"$not": {"$eq": None}}})
    count = 0
    for job in jobs:
        count += 1
        description = job["pageData"]["description"]
        groups = get_required_skill_groups(description)
        occurences = [ to_understandable_skill(item["skillName"]) for sub_list in groups for item in sub_list ]
        index_occurences = [ skill_name_list.index(occurence) + 1 for occurence in occurences ]
        if len(index_occurences) < MAX_SEQUENCE_LENGTH:
            index_occurences.extend([0] * (MAX_SEQUENCE_LENGTH - len(index_occurences)))
        else:
            index_occurences = index_occurences[0:MAX_SEQUENCE_LENGTH]
            
        x_data.append(index_occurences)

        score = get_jd_score(description)
        fit = True
        if score >= 7.5:
            fit = True
        elif score <= 4.8:
            fit = False
        else:
            fit = job["alreadyApplied"]
        y_data.append([0.0, 1.0] if fit else [1.0, 0.0])
        # if fit == False:
        #     print("----------" + job["position"] + "   :   " + str(score))
        #     print(" ".join(occurences))

    x_data = x_data[1500:]
    y_data = y_data[1500:]
    x_data_len = len(x_data)

    dataset = x_data
    labels = y_data
    # dataset = []
    # labels = []

    # Stretch train data
    # for index, item in enumerate(x_data):
    #     rand = random.random() * (index / x_data_len * 1.5 + 1) + 0.3
    #     count = round(rand)
    #     dataset.extend([item] * count)
    #     labels.extend([y_data[index]] * count)
    # print(len(x_data), len(dataset))


    test_data_percent = 0.1
    train_data_length = int(len(dataset) * (1.0 - test_data_percent))
    test_data_length = len(dataset) - train_data_length

    np.random.seed(7)
    print("Load completed")
    return \
        np.array(dataset[test_data_length:]), \
        np.array(dataset[0:test_data_length]), \
        np.array(labels[test_data_length:]), \
        np.array(labels[0:test_data_length]), \
        word_index, \
        embeddings_index


X_train, X_test, Y_train, Y_test, word_index, embeddings_index = load_data()

print(X_train.shape, "X shape")
print(Y_train.shape, "Y shape")

model_RCNN = Build_Model_RCNN_Text(word_index, embeddings_index, 2)
model_RCNN.summary()
model_RCNN.fit(X_train, Y_train,
                              validation_data=(X_test, Y_test),
                              epochs=15,
                              batch_size=128,
                              verbose=2)

predicted = model_RCNN.predict(X_test)
predicted = np.argmax(predicted, axis=1)
# print(metrics.classification_report(Y_test, predicted))
