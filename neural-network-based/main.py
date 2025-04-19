import collections
import datetime
import glob
import numpy as np
import pathlib
import pandas as pd
import pretty_midi
import seaborn as sns
import tensorflow as tf
import os

from matplotlib import pyplot as plt
from typing import Optional

class MidiGeneratorModel:
    def __init__(self, dataPath='data/maestro-v2.0.0', sequenceLength=25, samplingRate=16000):
        # self.seed = 42
        self.sequenceLength = sequenceLength
        self.numPitches = 128
        self.samplingRate = samplingRate
        self.dataPath = pathlib.Path(dataPath)

        # tf.random.set_seed(self.seed)
        # np.random.seed(self.seed)

        self.model = None
        self.notesDf = None
        self.X = None
        self.y = None

        self._ensureDataDownloaded()
        self._loadData()
        self._prepareSequences()
        self._buildModel()

    def _ensureDataDownloaded(self):
        if not self.dataPath.exists():
            tf.keras.utils.get_file(
                'maestro-v2.0.0-midi.zip',
                origin='https://storage.googleapis.com/magentadata/datasets/maestro/v2.0.0/maestro-v2.0.0-midi.zip',
                extract=True,
                cache_dir='.',
                cache_subdir='data',
            )

    def _midiToNotes(self, midiFile):
        pm = pretty_midi.PrettyMIDI(midiFile)
        notes = []
        for instrument in pm.instruments:
            if not instrument.is_drum:
                for note in instrument.notes:
                    notes.append((note.start, note.end, note.pitch, note.velocity))
        notes.sort(key=lambda x: x[0])
        return notes

    def _loadData(self, fileLimit=5):
        fileNames = glob.glob(str(self.dataPath / '**/*.mid*'), recursive=True)
        print(f'Total MIDI files: {len(fileNames)}')
        allNotes = []

        if fileLimit != None:
            fileNames = fileNames[:fileLimit]

        for file in fileNames:
            notes = self._midiToNotes(file)
            allNotes.extend(notes)

        self.notesDf = pd.DataFrame(allNotes, columns=['start', 'end', 'pitch', 'velocity'])

    def _prepareSequences(self):
        pitchSequences = []
        step = 1
        for i in range(0, len(self.notesDf) - self.sequenceLength, step):
            seq = self.notesDf['pitch'].values[i:i + self.sequenceLength]
            pitchSequences.append(seq)

        pitchSequences = np.array(pitchSequences)
        self.X = pitchSequences[:, :-1] / self.numPitches
        self.y = tf.keras.utils.to_categorical(pitchSequences[:, -1], num_classes=self.numPitches)

    def _buildModel(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.sequenceLength - 1,)),
            tf.keras.layers.Embedding(input_dim=self.numPitches, output_dim=64),
            tf.keras.layers.LSTM(128),
            tf.keras.layers.Dense(self.numPitches, activation='softmax')
        ])

        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model.summary()

    def train(self, epochs=20, batchSize=64):
        self.model.fit(self.X, self.y, epochs=epochs, batch_size=batchSize)

    def generateMusic(self, seedSequence, length=100):
        generated = list(seedSequence)
        for _ in range(length):
            inputSeq = np.array(generated[-(self.sequenceLength - 1):])
            inputSeq = inputSeq / self.numPitches
            inputSeq = np.expand_dims(inputSeq, axis=0)
            prediction = self.model.predict(inputSeq, verbose=0)
            nextNote = np.argmax(prediction)
            generated.append(nextNote)
        return generated

    def saveMidi(self, sequence, outputFile='generated.mid'):
        midi = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0)
        start = 0
        duration = 0.5
        for pitch in sequence:
            note = pretty_midi.Note(velocity=100, pitch=int(pitch), start=start, end=start + duration)
            instrument.notes.append(note)
            start += duration
        midi.instruments.append(instrument)
        midi.write(outputFile)
        print(f"Generated music saved to '{outputFile}'")

if __name__ == '__main__':
    midiGen = MidiGeneratorModel()
    midiGen.train()

    seedSeq = midiGen.X[0] * midiGen.numPitches
    generatedSeq = midiGen.generateMusic(seedSeq)
    midiGen.saveMidi(generatedSeq)
