
#### Suspension

| Name                                                                  | Comments               | Default |
| --------------------------------------------------------------------- | ---------------------- | ------- |
| {{!SpringStrength:float:CabSuspension:"Suspension spring stiffness"}} | Spring Stiffness       |         |
| {{!SpringDamping:float:CabSuspension:"Desc Hahaha"}}                  | Shock Damping          |         |
| {{MaxSuspensionCompression:float}}                                    | Maximum Travel         |         |
| {{RestSuspensionLength:float}}                                        | Normal Wheel Extension |         |
| {{SnowSinkAmount:float}}                                              | Snow Compression       |         |
| {{SuspensionTraceDistance:float}}                                     | Raycast Length         |         |

{{SpringStrength:float:thing}} {{SpringStrength:float}}


| Name                                                                     | Comments                                     | Default |     |
| ------------------------------------------------------------------------ | -------------------------------------------- | ------- | --- |
| {{!TotalForce:vector:Cab, Force Accumulators:"Description blah blah"}}   |                                              |         |     |
| {{!TotalTorque:vector: Cab, Force Accumulators:"total torque to apply"}} | Force Accumulators:"Total Torque To Apply"}} |         |     |
| {{EngineForce:vector}}                                                   |                                              |         |     |
| {{BrakeForce:vector}}                                                    |                                              |         |     |
| {{SuspensionForce:vector}}                                               |                                              |         |     |
| {{TireForce:vector}}                                                     |                                              |         |     |
| {{DragForce:vector}}                                                     |                                              |         |     |
| {{DownForce:vector}}                                                     |                                              |         |     |


#### Engine/Drive

| Name                      | Comments | Default |
| ------------------------- | -------- | ------- |
| {{MaxDrivePower:float}}   |          |         |
| {{DrivePowerScale:float}} |          |         |
| {{MaxSpeed:float}}        |          |         |
| {{MaxSpeedScale:float}}   |          |         |
| {{PowerCurve:curvefloat}} |          |         |


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
