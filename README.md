# chwordle-bot

A simple Discord bot that allows users to play Wordle and Chordle!

## [Invite the bot](https://discord.com/api/oauth2/authorize?client_id=945329906739458098&permissions=274877910016&scope=bot)

### Wordle
Based on [Wordle](https://www.nytimes.com/games/wordle/index.html)
- Official Wordle wordlist (2300+ possible secret words, 12000+ total words to guess from)
- Possible secret words are more common words with no plurals
- Detailed game statistics using `$w available`

### Chordle
Based on [Chordle](https://www.chordle.synthase.cc/)
- 250+ 7th, 9th, 13th, and 6th chords
- 7th chords
  - maj7
  - min7
  - dom7
  - dim7
  - halfdim7
  - augmaj7
  - augmin7
  - minmaj7
- 9th chords
  - dom9
  - dom7b9
- 13th chords
  - dom9
  - dom7b9
- 6th chords
  - maj6
  - min6
- Accurate note spelling
- Players can guess chords by their symbol `e.g. Dbmaj7` or by their notes `Db F Ab C`

## Full list of commands

| Command       | Description   |
| ------------- | ------------- |
| `$w help`     | Show WORDLE instructions  |
| `$w play`     | Start a WORDLE game  |
| `$w guess [guess]` | Guess a 5-letter word |
| `$w show`     | Show player's guesses |
| `$w available` | Show correct and not guessed letters |
| `$w quit` | End WORDLE game |
| `$w statistics` | Show WORDLE game statistics |
| ------------- | ------------- |
| `$c help`     | Show CHORDLE instructions  |
| `$c play`     | Start a CHORDLE game  |
| `$c guess [guess]` | Guess a 4-note chord |
| `$c show`     | Show player's guesses |
| `$c quit` | End CHORDLE game |
| `$w statistics` | Show CHORDLE game statistics |
