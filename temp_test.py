import numpy as np
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.model_selection import train_test_split
from functions import read_database, label_encoding, process_text
from torch.utils.data import DataLoader, TensorDataset, RandomSampler, SequentialSampler

# 1. Load and preprocess data
sentences_raw, labels_raw, all_intents = read_database('../../db.sqlite3')
for i in range(len(sentences_raw)):
    sentences_raw[i] = process_text(sentences_raw[i])

# Split the data into train and test sets
sentences_train, sentences_test, labels_train, labels_test = train_test_split(sentences_raw, labels_raw, test_size=0.3)

# 2. Tokenize the data using BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
train_encodings = tokenizer(sentences_train, truncation=True, padding=True, max_length=50, return_tensors="pt")
test_encodings = tokenizer(sentences_test, truncation=True, padding=True, max_length=50, return_tensors="pt")

# Convert labels to tensors
y_train = label_encoding(labels_train)
y_test = label_encoding(labels_test)
train_labels = torch.tensor(y_train)
test_labels = torch.tensor(y_test)

# Create DataLoader for training and validation data
train_dataset = TensorDataset(train_encodings.input_ids, train_encodings.attention_mask, train_labels)
train_loader = DataLoader(train_dataset, sampler=RandomSampler(train_dataset), batch_size=8)
test_dataset = TensorDataset(test_encodings.input_ids, test_encodings.attention_mask, test_labels)
test_loader = DataLoader(test_dataset, sampler=SequentialSampler(test_dataset), batch_size=8)


# 3. Create BERT model for sequence classification
num_labels = len(all_intents)
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels)
model.train()

# 4. Train the model
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
for epoch in range(100):  # Number of epochs can be adjusted
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids, attention_mask, labels = batch
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()

    # Validation after each epoch
    model.eval()  # Set the model to evaluation mode
    correct = 0
    total = 0
    with torch.no_grad():
        for batch in test_loader:
            input_ids, attention_mask, labels = batch
            outputs = model(input_ids, attention_mask=attention_mask)
            _, predicted = torch.max(outputs.logits, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = correct / total
    print(f'Validation Accuracy after epoch {epoch + 1}: {accuracy:.2f}')
    model.train()  # Set the model back to training mode

# 5. Save the trained model
model.save_pretrained("./data/bert_model")
tokenizer.save_pretrained("./data/bert_model")

# Final test accuracy after training
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for batch in test_loader:
        input_ids, attention_mask, labels = batch
        outputs = model(input_ids, attention_mask=attention_mask)
        _, predicted = torch.max(outputs.logits, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

final_accuracy = correct / total
print(f'Final Test Accuracy: {final_accuracy:.2f}')