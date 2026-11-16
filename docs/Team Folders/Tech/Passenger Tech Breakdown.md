---
tags:
  - page
Categories: Tech
header image url: https://bugsblog.neocities.org/cabbypics/tech/ezgif.com-speed_2.gif
---

# Passenger Tech Breakdown

## Resources and References

## Notes

#### Dialogue:
**There are a few major types of passenger dialogue:**

**Instructions:** Reacting to the player's previous turn (Reaction), and telling them where to go next (Directions). 
- **Directions** are determined using the [[Route Navigation]] system, which finds the shortest path between the player's current road segment and the passenger's desired stop. Passengers may have specific conditions that alter which routes they want to take.
- Instructions can be formulaic, and usually contain:
```
[Response to previous turn] [Directions for the next turn]
```

**Commentary:** Reacting to the player's driving or the current location. 
- The commentary system is the most complicated. It is covered in [[Passenger Commentary System]]

**Babble:** Miscellaneous, rambling, or random dialogue thrown in (if the passenger is feeling chatty).