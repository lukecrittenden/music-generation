import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input, Dropout
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping
from utils import loadMidiFiles, midiFilesToNotes

class LSTMModel:
    def __init__(self, seqLength, trainNotes):
        self.seqLength = seqLength
        self.trainNotes = np.array(trainNotes, dtype=float)
        self.prepData()
        self.buildModel()
        self.trainModel()
        self.saveModel()

    def prepData(self):
        self.trainNotes[:, 0] = self.trainNotes[:, 0] / 127.0
        self.trainNotes[:, 1] = self.trainNotes[:, 1] / np.max(self.trainNotes[:, 1])

        sequences = []
        targets = []

        for i in range(len(self.trainNotes) - self.seqLength):
            sequences.append(self.trainNotes[i:i + self.seqLength])
            targets.append(self.trainNotes[i + self.seqLength])

        self.X = np.array(sequences)
        self.y = np.array(targets)

    def buildModel(self):
        self.model = Sequential([
            Input(shape=(self.seqLength, 2)),
            LSTM(128, return_sequences=True, kernel_regularizer=l2(0.001)),
            Dropout(0.3),
            LSTM(128, kernel_regularizer=l2(0.001)),
            Dropout(0.3),
            Dense(64, activation='relu', kernel_regularizer=l2(0.001)),
            Dropout(0.3),
            Dense(2)
        ])
        self.model.summary()
        print()
        self.model.compile(loss='mean_squared_error', optimizer='adam')

    def trainModel(self):
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        self.model.fit(self.X, self.y, epochs=50, batch_size=64, validation_split=0.2, callbacks=[early_stop])

    def saveModel(self):
        self.model.save('lstm_model.keras')

def main():
    seqLength = 50

    numFilesInput = input("Enter the number of MIDI files to load from the dataset (or press Enter to use all files): ")
    numFiles = int(numFilesInput) if numFilesInput.strip() else None

    midiFiles = loadMidiFiles(numFiles)
    notesDict = midiFilesToNotes(midiFiles)

    trainingNotes = []
    for file, notes in notesDict.items():
        trainingNotes.extend(notes)

    if not trainingNotes:
        print("Error: No MIDI files available for training.")
        return

    print(f"\nTraining model using {len(midiFiles)} MIDI files...\n")
    network = LSTMModel(seqLength, trainingNotes)
    print("\nModel training complete and saved as 'lstm_model.keras'.")

if __name__ == '__main__':
    main()