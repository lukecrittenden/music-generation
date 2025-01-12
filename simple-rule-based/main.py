from midiutil import MIDIFile
import random
from typing import List, Tuple

C_MAJ = [60, 62, 64, 65, 67, 69, 71, 72]
C_MIN = [60, 62, 63, 65, 67, 68, 71, 72]

TRACK = 0
CHANNEL = 0
TEMPO = 120
VOLUME = 90

LEAP_CHANCE = 0.35

def OutputMIDI(melody: 'Melody', chords: 'Chords', mode: List[int], transposeAmount: int, filename: str) -> None:
    try:
        MIDIMelody = MIDIFile(1)
        MIDIMelody.addTempo(TRACK, 0, TEMPO)
        for note in melody.melody:
            MIDIMelody.addNote(TRACK, CHANNEL, mode[note[0]] + transposeAmount, note[1], note[2], VOLUME)
        for note in chords.chords:
            MIDIMelody.addNote(TRACK, CHANNEL, mode[note[0]] - 12 + transposeAmount, note[1], note[2], VOLUME)
        with open(filename + ".mid", "wb") as outputFile:
            MIDIMelody.writeFile(outputFile)
    except:
        print("An error occurred while generating the MIDI file")

class Melody:
    def __init__(self, length: int) -> None:
        self.length = length + (4 - length % 4) if length % 4 != 0 else length
        self.melody: List[Tuple[int, int, int]] = []

    def chooseNoteLength(self) -> int:
        return random.choice([1, 2, 4])
        
    def chooseNotePitch(self) -> int:
        return random.choice([0, 1, 2, 4, 5, 6, 7])

    def generateMelody(self) -> None:
        time = 0
        previousPitch = -1
        previousPitchCount = 0
        firstNote = True

        while self.length > 0:
            duration = self.chooseNoteLength()

            if self.length - duration >= 0:
                if firstNote:
                    pitch = random.choice([0, 4])
                    firstNote = False
                elif self.length - duration == 0:
                    pitch = random.choice([0, 7])
                else:
                    if random.random() < LEAP_CHANCE:
                        pitch = self.chooseNotePitch()
                    else:
                        pitch = random.choice([previousPitch - 1, previousPitch, previousPitch + 1])
                        if previousPitchCount >= 4:
                            pitch = random.choice([previousPitch - 1, previousPitch + 1])

                self.melody.append((pitch, time, duration))

                previousPitchCount = previousPitchCount + 1 if pitch == previousPitch else 0
                previousPitch = pitch
                time += duration
                self.length -= duration

class Chords:
    def __init__(self, melody: List[Tuple[int, int, int]]) -> None:
        self.melody = melody
        self.chords: List[Tuple[int, int, int]] = []

    def generateChords(self) -> None:
        chordMap = {
            0: [0, 2, 4, 7],
            2: [0, 2, 4, 7],
            4: [0, 2, 4, 7],
            7: [0, 2, 4, 7],
            3: [0, 3, 5, 7],
            5: [0, 3, 5, 7],
            6: [4, 6, 1],
            1: [4, 6, 1]
        }

        for pitch, time, duration in self.melody:
            chord = chordMap.get(pitch, [0, 2, 4, 7])
            self.chords.extend([(chord[0], time, duration), (chord[1], time, duration), (chord[2], time, duration)])

if __name__ == '__main__':
    melody = Melody(32)
    melody.generateMelody()

    chords = Chords(melody.melody)
    chords.generateChords()

    mode = random.choice([C_MAJ, C_MIN])
    transposeAmount = random.randint(0, 11)

    OutputMIDI(melody, chords, mode, transposeAmount, "Untitled")