from pynq.overlays.logictools import LogicToolsOverlay
from pynq.lib.logictools import Waveform
from random import random
import time
import re
from copy import deepcopy
from collections import OrderedDict
from pynq import Register
from pynq.lib.logictools.constants import *
from pynq.lib.logictools.logictools_controller import LogicToolsController
from pynq.lib.logictools.trace_analyzer import TraceAnalyzer
from pynq.lib.logictools.waveform import Waveform

logictools_olay = LogicToolsOverlay('logictools.bit')
print("Loaded")

def waveGen(data):
    return(''.join(list(map(translate1,data))))

def translate1(a):
     return(chr((-4*a)+108)+'.'*(int(1)-1))
    
def translate2(a):
    return(int((ord(a)-108)/(-4)))

def dataGen(waveform):
    datstring = waveform.get('wave')
    liststring=list(datstring)[::1]
    data=[]
    for i in range(0,len(liststring)):
        if liststring[i] == '.':
            liststring[i] = liststring[i-1]
    data = list(map(translate2,liststring))
    return [data]

def pattern_gen(a):
    #setup input and output pins
    
    up_counter = {'signal': [
        ['stimulus',
            {'name': 'Laser', 'pin': 'D0', 'wave': 'l'*len(a) }], 

        ['analysis',
            {'name': 'Loopback', 'pin': 'D10'}]], 

        'foot': {'tock': 1},
        'head': {'text': 'up_counter'}}
    
    #display output waveform
    #waveform = Waveform(up_counter)
    #waveform.display()

    pattern_generator = logictools_olay.pattern_generator
    pattern_generator.reset()
    pattern_generator.trace(num_analyzer_samples=len(a))
    
    
    
    
    pattern_generator.setup(up_counter,
                            stimulus_group_name='stimulus',
                            analysis_group_name='analysis',
                            #mode = 'multiple',
                            frequency_mhz = .3)
    
    print(pattern_generator.src_samples)
    pattern_generator.src_samples = np.array(a)
    print(pattern_generator.src_samples)
    
    st3 = time.time()
    src_addr = pattern_generator.logictools_controller.allocate_buffer('src_buf',1+len(pattern_generator.src_samples),data_type="unsigned int")
    tri_addr = pattern_generator.logictools_controller.allocate_buffer('tri_buf',1+len(pattern_generator.src_samples),data_type="unsigned int")
    pattern_generator.logictools_controller.buffers['src_buf'][0]=0
    pattern_generator.logictools_controller.buffers['tri_buf'][0]=0
    for index, data in enumerate(pattern_generator.src_samples):
        pattern_generator.logictools_controller.buffers['src_buf'][index+1] = data
    pattern_generator.logictools_controller.write_control([src_addr,1+len(pattern_generator.src_samples),0,tri_addr])
    pattern_generator.logictools_controller.write_command(CMD_CONFIG_PATTERN)
    pattern_generator.logictools_controller.free_buffer('src_buf')
    pattern_generator.logictools_controller.free_buffer('tri_buf')
    pattern_generator.logictools_controller.check_status()
    
    #print("Running")
    

    
    st4 = time.time()
    
    pattern_generator.run()
    print("Pattern generator set up time:")
    print(time.time()-st3)    
    #print("Pattern generator run time:")
    #print(time.time()-st4)    
    pattern_generator.show_waveform()

    

    
    pattern_list = pattern_generator.analyzer.analyze()
    

    
    output = pattern_list[10]
    print(output)
    pattern_generator.reset()
    #pattern_generator.stop()

    
    
    return output
    
    
#data_in = [1,0,1,0,1,0,1,0,1]
n=2000
data_in=[]
for k in range(0,8*n):
    data_in.append(round(random()))
    
st=time.time()
acc=[]
num=1
for i in range(0,num):
    st=time.time()
    b=pattern_gen(data_in)#waveGen(data_in))
    data_out = dataGen(b)[0]
    #print(data_out)
    #print("Total run time:")
    #print(time.time()-st)
    acc.append((data_out==data_in))
print(sum(acc))


#print("Date in:")
#print(data_in)
#print("Date out:")
#print(data_out)
#print("If input and output are the same:")
#print(data_in == data_out)