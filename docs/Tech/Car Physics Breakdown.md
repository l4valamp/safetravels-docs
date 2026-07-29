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
	|        | Spring Stiffness       |         |
	| {{SpringDamping:float}}            | Shock Damping          |         |
	| {{MaxSuspensionCompression:float}} | Maximum Travel         |         |
	| {{RestSuspensionLength:float}}     | Normal Wheel Extension |         |
	| {{SnowSinkAmount:float}}           | Snow Compression       |         |
	| {{SuspensionTraceDistance:float}}  | Raycast Length         |         |
=== "Force Accumulators (In Vehicle BP)"
	
	### Force Accumulators
	
	--8<-- "./docs/snippets/CabVariablesAccumulators.md"
***

### Replacing AddForceAtLocation()

**ApplyForceAtPoint({{Force:vector:f}}, {{WheelLocation:vector:f}})**. 

Each wheel calls this. After each wheels has updated the {{TotalForce:vector}} and {{TotalTorque:vector}} of the **cab**, the **Cab** can integrate it into motion. 

*  {{TotalForce:vector}} += {{Force:vector:f}}
* {{LeverArm:vector:l}} = {{WheelLocation:vector:f}} - {{CenterOfMassWorld:vector}}
* {{Torque:vector:l}} = CrossProduct({{LeverArm:vector:l}}, {{Force:vector:f}})
* {{TotalTorque:vector}} += {{Torque:vector:l}}

**Linear Motion**

* {{Acceleration:vector}} = {{TotalForce:vector}} / {{VehicleMass:float}}
* {{VehicleVelocity:vector}} += {{Acceleration:vector}} * {{FixedDelta:float}}

**Rotational Motion**

* {{AngularAcceleration:vector}} = {{TotalTorque:vector}} / {{MomentOfInertia:vector}} 
* {{AngularVelocity:vector}} += {{AngularAcceleration}} * {{FixedDelta:float}}

### Because we can't use GetVelocityAtPoint() Without Chaos, we need to replace it. 

#### GetVelocityAtPoint({{WorldPosition:vector:f}}) (Owned by Wheel Comp)

* {{Offset:vector:l}} = {{WorldPosition:vector:f}} - {{CenterOfMassWorld:vector}}
* {{RotationalVelocity:vector:l}} = CrossProduct({{AngularVelocity:vector}}, {{Offset:vector}})
* Return {{VehicleVelocity:vector}} + {{RotationalVelocity:vector:l}}


