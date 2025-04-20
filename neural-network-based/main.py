import numpy as np
import tensorflow as tf
import pretty_midi

class MidiMusicGenerator:
    def __init__(self, modelPath='trained_model.keras', dataPath='training_data.npz', sequenceLength=25):
        self.sequenceLength = sequenceLength
        self.numPitches = 128
            
        self.model = tf.keras.models.load_model(modelPath)
        data = np.load(dataPath)
        self.X = data['X']
        self.y = data['y']

    def sampleWithTemperature(self, preds, temperature=1.0):
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds + 1e-8) / temperature
        expPreds = np.exp(preds)
        preds = expPreds / np.sum(expPreds)
        return np.random.choice(range(len(preds)), p=preds)

    def generateMusic(self, seedSequence, length=100):
        generated = list(seedSequence)
        for _ in range(length):
            inputSeq = np.array(generated[-(self.sequenceLength - 1):])
            inputSeq = inputSeq / self.numPitches
            inputSeq = np.expand_dims(inputSeq, axis=0)
            prediction = self.model.predict(inputSeq, verbose=0)
            nextNote = self.sampleWithTemperature(prediction[0], temperature=0.8)
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
    generator = MidiMusicGenerator()
    seedSeq = generator.X[0] * generator.numPitches
    generatedSeq = generator.generateMusic(seedSeq)
    generator.saveMidi(generatedSeq)
