import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from keras.models import Model
from keras.layers import Input,LSTM, Dense


batch_size = 64  # Batch size for training
epochs = 100     # Number of epochs to train for
latent_dim = 256 # Latent dimensionality of the encoding space (Hidden State size)

# Toy Dataset (English -> French)
data_path = [
    ("Go.", "Va !"),
    ("Run!", "Cours !"),
    ("Run.", "Cours !"),
    ("Who?", "Qui ?"),
    ("Wow!", "Ça alors !"),
    ("Fire!", "Au feu !"),
    ("Help!", "À l'aide !"),
    ("Stop!", "Arrête-toi !"),
    ("Wait!", "Attends !"),
    ("Hello!", "Bonjour !"),
    ("I see.", "Je comprends.") 
]

input_texts = []
target_texts = []
input_characters = set()
target_characters = set()

for input_text, target_text in data_path:
    # We use "tab" as the "start sequence" character
    # for the targets, and "\n" as "end sequence" character.
    target_text = '\t' + target_text + '\n'
    
    input_texts.append(input_text)
    target_texts.append(target_text)
    
    for char in input_text:
        if char not in input_characters:
            input_characters.add(char)
    for char in target_text:
        if char not in target_characters:
            target_characters.add(char)

input_characters = sorted(list(input_characters))
target_characters = sorted(list(target_characters))
num_encoder_tokens = len(input_characters)
num_decoder_tokens = len(target_characters)
max_encoder_seq_length = max([len(txt) for txt in input_texts])
max_decoder_seq_length = max([len(txt) for txt in target_texts])

print(f"Number of samples: {len(input_texts)}")
print(f"Number of unique input tokens: {num_encoder_tokens}")
print(f"Number of unique output tokens: {num_decoder_tokens}")

# Create Token Mappings (Char -> Integer)
input_token_index = dict([(char, i) for i, char in enumerate(input_characters)])
target_token_index = dict([(char, i) for i, char in enumerate(target_characters)])

# Reverse Mapping (Integer -> Char) for decoding later
reverse_input_char_index = dict((i, char) for char, i in input_token_index.items())
reverse_target_char_index = dict((i, char) for char, i in target_token_index.items())

# Generate One-Hot Encoded Data
# Encoder Input: (num_samples, max_len, unique_chars)
encoder_input_data = np.zeros((len(input_texts), max_encoder_seq_length, num_encoder_tokens), dtype='float32')
# Decoder Input: Same but for target
decoder_input_data = np.zeros((len(input_texts), max_decoder_seq_length, num_decoder_tokens), dtype='float32')
# Decoder Target: Same but shifted by one (predict the NEXT char)
decoder_target_data = np.zeros((len(input_texts), max_decoder_seq_length, num_decoder_tokens), dtype='float32')

for i, (input_text, target_text) in enumerate(zip(input_texts, target_texts)):
    for t, char in enumerate(input_text):
        encoder_input_data[i, t, input_token_index[char]] = 1.
    encoder_input_data[i, t + 1:, input_token_index[' ']] = 1. # Padding

    for t, char in enumerate(target_text):
        # Decoder Input
        decoder_input_data[i, t, target_token_index[char]] = 1.
        if t > 0:
            # Decoder Target is ahead by 1 (it doesn't see the start char)
            decoder_target_data[i, t - 1, target_token_index[char]] = 1.
            
    decoder_input_data[i, t + 1:, target_token_index[' ']] = 1. # Padding
    decoder_target_data[i, t:, target_token_index[' ']] = 1. # Padding


# --- Encoder ---
encoder_inputs = Input(shape=(None, num_encoder_tokens))
# return_state=True tells LSTM to output the hidden state (h) and cell state (c)
encoder = LSTM(latent_dim, return_state=True) 
encoder_outputs, state_h, state_c = encoder(encoder_inputs)
# We discard 'encoder_outputs' and only keep the states.
encoder_states = [state_h, state_c] 

# --- Decoder ---
decoder_inputs = Input(shape=(None, num_decoder_tokens))
# We set up our decoder to return full output sequences, and to return internal states as well.
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
# The Critical Step: Initialize Decoder with Encoder's States
decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
decoder_dense = Dense(num_decoder_tokens, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# Define the model that takes encoder/decoder inputs and outputs target
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

# Compile & Train
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
print("\nTraining Model...")
model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
          batch_size=batch_size,
          epochs=epochs,
          validation_split=0.2,
          verbose=0) # Set verbose=1 to see epoch progress