import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from utils import midiFilesToNotes, saveMidi

def loadModel():
    return tf.keras.models.load_model('lstm_model.keras')

def generateNotes(model, selectedNotes, seqLength, numNotes, temperature=0.8):
    selectedNotes = np.array(selectedNotes, dtype=float)
    seed = np.array(selectedNotes[-seqLength:])
    generated = []
    fullSequence = selectedNotes.tolist()

    currentSequence = seed.copy()

    for _ in range(numNotes):
        pred = model.predict(currentSequence[np.newaxis, ...])[0]

        pred[0] = sampleWithTemperature(pred[0], temperature)
        pred[1] = sampleWithTemperature(pred[1], temperature)

        note_value = int(np.clip(round(pred[0] * 127), 0, 127))
        duration = int(np.clip(round(pred[1] * np.max(selectedNotes[:, 1])), 1, np.max(selectedNotes[:, 1])))

        note = [note_value, duration]
        generated.append(note)
        fullSequence.append(note)

        currentSequence = np.array(fullSequence[-seqLength:])

    return generated

def sampleWithTemperature(value, temperature):
    if temperature == 0:
        return value
    else:
        noise = np.random.normal(0, temperature)
        return np.clip(value + noise, 0, 127)

def plotNotes(originalNotes, generatedNotes, title):
    plt.figure(figsize=(10, 4))

    originalNoteValues = []
    for note in originalNotes:
        originalNoteValues.append(note[0])

    generatedNoteValues = []
    for note in generatedNotes:
        generatedNoteValues.append(note[0])

    plt.plot(range(len(originalNotes)), originalNoteValues, 'bo', markersize=2, label='Original Notes')
    plt.plot(range(len(originalNotes), len(originalNotes) + len(generatedNotes)), generatedNoteValues, 'ro', markersize=2, label='Generated Notes')
    plt.title(title)
    plt.xlabel('Time Step')
    plt.ylabel('Note')
    plt.legend()
    plt.show()

def main():
    seqLength = 50
    model = loadModel()

    datasetDir = os.path.join(os.path.dirname(__file__), 'dataset')
    selectedFile = os.path.join(datasetDir, input('Select a MIDI file to extend (e.g. file.mid): '))
    selectedNotes = midiFilesToNotes([selectedFile])[selectedFile]

    generatedNotes = generateNotes(model, selectedNotes, seqLength, 100, temperature=0.4)

    saveMidi(selectedNotes, generatedNotes, 'extended_music.mid')
    plotNotes(selectedNotes, generatedNotes, 'Original and Extended MIDI Notes')

if __name__ == '__main__':
    main()