from transformers import DistilBertTokenizer, TFDistilBertForQuestionAnswering
import tensorflow as tf

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad", cache_dir="./qa_model")
model = TFDistilBertForQuestionAnswering.from_pretrained("distilbert-base-uncased-distilled-squad", cache_dir="./qa_model")

question, text = "What is your first name?", "My name is Michael Chilelli."

inputs = tokenizer(question, text, return_tensors="tf")
outputs = model(**inputs)

answer_start_index = int(tf.math.argmax(outputs.start_logits, axis=-1)[0])
answer_end_index = int(tf.math.argmax(outputs.end_logits, axis=-1)[0])

predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
res = tokenizer.decode(predict_answer_tokens)
print(res)