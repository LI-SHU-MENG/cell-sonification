import pandas as pd
import pretty_midi
import numpy as np

# Load your data
# replace with your CSV file
df = pd.read_csv(
    "/Users/shumengli/Python_tuto/sonification_cell_test/cell table.csv")
data = df["AngleXY"].values

# Normalize data to MIDI pitch range (e.g. 40 to 80)
min_pitch = 60
max_pitch = 127
normalized = np.interp(data, (min(data), max(data)), (min_pitch, max_pitch))

# Create a PrettyMIDI object
midi = pretty_midi.PrettyMIDI()
instrument = pretty_midi.Instrument(program=0)  # 0 = Acoustic Grand Piano

# Create note sequence
start_time = 0
duration = 0.5  # seconds per note

for pitch in normalized:
    note = pretty_midi.Note(
        velocity=100,
        pitch=int(pitch),
        start=start_time,
        end=start_time + duration
    )
    instrument.notes.append(note)
    start_time += duration  # advance time

midi.instruments.append(instrument)

# Save the MIDI file
midi.write("sonified_output.mid")
