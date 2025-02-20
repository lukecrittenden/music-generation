import os
from mido import MidiFile, MidiTrack, Message, MetaMessage

def loadMidiFiles(numFiles=None):
    datasetDir = os.path.join(os.path.dirname(__file__), 'dataset')
    files = []

    for file in os.listdir(datasetDir):
        if file.endswith('.mid'):
            files.append(os.path.join(datasetDir, file))

    if numFiles is not None:
        files = files[:numFiles]

    return files

def midiFilesToNotes(midiFiles):
    notes = {}
    print()

    for file in midiFiles:
        print('loading: ', file)
        midi = MidiFile(file)
        fileNotes = []
        activeNotes = {}
        absoluteTime = 0

        for msg in midi:
            absoluteTime += msg.time

            if msg.type == 'note_on' and msg.velocity > 0:
                activeNotes[msg.note] = absoluteTime
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in activeNotes:
                    duration = absoluteTime - activeNotes[msg.note]
                    fileNotes.append([msg.note, duration])
                    del activeNotes[msg.note]

        notes[file] = fileNotes

    return notes

def saveMidi(originalNotes, generatedNotes, outputFile):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    track.append(Message('program_change', program=12, time=0))
    track.append(MetaMessage('set_tempo', tempo=500000, time=0))

    def add_note(note, duration, timeOffset):
        note = int(note)
        note = max(0, min(127, note))
        duration = max(1, int(duration))
        timeOffset = max(0, int(timeOffset))
        track.append(Message('note_on', note=note, velocity=64, time=timeOffset))
        track.append(Message('note_off', note=note, velocity=64, time=duration))

    currentTime = 0
    for note, duration in originalNotes:
        add_note(note, duration, currentTime)
        currentTime += duration

    for note, duration in generatedNotes:
        add_note(note, duration, currentTime)
        currentTime += duration

    midi.save(outputFile)