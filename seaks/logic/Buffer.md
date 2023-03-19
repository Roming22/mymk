# Scenario

X.sY: switch Y pressed while layer X is active
!sY: switch Y released
tsY: tap timer for switch Y timed out
csY: chord timer for switchY timed out

Ideas:
    - multiple buffers: one for non-processed inputs, one (or more?) for on-going (pressed) inputs.

## Layer0 keys
["0.s1"] -> KC.A (press), ["!s1"] -> KC.A (release)

## Layer0 TapHold
["0.s1","!s1"] -> KC.A (oneshot)
["0.s1","t.s1"] -> KC.B (press), ["!s1"] -> KC.B (release)

## Layer0 Chord
["0.s2","!s2"] -> KC.C (oneshot)
["0.s2","cs2!"] -> KC.C (press), ["s2"] -> KC.C (release)
["0.S3","!s3"] -> KC.D (oneshot)
["0.s3","cs3!"] -> KC.D (press), ["s3"] -> KC.D (release)
["0.s2","0.s3"],["0.s3","0.s2"] -> KC.E (press), ["!s2"], ["!s3"] -> KC.E (released), timer reset.

## Tap key repeats when first key is held
Chord can be retriggered if released key is pressed again before "cs2" or  "cs3", but only that chord.
That means event for the switches involved in the combo get routed only to that buffer, but only as long as the timer has not timed out?

## Layer0 Sequence
["0.s4"] -> KC.F (press), ["!s4"] -> KC.F (release)
["0.s5"] -> KC.G (press), ["!s5"] -> KC.G (release)
["0.s4","0.s5"] -> KC.H (press)
["0.s5","0.s4"] -> KC.I (press)

## Layer1 keys
["0.s6","!s6"] -> Switch to layer 1 (oneshot?)
["0.s7"] -> Switch to layer 1 (press?), ["!s7"] revert to previous layer (release?) if layer is active (can be delayed if multiple layers are stacked)

## Layer1 is ignored if key1 is released before key2 is released and layer is not engaged by hold
["0.s1"] -> KC.A (press), ["!s1"] -> KC.A (release)
["1.s1"] -> KC.J (press), ["!s1"] -> KC.J (release)
["0.s7","1.s1","!s7","!s1"] -> KC.A
["0.s7","1.s1","!s1","!s7"] -> KC.J
["0.s7","1.s1","ts7","!s7","!s1"] -> KC.J

## Switching layer while pressing a (mod?) key keeps the key pressed until the the key is released
["0.s8"] -> KC.LSHIFT (press), ["!s8"] -> KC.LSHIFT (release)
["0.s8","0.s7","1.s1","!s1","!s8","1.s1","!s1","!s7"] -> "Jj"
["0.s8","0.s7","1.s1","!s1","!s7","1.s1","!s1","!s8"] -> "JA"

## Layer transparency
["0.s1"] -> KC.A (press), ["!s1"] -> KC.A (release)
["2.s1"] -> KC.TRNS -> KC.A (press) if coming from layer0, KC.J (press) if coming from layer1.
