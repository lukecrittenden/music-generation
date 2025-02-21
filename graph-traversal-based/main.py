from midiutil import MIDIFile
import random

TRACK = 0
CHANNEL = 0
TEMPO = 120
VOLUME = 90
NOTE_DURATION = 2

def OutputMIDI(chords, filename):
    try:
        MIDIMelody = MIDIFile(1)
        MIDIMelody.addTempo(TRACK, 0, TEMPO)
        for note in chords.chords:
            MIDIMelody.addNote(TRACK, CHANNEL, note[0], note[1], note[2], VOLUME)
        with open(filename + ".mid", "wb") as outputFile:
            MIDIMelody.writeFile(outputFile)
    except:
        print("An error occurred while generating the MIDI file")

class Chords():
    def __init__(self, graph):
        self.chords = []
        self.graph = graph

    def generateChords(self, totalChords):
        time = 0

        currentChord = random.choice(list(self.graph.keys()))
        self.chords.extend([(currentChord[0], time, NOTE_DURATION), (currentChord[1], time, NOTE_DURATION), (currentChord[2], time, NOTE_DURATION)])

        while len(self.chords) // 3 < totalChords and currentChord in self.graph and self.graph[currentChord]:
            nextChord = random.choice(self.graph[currentChord])
            time += NOTE_DURATION
            self.chords.extend([(nextChord[0], time, NOTE_DURATION), (nextChord[1], time, NOTE_DURATION), (nextChord[2], time, NOTE_DURATION)])
            currentChord = nextChord

if __name__ == '__main__':
    graph = {
        (60, 64, 67): [(65, 69, 72), (67, 71, 74), (62, 65, 69), (64, 67, 71)],
        (65, 69, 72): [(67, 71, 74), (60, 64, 67), (69, 72, 76), (62, 65, 69)],
        (67, 71, 74): [(60, 64, 67), (65, 69, 72), (69, 72, 76), (64, 67, 71)],
        (62, 65, 69): [(60, 64, 67), (65, 69, 72), (67, 71, 74), (64, 67, 71)],
        (64, 67, 71): [(60, 64, 67), (65, 69, 72), (67, 71, 74), (62, 65, 69)],
        (69, 72, 76): [(60, 64, 67), (65, 69, 72), (67, 71, 74), (64, 67, 71)],
        (60, 63, 67): [(65, 68, 72), (67, 70, 74), (62, 65, 68), (64, 67, 70)],
        (65, 68, 72): [(67, 70, 74), (60, 63, 67), (69, 72, 75), (62, 65, 68)],
        (67, 70, 74): [(60, 63, 67), (65, 68, 72), (69, 72, 75), (64, 67, 70)],
        (62, 65, 68): [(60, 63, 67), (65, 68, 72), (67, 70, 74), (64, 67, 70)],
        (64, 67, 70): [(60, 63, 67), (65, 68, 72), (67, 70, 74), (62, 65, 68)],
        (69, 72, 75): [(60, 63, 67), (65, 68, 72), (67, 70, 74), (64, 67, 70)],
    }

    chordProgression = Chords(graph)
    chordProgression.generateChords(4)

    OutputMIDI(chordProgression, "Untitled")