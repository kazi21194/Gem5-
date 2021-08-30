
"""
Declaration : I have referred(taken/edited some of the code) from the following materials.
            
            https://www.gem5.org/documentation/learning_gem5/part1/cache_config/
            https://gem5.googlesource.com/public/gem5/
"""

import m5
# import all of the SimObjects
from m5.objects import *

# create the system we are going to simulate
system = System()

# Set the clock fequency 
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the memory system
system.mem_mode = 'timing'               
system.mem_ranges = [AddrRange('512MB')] 

# Create a simple CPU
system.cpu = TimingSimpleCPU()


"""This is to create cache L1 and L2 """

#Extending the baseCache
class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

#Creating subclasses of L1 cache
class L1ICache(L1Cache):
    size = '16kB'
    # to connect cpu to L1 instruction cache
    def connectCPU(self,cpu):
        self.cpu_side = cpu.icache_port
    # to connect L1 instruction cache to L2 bus
    def connectBus(self,bus):
        self.mem_side = bus.cpu_side_ports

class L1DCache(L1Cache):
    size = '16kB'
    # to connect cpu to L1 data cache
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port
    # to connect L1 data cache to L2 bus   
    def connectBus(self,bus):
        self.mem_side = bus.cpu_side_ports

class L2Cache(Cache):
    size = '256kB'
    assoc = 4
    tag_latency = 10
    data_latency = 10
    response_latency = 10
    mshrs = 20
    tgts_per_mshr = 12
    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports



# create a L1cache
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

#connecting CPU to L1 cache
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus
system.membus = SystemXBar()

#create a L2 bus 
system.L2bus = L2XBar()

#connecting L2 bus to L1 I and D cache
system.cpu.icache.connectBus(system.L2bus)
system.cpu.dcache.connectBus(system.L2bus)

#create  a L2 cache
system.L2cache = L2Cache()

#connecting L2 cache to L2bus and membus
system.L2cache.connectCPUSideBus(system.L2bus)
system.L2cache.connectMemSideBus(system.membus)


# create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()

# interrupts are connected to the memory
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports




# Create a DDR3 memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports


# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports 


# get ISA for the binary to run.
isa = "x86"

# path of  susan binary file
binary = "/home/ubuntu-izak/gem5/configs/CA_assignments/susan"

# SE here is syscall emulation
system.workload = SEWorkload.init_compatible(binary)

# Create a process 
process = Process()

# Set the command
process.cmd = [binary]

# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

# set up the root SimObject and start the simulation 
root = Root(full_system = False, system = system)


m5.instantiate()

print("\nBeginning simulation!\n")
exit_event = m5.simulate()
print('\nExiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))
