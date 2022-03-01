import discord
from random import randint
from string import ascii_uppercase
import os
import json

W_INSTRUCTIONS = """
HOW TO PLAY WORDLE

Guess the secret word in six tries.
Each guess must be a valid five-letter word.
After each guess, information will be revealed about your guess:

A `codeblocked` letter means the letter is not in the word.
A **bolded** letter means the letter is in the word, but not in the right spot.
A __**bolded and underlined**__ letter means the letter is in the word and in the correct spot.

Type `$w play` to start a new game!
Type `$w guess` followed by a valid 5-letter word to guess words.
Type `$w available` to reveal the remaining possible letters.
Type `$w show` to show your guesses.
Type `$w quit` to end a game.
"""

C_INSTRUCTIONS = """
HOW TO PLAY CHORDLE

Guess the secret chord in four tries.
Each guess must be a valid chord. The following types of chords are available:

- maj7      (e.g.   `Cmaj7` - `C E G B`)
- min7      (e.g.   `Dbm7` - `Db Fb Ab Cb`)
- dom7      (e.g.   `D#7` - `D# Fx A# C#`)
- dim7      (e.g.   `Adim7` - `A C Eb Gb`)
- halfdim7  (e.g.   `Bhalfdim7` - `B D F A`)
- augmaj7   (e.g.   `Eaugmaj7` - `E G# B# D#`)
- augmin7   (e.g.   `Gaugmin7` - `G B D# F`)
- minmaj7   (e.g.   `Bbminmaj7` - `Bb Db F A`)
- dom9      (e.g.   `Bb9` - `Bb D Ab C`)
- dom7b9    (e.g.   `Bb7b9` - `Bb D Ab Cb`)
- dom13     (e.g.   `Eb13` - `Eb G Db C`)
- dom7b13   (e.g.   `Eb7b13` - `Eb G Db Cb`)
- maj6      (e.g.   `F#6` - `F# A# C# D#`)
- min6      (e.g.   `Cbm6` - `Cb Ebb Gb Ab`)

Chords will always be in their basic stacked order. See above for examples.
You may guess chords by either their chord symbol or their four notes:
`$c guess C6` or `$c guess C E G A`
Please follow the syntax in the examples above when guessing chords.

The possible roots of the chords are all the notes within an octave, up to at most one accidental.
However, keep in mind that some chords may contain notes with up to two accidentals.

Enharmonics are NOT the same. e.g. `F#` and `Gb` are considered different notes.

After each guess, information will be revealed about your guess:

A `codeblocked` note means the note is not in the chord.
A **bolded** note means the note is in the chord, but not in the right spot.
A __**bolded and underlined**__ note means the note is in the chord and in the correct spot.

Type `$c play` to start a new game!
Type `$c guess` followed by a valid 4-note chord to guess chords.
Type `$c show` to show your guesses.
Type `$c quit` to end a game.
"""

CHORD_NAMES = ['maj7','m7','7','dim7','halfdim7','augmaj7','augmin7','minmaj7','9','7b9','13','7b13','6','m6']

client = discord.Client()

def pad(guesses, length, max):
    temp_guesses = guesses.copy()
    for _ in range(max - len(temp_guesses)):
        temp_guesses.append(('` ` ' * length).strip())
    return "\n".join(temp_guesses)

def format_statistics(author, stats, game):
    results = f"""
1 guess:    {stats['1']}
2 guesses:  {stats['2']}
3 guesses:  {stats['3']}
4 guesses:  {stats['4']}
    """

    if game == "w":
        results += f"""
        5 guesses:  {stats['5']}
        6 guesses:  {stats['6']}"""

    results += f"Failed:     {stats['f']}"

    return results

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='$w help'))
    print('{0.user} successfully initiated.'.format(client))
    
    client.w_players = {}
    client.wordlist = [i.strip() for i in open("wordlist.txt", "r").readlines()]

    client.c_players = {}
    chordlist = []
    chord_groups = [i.split("\n") for i in open("chordlist.txt", "r").read().split("\n\n")]
    for c, group in enumerate(chord_groups):
        for d, chord in enumerate(group):
            chordlist.append(chord.split())
            chord_groups[c][d] = chord.split()

    client.chordlist = chordlist
    client.chordgroups = chord_groups

@client.event
async def reset(author, game):
    print("Closing game with", author)
    if game == "CHORDLE":
        del client.c_players[author]
    else:
        del client.w_players[author]

@client.event
async def on_message(message):
    message.content = message.content.lower().strip()

    if message.author == client.user:
        return

    if message.content == '$w':
        await message.channel.send("Hello, I'm WordleBot! Type `$w help` for instructions, or `$w play` to play!")

    if message.content == "$w help":
        await message.channel.send(W_INSTRUCTIONS)

    if message.content == '$w play': #initialize new game
        author = str(message.author).replace(" ", "")
        try:
            p = client.w_players[author]["name"]
        except:
            print("Player:", message.author)
            await message.channel.send(f'Starting a new WORDLE game with {message.author.mention}!\nType `$w guess` followed by your guess to start guessing.')
            client.w_players[author] = {
                "name": author,
                "secret": client.wordlist[randint(0, len(client.wordlist))],
                "guesses": [],
                "available": {
                    "correct": "",
                    "in": "",
                    "remaining": ascii_uppercase
                }
            }
            print("Secret word:", client.w_players[author]["secret"])
        else:
            await message.channel.send(f'You already have an ongoing game, {message.author.mention}.')

    if message.content.startswith("$w guess"):
        author = str(message.author).replace(" ", "")
        try:
            p = client.w_players[author]["name"]
        except:
            await message.channel.send("You do not have a game in progress. Type `$w play` to start one!")
        else:
            guess = message.content[8:].strip().lower()
            print("Player's guess:", guess)
            if len(guess) != 5:
                await message.channel.send("Your guess must be 5 letters long.")
            elif guess not in set(client.wordlist):
                await message.channel.send("Your guess was not found in the wordlist.")
            else:
                result = []
                temp_correct = ""
                temp_in = ""
                for c, i in enumerate(guess):
                    
                    if i == client.w_players[author]["secret"][c]:    #correct
                        result.append(f"**__{i.upper()}__**")
                        client.w_players[author]["available"]["correct"] += i.upper() 
                        client.w_players[author]["available"]["in"] += i.upper()
                        temp_correct += i.upper()
                        temp_in += i.upper()
                    elif i in client.w_players[author]["secret"]:     #in, but not in right spot
                        result.append(f"**{i.upper()}**")
                        client.w_players[author]["available"]["in"] += i.upper()
                        temp_in += i.upper()
                    else:                                                   #wrong
                        result.append(f"`{i.upper()}`")
                    client.w_players[author]["available"]["remaining"] = client.w_players[author]["available"]["remaining"].replace(i.upper(), "")
                    
                    correct_count = temp_correct.count(i.upper())
                    in_count = temp_in.count(i.upper())
                    secret_count = client.w_players[author]["secret"].count(i)

                    if correct_count + in_count > secret_count:
                        to_replace = correct_count + in_count - secret_count
                        replaced = 0
                        for d, j in enumerate(result):
                            if j == f"**{i.upper()}**":
                                result[d] = f"`{i.upper()}`"
                                replaced += 1
                            if replaced >= to_replace:
                                break
                        client.w_players[author]["available"]["in"].replace(i.upper(), "", to_replace)
                
                #remove duplicates
                client.w_players[author]["available"]["correct"] = "".join(sorted(set(client.w_players[author]["available"]["correct"]))) 
                client.w_players[author]["available"]["in"] = "".join(sorted(set(client.w_players[author]["available"]["in"])))         
                
                #print result
                result = " ".join(result)
                client.w_players[author]["guesses"].append(result)
                await message.channel.send(pad(client.w_players[author]["guesses"], 5, 6))
                if guess == client.w_players[author]["secret"]: 
                    await message.channel.send(f"Congratulations, {message.author.mention}, you guessed the word in {len(client.w_players[author]['guesses'])} tries!")
                    await client.update_statistics(author, "w", str(len(client.w_players[author]['guesses'])))
                    await client.reset(author, "WORDLE")
                elif len(client.w_players[author]["guesses"]) == 6:
                    await message.channel.send(f"You ran out of guesses, {message.author.mention}. The word was `{client.w_players[author]['secret']}`. Better luck next time!")
                    await client.update_statistics(author, "w", "f")
                    await client.reset(author, "WORDLE")

    if message.content == "$w available":
        author = str(message.author).replace(" ", "")
        try:
            p = client.w_players[author]["name"]
        except:
            await message.channel.send("You do not have a game in progress. Type `$w play` to start one!")
        else:
            output = "The available letters are:"
            if len(client.w_players[author]["available"]["correct"]) > 0:
                output += f'\n**__CORRECT:__** {" ".join(list(client.w_players[author]["available"]["correct"]))}'
            if len(client.w_players[author]["available"]["in"]) > 0:
                output += f'\n**IN WORD:** {" ".join(list(client.w_players[author]["available"]["in"]))}'
            if len(client.w_players[author]["available"]["remaining"]) > 0:
                output += f'\nNOT GUESSED: {" ".join(list(client.w_players[author]["available"]["remaining"]))}'
            
            await message.channel.send(output)

    if message.content == "$w show":
        author = str(message.author).replace(" ", "")
        try:
            p = client.w_players[author]["name"]
        except:
            await message.channel.send("You do not have a game in progress. Type `$w play` to start one!")
        else:
            await message.channel.send(f'Guesses for {message.author.mention}:\n' + pad(client.w_players[author]["guesses"], 5, 6))

    if message.content == "$w quit":
        author = str(message.author).replace(" ", "")
        try:
            p = client.w_players[author]["name"]
        except:
            await message.channel.send("You do not have a game in progress. Type `$w play` to start one!")
        else:
            await message.channel.send(f'Ending game. The word was `{client.w_players[author]["secret"]}`')
            await client.update_statistics(author, "w", "f")
            await client.reset(author, "WORDLE")

    if message.content == "$w statistics":
        try: 
            f = open("statistics.json", "r")
        except:
            f = open("statistics.json", "w")
            f.close()
            f = open("statistics.json", "r")

        try:
            statistics = json.load(f)
            f.close()
        except:
            statistics = {}

        id_stats = {}
        if id not in statistics:
            id_stats = {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "failed": 0,
            }
            id_stats = format_statistics(id_stats, "w")
        else:
            id_stats = format_statistics(statistics[id]["w"], "w")
        
        await message.channel.send(f"Statistics for {message.author.mention}:\n{id_stats}")

    #CHORDLE
    if message.content == '$c':
        await message.channel.send("Hello, I'm ChordleBot! Type `$c help` for instructions, or `$c play` to play!")

    if message.content == "$c help":
        await message.channel.send(C_INSTRUCTIONS)

    if message.content == '$c play': #initialize new game
        author = str(message.author).replace(" ", "")
        try:
            p = client.c_players[author]["name"]
        except:
            print("Player:", message.author)
            await message.channel.send(f'Starting a new CHORDLE game with {message.author.mention}!\nType `$c guess` followed by your guess to start guessing.')
            client.c_players[author] = {
                "name": author,
                "secret": client.chordlist[randint(0, len(client.chordlist))],
                "guesses": [],
            }
            print("Secret chord:", client.c_players[author]["secret"])
        else:
            await message.channel.send(f'You already have an ongoing game, {message.author.mention}.')

    if message.content.startswith("$c guess"):
        author = str(message.author).replace(" ", "")
        try:
            p = client.c_players[author]["name"]
        except:
            await message.channel.send("You do not have a game in progress. Type `$c play` to start one!")
        else:
            guess = message.content[8:].strip()
            if " " not in guess:
                guess_quality = guess.capitalize()
                guess_root = ""
                s = 1
                if guess_quality[1] in "#b":
                    s = 2
                guess_root = guess_quality[:s]
                guess_quality = guess_quality[s:]
                try:
                    i = CHORD_NAMES.index(guess_quality)
                except:
                    await message.channel.send("Your guess was not found in the chordlist.")
                    return
                else:
                    i = CHORD_NAMES.index(guess_quality)
                    for j in client.chordgroups[i]:
                        if j[0] == guess_root:
                            guess = j
                            break
            else:
                guess = [i.capitalize() for i in guess.split()]
            print("Player's guess:", guess)
            if len(guess) != 4:
                await message.channel.send("Your guess must be 4 notes long.")
            elif guess not in client.chordlist:
                await message.channel.send("Your guess was not found in the chordlist.")
            else:
                result = []
                for c, i in enumerate(guess):
                    if i == client.c_players[author]["secret"][c]:          #correct
                        result.append(f"**__{i}__**")
                    elif i in client.c_players[author]["secret"]:           #in, but not in right spot
                        result.append(f"**{i}**")
                    else:                                                   #wrong
                        result.append(f"`{i}`")

                #print result
                result = " ".join(result)
                client.c_players[author]["guesses"].append(result)
                await message.channel.send(pad(client.c_players[author]["guesses"], 4, 4))
                if guess == client.c_players[author]["secret"]: 
                    await message.channel.send(f"Congratulations, {message.author.mention}, you guessed the chord in {len(client.c_players[author]['guesses'])} tries!")
                    await client.update_statistics(author, "c", str(len(client.c_players[author]['guesses'])))
                    await client.reset(author, "CHORDLE")
                elif len(client.c_players[author]["guesses"]) == 4:
                    secret = client.c_players[author]['secret']
                    for c, i in enumerate(client.chordgroups):
                        for j in i:
                            if j == client.c_players[author]['secret']:
                                secret = secret[0] + CHORD_NAMES[c] + f" - {' '.join(secret)}"
                                break
                    await message.channel.send(f"You ran out of guesses, {message.author.mention}. The chord was `{secret}`. Better luck next time!")
                    await client.update_statistics(author, "c", "f")
                    await client.reset(author, "CHORDLE")

    if message.content == "$c show":
        author = str(message.author).replace(" ", "")
        try:
            p = client.c_players[author]["name"]
        except:
            await message.channel.send("You do not have a game in progress. Type `$c play` to start one!")
        else:
            await message.channel.send(f'Guesses for {message.author.mention}:\n' + pad(client.c_players[author]["guesses"], 4, 4))

    if message.content == "$c quit":
        author = str(message.author).replace(" ", "")
        try:
            p = client.c_players[author]["name"]
        except:
            await message.channel.send("You do not have a game in progress. Type `$c play` to start one!")
        else:
            secret = client.c_players[author]['secret']
            for c, i in enumerate(client.chordgroups):
                for j in i:
                    if j == client.c_players[author]['secret']:
                        secret = secret[0] + CHORD_NAMES[c] + f" - {' '.join(secret)}"
                        break
            await message.channel.send(f'Ending game. The chord was `{secret}`')
            await client.update_statistics(author, "c", "f")
            await client.reset(author, "CHORDLE")
    
    if message.content == "$w statistics":
        try: 
            f = open("statistics.json", "r")
        except:
            f = open("statistics.json", "w")
            f.close()
            f = open("statistics.json", "r")

        try:
            statistics = json.load(f)
            f.close()
        except:
            statistics = {}

        id_stats = {}
        if id not in statistics:
            id_stats = {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "failed": 0,
            }
            id_stats = format_statistics(id_stats, "c")
        else:
            id_stats = format_statistics(statistics[id]["c"], "c")
        
        await message.channel.send(f"Statistics for {message.author.mention}:\n{id_stats}")

@client.event
async def update_statistics(id, game, guesses):
    try: 
        f = open("statistics.json", "r")
    except:
        f = open("statistics.json", "w")
        f.close()
        f = open("statistics.json", "r")

    try:
        stats = json.load(f)
        f.close()
    except:
        stats = {}

    if id not in stats:
        stats[id] = {
            "w": {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "f": 0,
            },
            "c": {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "f": 0,
            }
        }

    stats[id][game][guesses] += 1

    with open("statistics.json", "w") as out:
        out.write(json.dumps(stats, indent=4))
        out.close()
        
client.run(os.environ["DISCORD_TOKEN"])