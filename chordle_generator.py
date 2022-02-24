white = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

scale = [
    ['C', 'B#', 'Dbb'],
    ['C#', 'Db', 'Bx'],
    ['D', 'Cx', 'Ebb'],
    ['D#', 'Eb', 'Fbb'],
    ['E', 'Fb', 'Dx'],
    ['F', 'E#', 'Gbb'],
    ['F#', 'Gb', 'Ex'],
    ['G', 'Fx', 'Abb'],
    ['G#', 'Ab'],
    ['A', 'Gx', 'Bbb'],
    ['A#', 'Bb', 'Cbb'],
    ['B', 'Cb', 'Ax'],
]

intervals = [
    [4, 7, 11], #maj7
    [3, 7, 10], #min7
    [4, 7, 10], #dom7
    [3, 6, 9],  #dim7
    [3, 6, 10], #halfdim7
    [4, 8, 11], #augmaj7
    [4, 8, 10], #augmin7
    [3, 7, 11], #minmaj7
    [4, 10, 14], #dom9
    [4, 10, 13], #dom7b9
    [4, 10, 21], #dom13
    [4, 10, 20], #dom13b9
    [4, 7, 9], #maj6
    [3, 7, 9], #min6
]

distances = [
    [2, 4, 6],
    [2, 4, 6],
    [2, 4, 6],
    [2, 4, 6],
    [2, 4, 6],
    [2, 4, 6],
    [2, 4, 6],
    [2, 4, 6],
    [2, 6, 8],
    [2, 6, 8],
    [2, 6, 12],
    [2, 6, 12],
    [2, 4, 5],
    [2, 4, 5],
]
all_chords = [
    [], #maj7
    [], #min7
    [], #dom7
    [], #dim7
    [], #halfdim7
    [], #augmaj7
    [], #augmin7
    [], #minmaj7
    [], #dom9
    [], #dom7b9
    [], #dom13
    [], #dom7b13
    [], #maj6
    [], #min6
]

def get_note(note, root, dist, interval):
    base = white[(white.index(root[0]) + dist) % 7]
    for i in scale[(note + interval) % 12]:
        if i[0] == base:
            return i
    return False

for c, i in enumerate(scale):
    for j in range(2):
        root = i[j]
        if root in ["B#", "E#", "Cx", "Fx", "Gx"]:
            continue
        for d, chord in enumerate(intervals):
            result_chord = []
            for k in range(3):
                result_chord.append(get_note(c, root, distances[d][k], chord[k]))
            if False not in result_chord:
                all_chords[d].append(f'{root} {" ".join(result_chord)}')

f = open("chordlist.txt", "w")
for i in all_chords:
    for j in i:
        f.write(j + "\n")
    f.write("\n")