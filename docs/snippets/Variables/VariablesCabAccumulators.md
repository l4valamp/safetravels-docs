
#### Force Accumulators

| Name                                                                     | Comments | Default |     |
| ------------------------------------------------------------------------ | -------- | ------- | --- |
| {{!TotalForce:vector:Cab, Force Accumulators:""}}                        |          |         |     |
| {{!TotalTorque:vector: Cab, Force Accumulators:"Total torque to apply"}} |          |         |     |
| {{!EngineForce:vector:Cab, Force Accumulators:""}}                       |          |         |     |
| {{!BrakeForce:vector:Cab, Force Accumulators:""}}                        |          |         |     |
| {{!SuspensionForce:vector:Cab, Force Accumulators:""}}                   |          |         |     |
| {{!FrictionForce:vector:Cab, Force Accumulators:""}}                     |          |         |     |
| {{!DragForce:vector:Cab, Force Accumulators:""}}                         |          |         |     |
| {{!DownForce:vector:Cab, Force Accumulators:""}}                         |          |         |     |


#### Engine/Drive

| Name                                      | Comments | Default |
| ----------------------------------------- | -------- | ------- |
| {{!MaxDrivePower:float:Cab, Engine:""}}   |          |         |
| {{!DrivePowerScale:float:Cab, Engine:""}} |          |         |
| {{!MaxSpeed:float:Cab, Engine:""}}        |          |         |
| {{!MaxSpeedScale:float:Cab, Engine:""}}   |          |         |
| {{!PowerCurve:curvefloat:Cab, Engine:""}} |          |         |

#### Deceleration

| Name                                              | Comments | Default |
| ------------------------------------------------- | -------- | ------- |
| {{!bBraking:bool:Cab, Deceleration:""}}           |          |         |
| {{!BrakeInput:float:Cab, Deceleration:""}}        |          |         |
| {{!DecelerationForce:float:Cab, Deceleration:""}} |          |         |
| {{!BrakeStrength:float:Cab, Deceleration:""}}     |          |         |

#### Steering

| Name                                             | Comments | Default |
| ------------------------------------------------ | -------- | ------- |
| {{!SteeringInput:float:Cab, Steering:""}}        |          |         |
| {{!CurrentSteeringAngle:float:Cab, Steering:""}} |          |         |
| {{!MaxSteeringAngle:float:Cab, Steering:""}}     |          |         |
| {{!SteeringSensitivity:float:Cab, Steering:""}}  |          |         |
| {{!SteeringSpeed:float:Cab, Steering:""}}        |          |         |

#### Air Control

| Name                                              | Comments | Default |
| ------------------------------------------------- | -------- | ------- |
| {{!AirControlStrength:float:Cab, Air Control:""}} |          |         |
| {{!AirPitchInput:float:Cab, Air Control:""}}      |          |         |
| {{!AirYawInput:float:Cab, Air Control:""}}        |          |         |
| {{!AirTime:float:Cab, Air Control:""}}            |          |         |
| {{!bAirborne:bool:Cab, Air Control:""}}           |          |         |

#### RigidBody/Sleeping

| Name                                       | Comments | Default |
| ------------------------------------------ | -------- | ------- |
| {{!FreezeTimer:float:Cab, Sleeping:""}}    |          |         |
| {{!FreezeDelay:float:Cab, Sleeping:""}}    |          |         |
| {{!bFrozen:bool:Cab, Sleeping:""}}         |          |         |
| {{!bFreezeRotation:bool:Cab, Sleeping:""}} |          |         |

