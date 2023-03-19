# TODO

## Getting Started
[X] Automate project deployment
[X] Physical keyboard definition
[X] Detect and log keypress events

## State-Event-Action
[X] Create State object
[X] Create Event object
[X] Link Events to State
[X] Generate an Event on key press
[X] Event is sent to State to be processed
[X] Create Action object
[X] Link Action to an Event
[X] Link Action to next State
[X] Add Timer
[ ] Add TapHold support
[ ] Add combo key for 2 keys
[ ] Add combo keys for n keys

## Layout definition
[X] Alpha layer single key chars
[ ] Alpha layer Mod keys
[X] Alpha layer Fn keys
[ ] Alpha layer lock Fn
[ ] Alpha layer combo key chars
[ ] Caps Word

## Tests
[ ] Layer0 keys
[ ] Layer0 TapHold
[ ] Layer0 Chord
    [ ] Chord activates
    [ ] Tap key repeats when first key is held
[ ] Layer0 Sequence
[ ] Layer1 keys
    [ ] Layer1 is ignored if key1 is released before key2 is released.
    [ ] Switching layer while pressing a (mod?) key keeps the key pressed until the the key is released.

## Known bugs
[ ] Switching layers while holding a key does not release the key when the key is released
[ ] Chords do not release

## LEDs
[ ] Turn LEDs on
[ ] Change colors based on active layer

## YAML config
[ ] Move board configuration to YAML
[ ] Move keymap configuration to YAML
