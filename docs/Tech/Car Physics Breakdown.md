!!! warning
	Avoid putting physics in Event Tick using Delta Seconds. Add an accumulator. 



### Blueprint-Only Physics Best Practices

##### Avoid Relying on a Chaos Physics Body
Even if using an accumulator, Chaos does not update its physics in time with our Blueprint tick-based fixed step. **Add Force** integrates Chaos physics, so we should avoid it.

* Keep vehicle-wide suspension tuning on the car actor
* Keep per-wheel runtime state inside each wheel component
* Keep per-wheel configuration inside each wheel component only when it is unique
### Maintaining Vehicle State Separately

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
	--8<-- "./docs/snippets/Variables/VariablesWheels.md"
	--8<-- "./docs/snippets/Variables/S_SurfaceData.md"

=== "Vehicle BP Variables"
	--8<-- "./docs/snippets/Variables/VariablesCab.md"

=== "Force Accumulators (In Vehicle BP)"
	--8<-- "./docs/snippets/Variables/VariablesCabAccumulators.md"
***

### Replacing AddForceAtLocation()


!!! note "**ApplyForceAtPoint({{Force:vector:f}}, {{WheelLocation:vector:f}})** (Owned by Cab)"
	Each wheel calls this. After each wheels has updated the {{TotalForce}} and {{TotalTorque} of the **Cab**, the **Cab** can integrate it into motion. 
	
	*  {{TotalForce:vector}} += {{Force:vector:f}}
	* {{LeverArm:vector:l}} = {{WheelLocation:vector:f}} - {{CenterOfMassWorld:vector}}
	* {{Torque:vector:l}} = CrossProduct({{LeverArm:vector:l}}, {{Force:vector:f}})
	* {{TotalTorque:vector}} += {{Torque:vector:l}}

!!! note "Cab Integrates {{TotalForce}} and {{TotalTorque}}"
	**Linear Motion**
	
	* {{Acceleration:vector:l}} = {{TotalForce:vector}} / {{CabMass:float}}
	* {{CabVelocity:vector}} += {{Acceleration:vector:l}} * {{FixedDelta:float}}
	
	 **Rotational Motion**
	 
	 * {{AngularAcceleration:vector:l}} = {{TotalTorque:vector}} / {{MomentOfInertia:vector}} 
	 * {{CabAngularVelocity}} += {{AngularAcceleration:vector:l}} * {{FixedDelta:float}}


!!! note "GetVelocityAtPoint({{WorldPosition:vector:f}}) (Owned by Wheel Comp)"
	Because we can't use GetVelocityAtPoint() Without Chaos, we need to replace it. 
	
	* {{Offset:vector:l}} = {{WorldPosition:vector:f}} -  ={{CenterOfMassWorld:vector}}
	* {{RotationalVelocity:vector:l}} = CrossProduct({{CabAngularVelocity}}, {{Offset:vector:l}})
	* Return {{CabVelocity:vector}} + {{RotationalVelocity:vector:l}}

```
Wheel
-Calculates Suspension Force
	Cab.ApplyForceAtPoint(SuspensionForce, ContactPoint)
-Calculates Drive Force
	Cab.ApplyForceAtPoint(DriveForce, ContactPoint)
-Calculates Braking Force
	Cab.ApplyForceAtPoint(BrakingForce, ContactPoint)
-Calculates Friction Force
	Cab.ApplyForceAtPoint(BrakingForce, ContactPoint)
```
