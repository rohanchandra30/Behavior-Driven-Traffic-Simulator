"""
@file    runner.py
@author  Xiaoyu Li
@date    2019-08-01
This file is part of SUMO for sublane_model.
"""
from __future__ import absolute_import
from __future__ import print_function


import os
import subprocess
import sys
import shutil
import asyncio


try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

sumoBinary = checkBinary('sumo')

# run simulation
retcode = subprocess.call(
    [sumoBinary, "-c", "./sublane_model.sumocfg", "--no-step-log"], stdout=sys.stdout, stderr=sys.stderr)
print(">> Simulation closed with status %s" % retcode)
sys.stdout.flush()

# start the simulation and connect to it with the script: 
import traci
import compute_density
import parse

out_file = './out.xml'
net_file = './net.net.xml'
buckets=20
(data,vehicleList) = parse.parse_out(out_file)
(edges,leng) = compute_density.compute_func(out_file,net_file)

step_length = 2
traci.start([checkBinary('sumo-gui'), '-c',"./sublane_model.sumocfg", '--step-length', str(step_length)])

vehicles = []
flag = 0
start_vel = 5
step = 0
stopList = set()
changeLane = {}
aggrVehicle = set()

# set up the start speed of each vehicle
for v in vehicleList:
    Id = traci.vehicle.getTypeID(str(v))
    if Id == "AggrCar":
        aggrVehicle.add(v)
    traci.vehicle.setSpeedMode(v, 0)
    traci.vehicle.setSpeed(v, start_vel)

# record the time the aggressive cars have been blocked
for v in aggrVehicle:
    changeLane[v] = 1

traci.simulationStep() 
step = 1

# Run a simulation until all vehicles have arrived
while traci.simulation.getMinExpectedNumber() > 0: 
    traci.simulationStep()
    
    # recover the speed of the cars that stopped due to the pedestrain crossing from the last step
    for v in stopList:
      traci.vehicle.slowDown(v,start_vel,0)  
    stopList.clear()

    for e in edges:
        length = traci.lane.getLength(e+"_0")
        vehicles = traci.edge.getLastStepVehicleIDs(e)  
        persons = traci.edge.getLastStepPersonIDs(e)
        # stop conservative cars when there is a crossing
        for p in persons:
            posP = traci.person.getPosition(str(p))[0]
            if length-posP < 3 and length>posP:
                for v in vehicles:
                    Id = traci.vehicle.getTypeID(str(v))
                    pos = traci.vehicle.getLanePosition(str(v))
                    if Id == "Car" and length-pos < 10 and length>pos:
                        traci.vehicle.slowDown(v, 0,0)
                        stopList.add(v)
        # conservative cars should change lanes if blocked aggressive cars
        for v in vehicles:
            Id = traci.vehicle.getTypeID(str(v))
            pos = traci.vehicle.getLanePosition(str(v))
            if Id == "AggrCar":
                for v1 in vehicles:
                    pos1 = traci.vehicle.getLanePosition(str(v1))
                    if traci.vehicle.getTypeID(str(v1)) == "Car"and pos1 - pos < 20.0 and pos1 - pos > 0 and traci.vehicle.getLaneID(str(v1))==traci.vehicle.getLaneID(str(v)):
                        lane = traci.vehicle.getLaneID(str(v1))
                        tstep = changeLane[v]
                        traci.vehicle.highlight(v1, (255, 0, 0, 255), -1,1,6,0)
                        if tstep < 3:
                            changeLane[v] = tstep+1
                        else: 
                            index = int(lane[4])
                            if e == "beg":
                                if index == 1:
                                    traci.vehicle.moveTo(v1, e+"_2", pos1+5)
                                elif index == 2:
                                    traci.vehicle.moveTo(v1, e+"_1", pos1+5)
                            elif e == "end":
                                if index == 0:
                                    traci.vehicle.moveTo(v1, e+"_1", pos1+5)
                                elif index == 1:
                                    traci.vehicle.moveTo(v1, e+"_0", pos1+5)
        # make aggressive cars occupy empty space                
        for i in range(buckets-3):
            flag = 0
            for j in range(3):
                if edges[e][step][i+j] > 2:
                    flag = 1
            if flag == 0:     
                for v in vehicles:
                    flag = 0
                    Id = traci.vehicle.getTypeID(str(v))
                    pos = traci.vehicle.getLanePosition(str(v))
                    if Id == "AggrCar" and i*length/buckets<=pos<=(i+1)*length/buckets:
                        for v1 in vehicles:
                            #decrease aggressive cars' speed to avoid collision
                            if v1!= v and traci.vehicle.getLanePosition(str(v1))-pos < 19.0 and traci.vehicle.getLanePosition(str(v1))-pos > -19.0 and traci.vehicle.getLaneID(str(v1))==traci.vehicle.getLaneID(str(v)) :
                                #too close to other vehicles
                                traci.vehicle.slowDown(v, start_vel,0) 
                                #conservative cars should change lanes if blocked aggressive cars
                                if traci.vehicle.getTypeID(str(v1)) == "Car":
                                    lane = traci.vehicle.getLaneID(str(v1))
                                    if lane==e+"_1":
                                        traci.vehicle.changeLane(v1,2,1000)
                                    elif lane==e+"_2":
                                        traci.vehicle.changeLane(v1,1,1000)
                                flag = 1
                        if flag == 0:
                            newSpeed = traci.vehicle.getSpeed(v) + 0.5
                            traci.vehicle.slowDown(v, newSpeed,0)
                            print(v+":  "+str(traci.vehicle.getSpeed(v)))      
    print('---------------------------------------------')
    step += 1
    
print(step)
traci.close()