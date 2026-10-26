import ast
import inspect
import copy
import textwrap
import punxa_6502 as punxa
import astunparse
import py4hw

class Example:

    def __init__(self):
        self.a = self.addIn('a')
    
    def test(self):
        yield from self.bar()
        
        while (True):
            yield from self.bar()
            
            yield from self.foo()
        
    def foo(self):
        self.a,put(2)
        yield 
        self.a,put(3)
        yield   
        self.a,put(4)
        yield from self.bar()
    
    def bar(self):
        self.a,put(5)
        yield 
        self.a,put(6)
        yield 
        
class Example2:

    def __init__(self):
        self.a = self.addIn('a')
    
    def run(self):
        self.a.prepare(5)
        yield
        self.a.prepare(6)
        yield
        while True:
            self.a.prepare(5)
            yield
            self.a.prepare(6)
            yield
            self.a.prepare(2)
            yield
            self.a.prepare(3)
            yield
            self.a.prepare(4)
            

class Example3:

    def __init__(self):
        self.a = self.addIn('a')
        
        self.state = 0
    
    def run(self):
        
        if (self.state == 0):
            self.a.prepare(5)
            self.state = 1
        elif (self.state == 1):
            self.a.prepare(6)
            self.state = 2

        elif (self.state == 2):
            # while True:
            self.a.prepare(5)
            self.state = 3
        elif (self.state == 3):
            self.a.prepare(6)
            self.state = 4
        elif (self.state == 4):
            self.a.prepare(2)
            self.state = 5
        elif (self.state == 5):
            self.a.prepare(3)
            self.state = 6
        elif (self.state == 6):
            self.a.prepare(4)
            self.state = 2
 
class Example4(py4hw.Logic):
    
    def __init__(self, parent, name:str, reset, status, control):
        
        super().__init__(parent, name)

        self.addIn('reset', reset)

        for key in status.keys():
            self.addIn(key, status[key])

        
        for key in control.keys():
            self.addOut(key, control[key])
            
            
        self.status = status
        self.control = control
        
        self.retired = 0
        
        self.co = self.run()
        
    def getRetiredInstructions(self):
        return self.retired
    
    def clock(self):
        next(self.co)
        
        
    def resetCycle(self):
        control = self.control
        control['sel_databus'].prepare(0)
        control['sel_memory'].prepare(0)
        control['e_PC_lo'].prepare(0)
        control['e_PC_hi'].prepare(0)
        
        yield
        
    def run(self):
        yield from self.resetCycle()
        
        while (True):
            yield from self.fetchIR()
            #yield from self.decodeAndExecute()
            
            self.retired += 1
            yield
            #yield from self.incpc()
            #yield from self.fetchOperand()
            #yield from self.execute()
        
    def fetchIR(self):
        # Some debug
        pc = self.parent.children['datapath']._wires['q_PC'].get()

        if (pc in self.parent.symbols.keys()):
            print('{}:'.format(self.parent.symbols[pc]))

        print(f'{pc:04X} - ', end='')
        # We just fetch one instruction from the PC address
        control = self.control
        control['sel_memory'].prepare(0) # select PC for address
        control['mem_read'].prepare(1)
        yield
        yield
        control['mem_read'].prepare(0)
        control['sel_databus'].prepare(self.DATA_MEM) 
        control['e_IR'].prepare(1)
        yield
        control['e_IR'].prepare(0)
        control['sel_databus'].prepare(self.DATA_ALU) 
        yield
        ir = self.parent.children['datapath']._wires['q_IR'].get()
        print(f'{ir:02X} ', end='')
    
#print(inline_yield_from(Example))

#print(inline_yield_from(punxa.ControlUnit6502Behavioral))

#print(transform_generator_to_fsm(Example2))

gen = py4hw.Py4hwGenerator()

print(gen.generateSequentialCode(Example4))

if (False):
    hw = py4hw.HWSystem()
    
    reset = hw.wire('reset')
    
    control = {}
    status = {}
    
    dut = Example4(hw, 'dut', reset, status, control)
    
    rtl = py4hw.VerilogGenerator(dut)
    print(rtl.getVerilog())