
#### Wheel ID Variables
| Name                                                    | Comments              | Default |
| ------------------------------------------------------- | --------------------- | ------- |
| {{!WheelName:name:Wheel, ID:""}}                        |                       |         |
| {{!WheelIndex:int:Wheel, ID:""}}                        |                       |         |
| {{!bSteeringWheel:bool:Wheel, ID:"can steer"}}          | can steer             |         |
| {{!bDriveWheel:bool:Wheel, ID:"Receives engine power"}} | Receives engine power |         |
| {{!bBrakeWheel:bool:Wheel, ID:"Receives brakes"}}       | Receives brakes       |         |

#### Wheel Transform Variables
| Name                                                   | Comments | Default |
| ------------------------------------------------------ | -------- | ------- |
| {{!WheelMountTransform:transform:Wheel, Transform:""}} |          |         |
| {{!WheelContactPoint:vector:Wheel, Transform:""}}      |          |         |
| {{!WheelForwardDirection:vector:Wheel, Transform:""}}  |          |         |
| {{!WheelRightDirection:vector:Wheel, Transform:""}}    |          |         |
| {{!WheelUpDirection:vector:Wheel, Transform:""}}       |          |         |

#### Wheel Suspension Runtime Variables

| Name                                                                             | Comments             | Default |
| -------------------------------------------------------------------------------- | -------------------- | ------- |
| {{!SuspensionCompression:float:Wheel, Suspension Runtime:"Current Compression"}} | Current Compression  |         |
| {{!SuspensionVelocity:float:Wheel, Suspension Runtime:"Compression Speed"}}      | Compression Speed    |         |
| {{!SuspensionForce:float:Wheel, Suspension Runtime:"Current Spring Force"}}      | Current Spring Force |         |
| {{!bGrounded:bool:Wheel, Suspension Runtime:"Ground Contact"}}                   | Ground Contact       |         |
| {{!GroundHit:Wheel, Suspension Runtime:"Trace Result"}}                          | Trace Result         |         |
| {{!GroundNormal:vector:Wheel, Suspension Runtime:"Surface Normal"}}              | Surface Normal       |         |
| {{!ContactPoint:vector:Wheel, Suspension Runtime:"Ray hit point"}}               | Ray hit point        |         |
| {{!ContactTag:name:Wheel, Suspension Runtime:"Surface type"}}                    | Surface type         |         |


#### Wheel Other Runtime Variables
| Name                                          | Comments | Default |
| --------------------------------------------- | -------- | ------- |
| {{!WheelVelocity:vector:Wheel, Runtime:""}}   |          |         |
| {{!ForwardVelocity:vector:Wheel, Runtime:""}} |          |         |
| {{!LateralVelocity:vector:Wheel, Runtime:""}} |          |         |
| {{!SlipAmount:float:Wheel, Runtime:""}}       |          |         |
| {{!WheelSpinAmount:float:Wheel, Runtime:""}}  |          |         |
| {{!CurrentFriction:float:Wheel, Runtime:""}}  |          |         |
| {{!MaxFrictionForce:float:Wheel, Runtime:""}} |          |         |
| {{!SlideAmount:float:Wheel, Runtime:""}}      |          |         |
