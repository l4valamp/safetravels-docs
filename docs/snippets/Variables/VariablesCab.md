
#### Suspension

| Name                                                                     | Comments               | Default |
| ------------------------------------------------------------------------ | ---------------------- | ------- |
| {{!SpringStrength:float:Cab,  Suspension:"Suspension spring stiffness"}} | Spring Stiffness       |         |
| {{!SpringDamping:float:Cab, Suspension:"Shock Damping"}}                 | Shock Damping          |         |
| {{!MaxSuspensionCompression:float:Cab, Suspension:"Maximum Travel"}}     | Maximum Travel         |         |
| {{!RestSuspensionLength:float:Cab, Suspension:"Normal Wheel Extension"}} | Normal Wheel Extension |         |
| {{!SnowSinkAmount:float:Cab, Suspension:"Snow Compression"}}             | Snow Compression       |         |
| {{!SuspensionTraceDistance:float:Cab, Suspension:"Raycast Length"}}      | Raycast Length         |         |

#### Fixed Timestep Variables
| Name                                                                     | Comments                   | Default  |
| ------------------------------------------------------------------------ | -------------------------- | -------- |
| {{!PhysicsAccumulator:float:Cab, Timestep:"Stores leftover frame time"}} | Stores leftover frame time |          |
| {{!FixedDelta:float:Cab, Timestep:"Physics step size"}}                  | Physics step size          | 0.016666 |
| {{!MaxPhysicsSteps:int:Cab, Timestep:"Prevents Infinite Loops"}}         | Prevents Infinite Loops    |          |
| {{!PhysicsStepsThisFrame:int:Cab, Timestep:"Debug Counter"}}             | Debug Counter              |          |

#### Cab Physics State Variables (Replacing Chaos rigid body state)
| Name                                                                                    | Comments                                   | Default |
| --------------------------------------------------------------------------------------- | ------------------------------------------ | ------- |
| {{!CabVelocity:vector:Cab, PhysicsState:"No sideways or vertical movement"}}            | No sideways or vertical movement           |         |
| {{!CabAngularVelocity:vector:Cab, PhysicsState:"Rotational speed"}}                     | Rotational speed                           |         |
| {{!CabPosition:vector:Cab, PhysicsState:"Actor Location"}}                              | Actor Location                             |         |
| {{!CabRotation:rotator:Cab, PhysicsState:"Using Quarternion "to avoid gimbal issues""}} | Using Quarternion "to avoid gimbal issues" |         |
| {{!CabAcceleration:vector:Cab, PhysicsState:"Current calculated forward acceleration"}} | Current calculated acceleration            |         |
| {{!CabAngularAcceleration:vector:Cab, PhysicsState:""}}                                 |                                            |         |
| {{!CabMass:float:Cab, PhysicsState:"Cab mass (kg)"}}                                    | Cab mass (kg)                              |         |
| {{!CabCenterOfMass:vector:Cab, PhysicsState:""}}                                        |                                            |         |
