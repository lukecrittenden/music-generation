import pathlib
import tensorflow as tf
import numpy as np
import pandas as pd
import pretty_midi
import glob

from typing import Optional

class MidiGeneratorModel:
    def __init__(self, dataPath='data/maestro-v2.0.0', sequenceLength=25, samplingRate=16000):
        self.sequenceLength = sequenceLength
        self.numPitches = 128
        self.samplingRate = samplingRate
        self.dataPath = pathlib.Path(dataPath)

        self.model = None
        self.notesDf = None
        self.X = None
        self.y = None

        self._ensureDataDownloaded()
        self._loadData(fileLimit=1)
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

    def _loadData(self, fileLimit=20):
        fileNames = glob.glob(str(self.dataPath / '**/*.mid*'), recursive=True)
        print(f'Total MIDI files: {len(fileNames)}')
        allNotes = []

        if fileLimit is not None:
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

    def save(self, modelPath='trained_model.keras', dataPath='training_data.npz'):
        self.model.save(modelPath)
        np.savez_compressed(dataPath, X=self.X, y=self.y)
        print(f"Model saved to '{modelPath}' and data saved to '{dataPath}'")


if __name__ == '__main__':
    midiGen = MidiGeneratorModel()
    midiGen.train()
    midiGen.save()
