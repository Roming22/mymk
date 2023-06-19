# TODO

## State-Event-Action
[X] Add Timer
[X] Add TapHold support
[ ] Add MultiTap support
[X] Add combo key for 2 keys
[X] Add combo keys for n keys
[X] Add Layer support

## Layout definition
[X] Alpha layer single key chars
[X] Alpha layer Mod keys
[X] Alpha layer Fn keys
[X] Alpha layer lock Fn
[X] Alpha layer combo key chars
[ ] Caps Word

## Tests
[X] Layer0 keys
[X] Layer0 TapHold
[X] Layer0 Chord
    [X] Chord activates
    [ ] Tap key repeats when first key is held
[X] Layer0 Sequence
[ ] Chords/Sequences can be repeated by pressing/releasing a key (any or just the last?) of the sequence fast enough.
[X] Layer1 keys
[X] Keys remained pressed when switching layer as long as they are held

## Hardware
[X] Turn LEDs on
[X] Change colors based on active layer
[ ] Split keyboard communication
    [X] Detect Left/Right board in case of split keyboard
    [ ] Send power to Extension board
    [?] Detect Controller/Extension board
    [X] Implement and execute Extension loop
    [ ] Send switch event over the wire
    [ ] Send leds event over the wire

# General improvements
[ ] Use supervisor.runtime.serial connected to dynamically remove print/memory/fps info

## Known bugs
