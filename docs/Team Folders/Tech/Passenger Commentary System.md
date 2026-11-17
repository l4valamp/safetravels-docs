---
tags:
  - page
Categories: Tech
header image url: https://bugsblog.neocities.org/cabbypics/tech/Screenshot%202026-11-15%20175917.png
---

# Passenger Commentary System Breakdown

## Resources and References

## Notes

**Passenger Commentary** is all passenger dialogue spurred as a reaction to **How** or **Where** the player is driving, excluding Instructions and Babble (to keep the focus clear). 

This happens in 3 stages:
- Triggering: BPC_DrivingTelemetry detects an event and triggers a dispatch
- Evaluation: BPC_PassengerDialogue checks Dialogue Data-Table row conditions against the current driving state
- Selection: ??? Selects and queues dialogue for playback. 

#### Triggering:
- Takes place in BPC_DrivingTelemetry (Attached to BP_Player).
- On tick, BP_Player calls BPC_DrivingTelemetry's "Sample Driving" 
- **Sample Driving Does:**
	- Gets Seconds Elapsed Since Last Tick
	- Makes Sure It Isn't Being Called Twice
	- Uses Elapsed Seconds, Forward Vector, and Velocity to calculate:
		- Forward Acceleration
		- Forward Speed
		- Yaw Rate
		- Last Yaw
		- Lateral Speed
		- Speed
	- Calls "Read Cab Road Contact":
		- Checks if each wheel is touching asphalt (Passenger road contact int value set when wheel determines its own surface material.) Returns 1(asphalt), 2(other), or 0 (for null)
	- Calls "Update Manuevers":
		- Currently Disconnected, updates Brake Active nad Brake Time, potentially calls **Harsh Braking (Qualified) Driving Event**. 
		- Uses Forward Speed, Min Maneuver Speed, Forward Acceleration, Brake Threshold. 
	- Calls "Update Swerve"
		- Not for Swerve detection, for turning off the swerve after swerve window. 
	- Calls "Track Lateral Direction"
		- Detects Swerves, calls **Swerve (Qualified) Driving Event**.
	- If Road Contact is VALID...
	- Call "UpdateOffRoad"
		- If OffRoad is Active, and wasn't before, set OffRoadStarted game time, OffRoad to true, and **OffRoad (Started) Driving Event**. (No Duration or Severity)
		- If OffRoad is Not Active, and it was before, calculate the total time spent off road, set OffRoad to false, then **Call OffRoad (Ended) Driving Event**. (With Duration this time).
	- Call "UpdateStopped" - Structured Similarly to "Update Off Road"
		- Either calls **Stopped (Started) Driving Event**. (Only Timestamp)
		- Or calls **Stopped (Ended) Driving Event**. (Timestamp + Duration)
	- Call "Update Trip Off Road Stop"
		- Sets how many times the player has been offroad and stopped this trip.
	- Call "Publish Passenger Duration"
		- Calls **DrivingState Update Driving Event**. (Just timestamped)
		- This calls every .2 seconds and tells the passenger to check all of the values in BPC_Telemetry itself.
