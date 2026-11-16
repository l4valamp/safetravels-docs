---
Categories: "[[Tech]]"
tags:
  - "#category"
  - teampage
---

### Major Systems:

**PRIORITY 1 (MVP):**
- **[[Car Controller]]**
	- A customizable realistic car that is fun to drive and intuitive to control. Interacts with physics, much is controlled in the wheels. The car must detect crashes and damage, be reactive to ground friction, and give off appropriate VFX. The values that control the car's game feel must be exposed to dev settings. The car must be the appropriate size. 
- **[[Road Logic]]**
	- Designers must be able to place road splines handle everything. Roads must be able to detect intersections with each other and segment their own data automatically. Roads must be set default sizes. Roads must have additional customization and decals built-in. Roads must have lanes. Roads segments could have their own persistent identities (requires editor tool?)
- **[[Route Navigation]]**
	- A GPS system that can give the player instructions from where they are to their target destination. This system may be able to filter out certain roads based on conditions (closures, avoiding certain neighborhoods, avoiding left-turns, etc.). Relies on Road Registration breaking road splines down into a workable structure of nodes and edges.
- [[Passenger Commentary System Breakdown]]
	- Possibly the biggest system. Passengers must detect how and where you are driving, analyze their dialogue options, and queue them properly. 
- **[[Arcade Mode]]**
	- Infinite game mode that randomly selects passengers and routes on a timer. Ignores persistent plot-related flags or passenger memory. Used for testing and keeping game-systems separate from hard-coded progression systems.

**PRIORITY 2:**
- **[[Story Mode]]**
	- Story (Core) game mode with persistent memory and pre-authored order of passengers and events. 
- **[[Saving and Loading]]**
	- Money can be used at auto-body shops to save progress. Gives players control, but can't abuse save-scumming. Passengers can use bribes to get the player to do immoral or dangerous things. 

PRIORITY 3:
- **[[AI Cars]]**
	- Cars on the road that drive naturally, detect intersections, handle traffic themselves. Requires more in-depth handling with the roads. (Lanes, intersection collision boxes).
- **[[NPC People]]**
	- People on the sides of the road (waiting to get picked up, walking down the streeth) that react naturally to being hit by the car. Have minimal pathing logic. 
- **[[Time of Day and Weather]]**
	- Time of day clock on a timer. Gradually lerps between lighting conditions. Requires artist pass. Weather conditions on a similar manager system (Rain, fog, overcast, wind). We could lerp between different data assets that layer on top of the time of day.

***

### Tech pages
![[pages.base#ByCategory]]
