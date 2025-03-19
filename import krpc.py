import krpc
import math
import time

# Connect to kRPC server
conn = krpc.connect(name='List Parts')
print("Connected to kRPC server")

# Get the active vessel
vessel = conn.space_center.active_vessel
flight = vessel.flight(vessel.surface_reference_frame)
control = vessel.control
autopilot = vessel.auto_pilot
for part in vessel.parts.with_tag("EngineS1-1"):
    Engine1 = part.engine
    print(Engine1)

StageGo = True
VehicleGreen = False
Stage = 0
ORBGUIDO = False
BGUIDO = False
GravityTurn = False
TSA = 1500
TEA = 65000
staged = False
if StageGo: 
    Engine1.active = True
    Engine1.independent_throttle = True
    Engine1.throttle = 1
    VehicleGreen = True
    Stage = 1
    vessel.control.activate_next_stage()
    control.sas = True

while VehicleGreen and Stage == 1:
    print(vessel.resources_in_decouple_stage(1,True).amount('Oxidizer'), flight.pitch, flight.heading, flight.roll )
    
    if flight.dynamic_pressure > 12000:
        Engine1.throttle = 0.8

    elif flight.surface_altitude > 10500:
        Engine1.throttle = 1
    
    print(vessel.resources_in_decouple_stage(1,False).amount('Oxidizer'), vessel.control )
    
    if vessel.resources_in_decouple_stage(1,True).amount('Oxidizer') < 5: 
        vessel.control.activate_next_stage()
        print("ReadyForStaging")
        Stage = 2
    if Stage == 2: 
        ORBGUIDO = True
    BGUIDO = not ORBGUIDO       
    if flight.surface_altitude > 100 and not GravityTurn:
        vessel.auto_pilot.engage()
        autopilot.target_roll = 90
        autopilot.target_pitch = 90
    if flight.surface_altitude > 1500: 
        autopilot.target_roll = 0
        autopilot.target_pitch = 90 * (1 - (flight.surface_altitude - TSA) / (TEA - TSA))
        print(autopilot.target_pitch)
        GravityTurn = True
    
    time.sleep(0.1)


vessel.control.roll = 0 
vessel.control.yaw = 0
vessel.control.pitch = 0
VehicleGreen = True 
Stage = 2
vessel.auto_pilot.disengage()
time.sleep(0.5)
while VehicleGreen and Stage == 2: 
    if Stage == 2  and not staged:
        control.sas = True
        time.sleep(0.1)
        control.throttle = 1
        time.sleep(1)
        control.throttle = 0
        staged = True
        control.sas_mode = conn.space_center.SASMode.prograde
    if vessel.orbit.time_to_apoapsis < 45 and staged:
        control.throttle = 1
    elif vessel.orbit.periapsis_altitude > 80000 and staged:
        control.throttle = 0
    elif vessel.orbit.time_to_apoapsis > 60 and staged and vessel.orbit.periapsis_altitude < 80000:
        control.throttle = 0
    time.sleep(0.1)

   
