---
tags:
  - page
Categories: "Tech"
header image url: "https://bugsblog.neocities.org/cabbypics/Screenshot%202026-07-22%20223828.png"
---

- A passenger class is a child of BP_PassengerBase
- Each passenger has BPC_Passengerbrain. This listens to the player's BPC_NavData.
- The google sheets are converted to Data Tables
- The dialogue has lines with spots for Generic keys to be replaced
	- Directions
	- Location

- Passengers should react when:
- You turn a corner
- You pick them up
- You drop them off
- You drive off road

At a more advanced level, passengers should react when:
- You drive off road multiple times
- You slow down 
- You hit something
- You make several strings of wrong turns. 
- You're driving slowly compared to a countdown, making them late. 
- You're driving them through an area they have big feelings about.
- You've driven past the same juncture or landmark too many times.

This system needs to be flexible. That means:
- No set number of responses for any one thing
	- If one passenger responds to a very specific stimuli or landmark, we don't need a slot for every passenger to respond to that thing.
- Dialogue can be formatted in generic "chunks" instead of individual lines each anticipated statement. (Directions, attitude, specific roads and landmarks can be flexible)
- Dialogue can be overridden in Blueprints.
	- EX: We can write crude substitutes for specific road names. 



PASSENGER DIALOGUE:

Dialogue can "Unfold" using curly brackets and keywords. 

**EX:**
```
Wrong turn, but that's okay. Just {Directions}.
```

**and then in blueprints we set directions to:**
```
{Angle} onto {Road}. 
```

We can calculate the angle(Direction (Left, Right, Straight, Back)), and find the name of the road in Blueprints and input it. 

We can also optionally check for override text values from the data table? This could be expensive. 



