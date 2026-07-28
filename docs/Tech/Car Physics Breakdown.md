!!! warning
	Avoid putting physics in Event Tick using Delta Seconds. Add an accumulator. 



### Blueprint-Only Physics Best Practices

##### Fixed Accumulator




##### Avoid Relying on a Chaos Physics Body
Even if using an accumulator, Chaos does not update its physics in time with our Blueprint tick-based fixed step. **Add Force** integrates Chaos physics, so we should avoid it.

* Keep vehicle-wide suspension tuning on the car actor
* Keep per-wheel runtime state inside each wheel component
* Keep per-wheel configuration inside each wheel component only when it is unique
### Maintaining Vehicle State Separately

```
BP_CustomVehicle (Actor)
│
├── Vehicle Physics State
│
├── Vehicle Suspension Settings
│
├── Vehicle Tire Settings
│
├── Surface Data
│
├── Input State
│
└── Wheel Components
        │
        ├── Wheel_FL Component
        ├── Wheel_FR Component
        ├── Wheel_RL Component
        └── Wheel_RR Component
        
        
        
        ```
FixedPhysicsStep()

    Clear TotalForce
    Clear TotalTorque

    For each WheelComponent:

        Wheel.CalculateSuspension()

        Wheel.CalculateFriction()

        Wheel.CalculateDriveForce()

        Add forces to vehicle


    Calculate Drag

    Calculate Downforce

    Integrate Velocity

    Integrate Position

    Integrate Rotation

    SetActorTransform()
```




***
=== "Description"
	!!! note
		Variables have been sorted into Wheel Component, Vehicle BP, and Force Accumulators.
=== "Wheel Component"
	### Wheel Component Variables
	
	#### Wheel ID Variables
	| Name                    | Comments              | Default |
	| ----------------------- | --------------------- | ------- |
	| {{WheelName:name}}      |                       |         |
	| {{WheelIndex:int}}      |                       |         |
	| {{bSteeringWheel:bool}} | can steer             |         |
	| {{bDriveWheel:bool}}    | Receives engine power |         |
	| {{bBrakeWheel:bool}}    | Receives brakes       |         |
	
	#### Wheel Transform Variables
	| Name                              | Comments | Default |
	| --------------------------------- | -------- | ------- |
	| {{WheelMountTransform:transform}} |          |         |
	| {{WheelContactPoint:vector}}      |          |         |
	| {{WheelForwardDirection:vector}}  |          |         |
	| {{WheelRightDirection:vector}}    |          |         |
	| {{WheelUpDirection:vector}}       |          |         |
	
	#### Wheel Suspension Runtime Variables
	
	| Name                            | Comments             |Default |
	| ------------------------------- | -------------------- | ------- |
	| {{SuspensionCompression:float}} | Current Compression  |         |
	| {{SuspensionVelocity:float}}    | Compression Speed    |         |
	| {{SuspensionForce:float}}       | Current Spring Force |         |
	| {{bGrounded:bool}}              | Ground Contact       |         |
	| {{GroundHit}}                   | Trace Result         |         |
	| {{GroundNormal:vector}}         | Surface Normal       |         |
	| {{ContactPoint:vector}}         | Ray hit point        |         |
	| {{ContactTag:name}}             | Surface type         |         |
	
	#### Wheel Other Runtime Variables
	| Name                       | Comments | Default |
	| -------------------------- | -------- | ------- |
	| {{WheelVelocity:vector}}   |          |         |
	| {{ForwardVelocity:vector}} |          |         |
	| {{LateralVelocity:vector}} |          |         |
	| {{SlipAmount:float}}       |          |         |
	| {{WheelSpinAmount:float}}  |          |         |
	| {{CurrentFriction:float}}  |          |         |
	| {{MaxFrictionForce:float}} |          |         |
	| {{SlideAmount:float}}      |          |         |
=== "Vehicle BP Variables"
	### Vehicle BP Variables
	
	#### Fixed Timestep Variables
	| Name                          | Comments                   | Default  |
	| ----------------------------- | -------------------------- | -------- |
	| {{PhysicsAccumulator:float}}  | Stores leftover frame time |          |
	| {{FixedDeltaTime:float}}      | Physics step size          | 0.016666 |
	| {{MaxPhysicsSteps:int}}       | Prevents Infinite Loops    |          |
	| {{PhysicsStepsThisFrame:int}} | Debug Counter              |          |
	
	#### Vehicle Physics State Variables (Replacing Chaos rigid body state)
	| Name                                  | Comments                                   | Default |
	| ------------------------------------- | ------------------------------------------ | ------- |
	| {{VehicleVelocity:vector}}            | No sideways or vertical movement           |         |
	| {{VehicleAngularVelocity:vector}}     | Rotational speed                           |         |
	| {{VehiclePosition:vector}}            | Actor Location                             |         |
	| {{VehicleRotation:rotator}}           | Using Quarternion "to avoid gimbal issues" |         |
	| {{VehicleAcceleration:vector}}        | Current calculated acceleration            |         |
	| {{VehicleAngularAcceleration:vector}} |                                            |         |
	| {{VehicleMass:float}}                 | Vehicle mass (kg)                          |         |
	| {{CenterOfMass:vector}}               |                                            |         |
	
	#### Vehicle Suspension Variables
	
	| Name                               | Comments               | Default |
	| ---------------------------------- | ---------------------- | ------- |
	| {{SpringStrength:float}}           | Spring Stiffness       |         |
	| {{SpringDamping:float}}            | Shock Damping          |         |
	| {{MaxSuspensionCompression:float}} | Maximum Travel         |         |
	| {{RestSuspensionLength:float}}     | Normal Wheel Extension |         |
	| {{SnowSinkAmount:float}}           | Snow Compression       |         |
	| {{SuspensionTraceDistance:float}}  | Raycast Length         |         |
=== "Force Accumulators"
	
	### Force Accumulators
	
	Instead of adding force at location on the rigid body. we add to force values and use those to change location and rotation. 
	
	| Name                       | Comments | Default |
	| -------------------------- | -------- | ------- |
	| {{TotalForce:vector}}      |          |         |
	| {{TotalTorque:vector}}     |          |         |
	| {{EngineForce:vector}}     |          |         |
	| {{BrakeForce:vector}}      |          |         |
	| {{SuspensionForce:vector}} |          |         |
	| {{TireForce:vector}}       |          |         |
	| {{DragForce:vector}}       |          |         |
	| {{DownForce:vector}}       |          |         |
	
	
	#### Engine/Drive
	
	| Name                      | Comments | Default |
	| ------------------------- | -------- | ------- |
	| {{MaxDrivePower:float}}   |          |         |
	| {{DrivePowerScale:float}} |          |         |
	| {{MaxSpeed:float}}        |          |         |
	| {{MaxSpeedScale:float}}   |          |         |
	| {{PowerCurve:curvefloat}} |          |         |
	
	
	#### Braking
	
	| Name                        | Comments | Default |
	| --------------------------- | -------- | ------- |
	| {{bBraking:bool}}           |          |         |
	| {{BrakeInput:float}}        |          |         |
	| {{DecelerationForce:float}} |          |         |
	| {{BrakeStrength:float}}     |          |         |
	
	#### Steering
	
	| Name                           | Comments | Default |
	| ------------------------------ | -------- | ------- |
	| {{SteeringInput:float}}        |          |         |
	| {{CurrentSteeringAngle:float}} |          |         |
	| {{MaxSteeringAngle:float}}     |          |         |
	| {{SteeringSensitivity:float}}  |          |         |
	| {{SteeringSpeed:float}}        |          |         |
	
	#### Air Control
	
	
	| Name                         | Comments | Default |
	| ---------------------------- | -------- | ------- |
	| {{AirControlStrength:float}} |          |         |
	| {{AirPitchInput:float}}      |          |         |
	| {{AirYawInput:float}}        |          |         |
	| {{AirTime:float}}            |          |         |
	| {{bAirborne:bool}}           |          |         |
	
	#### RigidBody/Sleeping
	
	| Name                     | Comments | Default |
	| ------------------------ | -------- | ------- |
	| {{FreezeTimer:float}}    |          |         |
	| {{FreezeDelay:float}}    |          |         |
	| {{bFrozen:bool}}         |          |         |
	| {{bFreezeRotation:bool}} |          |         |
	
	#### Surface Data Struct
	| Name                        | Comments | Default |
	| --------------------------- | -------- | ------- |
	| {{SurfaceTag:name}}         |          |         |
	| {{FrictionScale:float}}     |          |         |
	| {{DrivePowerScale:float}}   |          |         |
	| {{SpeedLimitScale:float}}   |          |         |
	| {{bEnforceSpeedLimit:bool}} |          |         |

***

| Name | Comments | Default |
| ---- | -------- | ------- |
|      |          |         |
|      |          |         |

| Name | Comments | Default |
| ---- | -------- | ------- |
|      |          |         |
|      |          |         |
