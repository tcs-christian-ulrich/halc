# halc
Hardware Abstraction Layer for Python

halc makes Devices avalible as base classes in an "Sensor Tree" and Keeps that tree actual even when Devices are plugged out/in

hal.showTree() shows this Device Tree
with hal.Devices.find() You can search for Devices by ID (Address), Name or Device Class
with hal.EnsureDevice() You can ensure/wait for an specific Device by ID (Address), Name or Device Class