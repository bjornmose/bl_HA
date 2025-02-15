# This script defines functions to be used directly in drivers expressions to
# extend the builtin set of python functions.
#
# This can be executed on manually or set to 'Register' to
# initialize thefunctions on file load.

import bpy
import math
from math import sin, cos, radians
import mathutils
import bmesh
import json
import numpy as np
import os
import sys
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator



dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )
    print(sys.path)

import BVT

# this next part forces a reload in case you edit the source after you first start the blender session
import importlib
importlib.reload(BVT)

from BVT import *


nIDHAWatch    = "IDHAWatch"
nHA_Damp      = "HA_Damp"
nHA_Loops     = "HA_Loops"
nHA_Frames    = "HA_Frames"
nControlRoot = "ControlRoot"
nHARoot      = "HARoot"

nHASin        = "HASin"
nHACos        = "HACos" 
nHAOrder      = "HAOrder" 
nCSin1       = "CSin1"
nCCos1       = "CCos1" 
nCSin2       = "CSin2"
nCCos2       = "CCos2" 


nLissajousScale = "LisScale"
nLissajousSin1x = "LisSin1x"
nLissajousSin1y = "LisSin1y"
nLissajousSin1z = "LisSin1z"

nLissajousCos1x = "LisCos1x"
nLissajousCos1y = "LisCos1y"
nLissajousCos1z = "LisCos1z"

nLissajousSin2x = "LisSin2x"
nLissajousSin2y = "LisSin2y"
nLissajousSin2z = "LisSin2z"

nLissajousCos2x = "LisCos2x"
nLissajousCos2y = "LisCos2y"
nLissajousCos2z = "LisCos2z"



nFrames      = "Osz_Frames"
nShift       = "Osz_Shift"
nAmplitude   = "Osz_Amplitude"
nStickyOrg   = "Osz_StickyOrg"
nCopyFrom    = "Osz_CopyFrom"
nCopyTo      = "Osz_CopyTo"
nClock       = "Osz_Clock"

nDefaultPeriod =2*2*3*5*7

nControlDefaultDefaultShape = "SPHERE"

def _runCycleOnce():
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end
    obj = bpy.context.active_object
    actual = start
    bpy.context.scene.frame_set(actual)
    while (actual < end + 1):
     #print("actual:",actual)
     bpy.context.scene.frame_set(actual)
     actual += 1


def oszUniqueName(namein):
        name = namein
        pp=name.partition(nControlRoot)
        if (len(pp[1])>0):
            name = pp[0] + 'I'+nControlRoot
        return(name)   

def oscAxisID(t,axis,ID):
    obj = bpy.data.objects.get(ID+nControlRoot)
    if (not obj):
        return 0
    try:
     frames =  obj[nFrames]
    except: 
     frames = nDefaultPeriod
    try:
     shift  =  obj[nShift] 
    except: 
     shift = 0.0
    try:
     amp = obj[nAmplitude] 
    except: 
     amp = 1.0
    try:
     fo = obj[nStickyOrg] 
    except: 
     fo = 1.0

    try:
        now = obj[nClock] 
    except: 
        p = obj.parent
        try:
            now = p[nClock] 
        except:
            now = t

   

    timebase = frames/(2*math.pi)
    f=(now+shift)/timebase 
        
    obj = bpy.data.objects.get(ID+nControlRoot)
    o = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCSin1)
    a = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCCos1)
    b = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCSin2)
    c = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCCos2)
    d = obj.location[axis]
    v = fo*o + amp * (a  * sin(f) + b * cos(f) + c * sin(2*f) + d * cos(2*f))
    return v

def oscAxisIDe(t,axis,ID):
    obj = bpy.data.objects.get(ID+nControlRoot)
    if (not obj):
        return 0
    try:
     frames =  obj[nFrames]
    except: 
     frames = nDefaultPeriod 
    try:
     shift  =  obj[nShift] 
    except: 
     shift = 0.0
    try:
     amp = obj[nAmplitude] 
    except: 
     amp = 1.0
     
    try:
        now = obj[nClock] 
    except: 
        p = obj.parent
        try:
            now = p[nClock] 
        except:
            now = t

         
    timebase = frames/(2*math.pi)
    f=(now+shift)/timebase 
        
    #obj = bpy.data.objects.get(ID+nControlRoot)
    #o = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCSin1)
    a = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCCos1)
    b = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCSin2)
    c = obj.location[axis]
    obj = bpy.data.objects.get(ID+nCCos2)
    d = obj.location[axis]
    v = amp * (a  * sin(f) + b * cos(f) + c * sin(2*f) + d * cos(2*f))
    return v

def drv_HAAxisID(t,axis,ID):
    obj = bpy.data.objects.get(ID+nHARoot)
    if (not obj):
        return 0
    try:
     frames =  obj[nFrames]
    except: 
     frames = nDefaultPeriod 
    try:
     shift  =  obj[nShift] 
    except: 
     shift = 0.0
    try:
     amp = obj[nAmplitude] 
    except: 
     amp = 1.0
    try:
     nOrder = obj[nHAOrder] 
    except: 
     nOrder = 3.0
     
    try:
        now = obj[nClock] 
    except: 
        p = obj.parent
        try:
            now = p[nClock] 
        except:
            now = t

    timebase = frames/(2*math.pi)
    f=(now+shift)/timebase
    val = 0
    for o in range(1,nOrder+1):        
        OName ="{:}{:}{:}".format(ID,nHASin,o)
        obj = bpy.data.objects.get(OName)
        a = obj.location[axis]
        val = val + a * sin(o*f)
        OName ="{:}{:}{:}".format(ID,nHACos,o)
        obj = bpy.data.objects.get(OName)
        a = obj.location[axis]
        val = val + a * cos(o*f)
    return val

def drv_cumHaFi(axis,fu,n,ID,t,v):
    #calculate base fequency
    obj = bpy.data.objects.get(ID)
    frames = bpy.context.scene[nHA_Frames]
    damp = frames*bpy.context.scene[nHA_Damp]
    if (damp == 0): 
        return 0
    timebase = frames/(2.*math.pi)
    magic = 2.
    f=(t)/timebase 
    c=0
    if (fu == 'sin'): 
        c = magic*obj.location[axis] * sin(n*f)
    elif (fu == 'cos'): 
        c = magic*obj.location[axis] * cos(n*f)
    else:
        print('drv_cumHaFi fU?')
    r = ((damp-1)*v + c)/damp
    return r


def _driverCumHaFi(fu,n,index ,ID):
    txt = "drv_cumHaFi({:},'{:}',{:},'{:}',frame,self.location[{:}])".format(index,fu,n,ID,index)
    return txt
     

def add_driverCumHaFi(consumer,fu,n,index ,ID):
    d = consumer.driver_add( 'location', index ).driver
    d.use_self = True
    d.expression = _driverCumHaFi(fu,n,index ,ID) 
    
def _osz_hook_HA(consumer,IDwatched):
    name = consumer.name
    order = consumer[nHAOrder]
    pp=name.partition(nHARoot)
    prefix = pp[0]
    for o in range(1,order):
        OName ="{:}{:}{:}".format(prefix,nHASin,o)
        cso = bpy.data.objects.get(OName)
        add_driverCumHaFi(cso,'sin',o,0 ,IDwatched)
        add_driverCumHaFi(cso,'sin',o,1 ,IDwatched)
        add_driverCumHaFi(cso,'sin',o,2 ,IDwatched)

        OName ="{:}{:}{:}".format(prefix,nHACos,o)
        cso = bpy.data.objects.get(OName)
        add_driverCumHaFi(cso,'cos',o,0 ,IDwatched)
        add_driverCumHaFi(cso,'cos',o,1 ,IDwatched)
        add_driverCumHaFi(cso,'cos',o,2 ,IDwatched)


def _osz_unhook_HA(consumer):
    name = consumer.name
    pp=name.partition(nHARoot)
    order = consumer[nHAOrder]
    prefix = pp[0]
    for o in range(1,order):
        OName ="{:}{:}{:}".format(prefix,nHASin,o)
        cso = bpy.data.objects.get(OName)
        cso.driver_remove('location')
        OName ="{:}{:}{:}".format(prefix,nHACos,o)
        cso = bpy.data.objects.get(OName)
        cso.driver_remove('location')


class op_osz_hook_ha(bpy.types.Operator):
    bl_idname = "object.addhookdriveroperator"
    bl_label = "UpdateWatchkDriver"

    def execute(self,context):
        obj = context.object
        obsname=obj[nIDHAWatch]
        _osz_hook_HA(obj,obsname)
        return{'FINISHED'}

class op_osz_unhook_ha(bpy.types.Operator):
    bl_idname = "object.removehookdriveroperator"
    bl_label = "RemoveWatchkDriver"

    def execute(self,context):
        obj = context.object
        obsname=obj[nIDHAWatch]
        _osz_unhook_HA(obj)
        return{'FINISHED'}
    
 
def OszCopyFromNamedRoot(ID,name):
    obj1 = bpy.data.objects.get(ID+name)
    obj2 = bpy.data.objects.get(name)
    obj1.location = obj2.location

    
def OszCopyFromRoot(context,ID):
    OszCopyFromNamedRoot(ID,nControlRoot)
    OszCopyFromNamedRoot(ID,nCSin1)
    OszCopyFromNamedRoot(ID,nCCos1)
    OszCopyFromNamedRoot(ID,nCSin2)
    OszCopyFromNamedRoot(ID,nCCos2)

def OszCopyLocation(ID_me,ID_other,name):
    obj1 = bpy.data.objects.get(ID_me+name)
    obj2 = bpy.data.objects.get(ID_other+name)
    obj1.location = obj2.location
  
def OszCopyProps(ID_me,ID_other,name):
    obj1 = bpy.data.objects.get(ID_me+name)
    obj2 = bpy.data.objects.get(ID_other+name)
    obj1[nFrames]  = obj2[nFrames] 
    obj1[nShift]   = obj2[nShift] 
    obj1[nAmplitude]   = obj2[nAmplitude] 


def OszCopyFromOther(ID_me,ID_other):
    OszCopyLocation(ID_me,ID_other,nControlRoot)
    OszCopyProps(ID_me,ID_other,nControlRoot)
    OszCopyLocation(ID_me,ID_other,nCSin1)
    OszCopyLocation(ID_me,ID_other,nCCos1)
    OszCopyLocation(ID_me,ID_other,nCSin2)
    OszCopyLocation(ID_me,ID_other,nCCos2)
    

class OszControl():

    def objIsOsz(obj):
        to_name = obj.name + nControlRoot
        Cobj = bpy.data.objects.get(to_name)
        if (Cobj is not None ):
            return True
        else:
            return False

    @staticmethod
    def _objNameTaggedHA(obj):
        name = obj.name
        pp=name.partition(nHARoot)
        if (len(pp[1])>0):
            return True
        else:
            return False 

    @classmethod
    def objIsHA(self,obj):
        if (self._objNameTaggedHA(obj)):
            return True
        else:
            return False

    @classmethod
    def objHasHAParent(self,obj):
        pa = obj.parent
        if (pa):
            return self._objNameTaggedHA(pa)
        else:
            return False

    
    
def GenControl(ID):
     w_empty_draw_size = 1
     OName =ID+nControlRoot
     Cobj = bpy.data.objects.get(OName)
     if (not Cobj):
         Cobj = createEmpty(OName,w_empty_draw_size,nControlDefaultDefaultShape )
         Cobj[nFrames] = nDefaultPeriod 
         Cobj[nShift] = 0.0
         Cobj[nAmplitude] = 1.0
         Cobj[nCopyFrom] = 'void'
         Cobj[nCopyTo] = 'void'
         
         Cobj[nLissajousScale] = 0.5
         
         Cobj[nLissajousSin1x] = 1.         
         Cobj[nLissajousSin1y] = 0.         
         Cobj[nLissajousSin1z] = 0.         
         
         Cobj[nLissajousCos1x] = 0.         
         Cobj[nLissajousCos1y] = 1.         
         Cobj[nLissajousCos1z] = 0.         
         
         Cobj[nLissajousSin2x] = 1.         
         Cobj[nLissajousSin2y] = 0.        
         Cobj[nLissajousSin2z] = 0.        
         
         Cobj[nLissajousCos2x] = 0.         
         Cobj[nLissajousCos2y] = 1.         
         Cobj[nLissajousCos2z] = 0.         
  
 
           
     OName =ID+nCSin1
     obj = bpy.data.objects.get(OName)
     if (not obj):
         obj = createEmpty(OName,w_empty_draw_size,'ARROWS')
         obj.parent = Cobj

     OName =ID+nCCos1
     obj = bpy.data.objects.get(OName)
     if (not obj):
         obj = createEmpty(OName,w_empty_draw_size,'ARROWS')
         obj.parent = Cobj

     OName =ID+nCSin2
     obj = bpy.data.objects.get(OName)
     if (not obj):
         obj = createEmpty(OName,w_empty_draw_size,'ARROWS')
         obj.parent = Cobj

     OName =ID+nCCos2
     obj = bpy.data.objects.get(OName)
     if (not obj):
         obj = createEmpty(OName,w_empty_draw_size,'ARROWS')
         obj.parent = Cobj
     print(ID+"GenControl Done")
     return(Cobj)

def GenHAControl(ID,nOrder):
     w_empty_draw_size = 1
     OName =ID+nHARoot
     Cobj = bpy.data.objects.get(OName)
     if (not Cobj):
         Cobj = createEmpty(OName,w_empty_draw_size,nControlDefaultDefaultShape )
         Cobj[nFrames] = nDefaultPeriod 
         Cobj[nShift] = 0.0
         Cobj[nAmplitude] = 1.0
     Cobj[nHAOrder] = nOrder
     for order in range(1,nOrder+1):
        OName ="{:}{:}{:}".format(ID,nHASin,order)
        obj = bpy.data.objects.get(OName)
        if (not obj):
         obj = createEmpty(OName,w_empty_draw_size,'ARROWS')
         obj.parent = Cobj
        OName ="{:}{:}{:}".format(ID,nHACos,order)
        obj = bpy.data.objects.get(OName)
        if (not obj):
         obj = createEmpty(OName,w_empty_draw_size,'ARROWS')
         obj.parent = Cobj

     return(Cobj)
     


def AddHAdriver(source,ID):
    for n in range(3):
        d = source.driver_add( 'location', n ).driver
        d.expression = "drv_HAAxisID(frame,"+str(n)+",'"+ID+"')" 


def add_driverOsc(source, index ,ID):
    d = source.driver_add( 'location', index ).driver
    d.expression = "oscAxisID(frame,"+str(index)+",'"+ID+"')" 
    

def AddOszDriver(obj,ID):
    add_driverOsc(obj, 0, ID)    
    add_driverOsc(obj, 1, ID)
    add_driverOsc(obj, 2, ID)



def add_driverOsce(source, index ,ID):
    d = source.driver_add( 'location', index ).driver
    d.expression = "oscAxisIDe(frame,"+str(index)+",'"+ID+"')" 
    
def AddOszDrivere(obj,ID):
    add_driverOsce(obj, 0, ID)    
    add_driverOsce(obj, 1, ID)
    add_driverOsce(obj, 2, ID)


def add_driverOscRot(source, index ,ID):
    d = source.driver_add( 'rotation_euler', index ).driver
    d.expression = "oscAxisID(frame,"+str(index)+",'"+ID+"')" 
    
def AddOszDriverRot(obj,ID):
    add_driverOscRot(obj, 0, ID)    
    add_driverOscRot(obj, 1, ID)
    add_driverOscRot(obj, 2, ID)
    
def osz2JsonFile(ID,filepath):
    #write to json file
    with open(filepath, 'w') as ji:
            jdata = {}
            robj = bpy.data.objects.get(ID+nHARoot)
            order = robj[nHAOrder] 
            jdata[nHAOrder] = order
            for o in range(1,order+1):
                #do sin
                nSet = "{:}{:}".format(nHASin,o)
                obj = bpy.data.objects.get(ID+nSet)
                jdata[nSet] = [obj.location[0],obj.location[1],obj.location[2]]
                #do cos
                nSet = "{:}{:}".format(nHACos,o)
                obj = bpy.data.objects.get(ID+nSet)
                jdata[nSet] = [obj.location[0],obj.location[1],obj.location[2]]
            json.dump(jdata, ji, ensure_ascii=False, indent=4)
            ji.close()
    return{'FINISHED'}

def jsonFile2Osz(ID,filepath):
    #read from json file
    with open(filepath, 'r') as ji:
            jdata = json.load(ji)
            order = jdata[nHAOrder]
            for o in range(1,order+1):
                #do sin
                nSet = "{:}{:}".format(nHASin,o)
                obj = bpy.data.objects.get(ID+nSet)
                obj.location[0] = jdata[nSet][0]
                obj.location[1] = jdata[nSet][1]
                obj.location[2] = jdata[nSet][2]
                #do cos
                nSet = "{:}{:}".format(nHACos,o)
                obj = bpy.data.objects.get(ID+nSet)
                obj.location[0] = jdata[nSet][0]
                obj.location[1] = jdata[nSet][1]
                obj.location[2] = jdata[nSet][2]

            ji.close()
    return{'FINISHED'}



class op_osz2Json(bpy.types.Operator, ExportHelper):
    """Save positions of subcontrols to json file"""
    bl_idname = "object.op_osz2json"  # name to call from UI
    bl_label = "ExportOsz2Json"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        id = context.active_object.name        
        pp=id.partition(nHARoot)
        return osz2JsonFile(pp[0], self.filepath)
        
class op_json2Osz(bpy.types.Operator, ImportHelper):
    """Load positions of subcontrols ffrom json file"""
    bl_idname = "object.op_json2osz"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "ImportJson2Osz"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    def execute(self, context):
        id = context.active_object.name        
        pp=id.partition(nHARoot)
        return jsonFile2Osz(pp[0], self.filepath)

    
     
class CopyOszRootOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.copyoszroot_operator"
    bl_label = "CopyFromControlRoot"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        pp=obj.name.partition(nControlRoot)
        if (len(pp[1]) > 0):
         OszCopyFromRoot(context,pp[0])
         print("Transfer-->"+pp[0]+pp[1])
        return {'FINISHED'}
     

class AddOszDriverOperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.addoszdriveroperator"
    bl_label = "AddOszDriver"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        name = obj.name
        """
        pp=obj.name.partition(nControlRoot)
        if (len(pp[1])>0):
            name = pp[0] + 'I'+nControlRoot
        """
        con=GenControl(name)
        con[nStickyOrg] = 0.0

        AddOszDriver(obj,name)
        return {'FINISHED'}
    

class AddRotOszDriverOperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.adrotdoszdriveroperator"
    bl_label = "AddRotOszDriver"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        name = obj.name
        """
        pp=obj.name.partition(nControlRoot)
        if (len(pp[1])>0):
            name = pp[0] + 'I'+nControlRoot
        """
        con=GenControl(name)
        con[nStickyOrg] = 0.0
        con[nAmplitude] = 0.1
        AddOszDriverRot(obj,name)
        return {'FINISHED'}
    

class EmbedInHAOperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.embedinhaoperator"
    bl_label = "MakeHAChild"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        name = obj.name
        pobj = GenHAControl(name,5)
        pobj.location = obj.location
        obj.parent = pobj
        AddHAdriver(obj,name)
        return {'FINISHED'}

class EmbedInOszOperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.embedinoszoperator"
    bl_label = "MakeOszChild"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        name = obj.name
        pobj = GenControl(name)
        pobj.location = obj.location
        obj.parent = pobj
        AddOszDrivere(obj,name)
        return {'FINISHED'}





class duposzoperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.duposzoperator"
    bl_label  = "DupOszDriver"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        name = obj.name
        pp=obj.name.partition(nControlRoot)
        if (len(pp[1])>0):
            for i in range(1,10):
             nname = pp[0] +'_' +str(i)
             testobj = bpy.data.objects.get(nname+nControlRoot)
             if (testobj is None):
              GenControl(nname)
              OszCopyFromOther(nname,pp[0])
              obj[nCopyFrom]=nname  
              obj[nCopyTo]=nname  
              break
             else:
              print(testobj.name + ' exists')
            
        return {'FINISHED'}

class copyoszoperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.copyoszoperator"
    bl_label  = "Pull"

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            obj = context.object
            pp=obj.name.partition(nControlRoot)
            if (len(pp[1])>0):
                othername = obj[nCopyFrom]
                testobj = bpy.data.objects.get(othername+nControlRoot)
                if (testobj is not None):
                    return(1) 
        return(0)
            


    def execute(self, context):
        obj = context.object
        name = obj.name
        pp=obj.name.partition(nControlRoot)
        if (len(pp[1])>0): # am osz at all
          othername = obj[nCopyFrom]     
          testobj = bpy.data.objects.get(othername+nControlRoot)
          if (testobj is not None):
               OszCopyFromOther(pp[0],othername)
               print('copy ' + pp[0] + ' <--' +  othername)    
          else:
               print('OOPS?' + othername)     
                
        return {'FINISHED'}
    
    
class copyoszoperatorto(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.copytooszoperator"
    bl_label  = "Push"

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            obj = context.object
            pp=obj.name.partition(nControlRoot)
            if (len(pp[1])>0):
                try:
                    othername = obj[nCopyTo]
                    testobj = bpy.data.objects.get(othername+nControlRoot)
                    if (testobj is not None):
                        return(1) 
                except:
                    #expectet case no target
                    return(0)
        return(0)



    def execute(self, context):
        obj = context.object
        name = obj.name
        pp=obj.name.partition(nControlRoot)
        if (len(pp[1])>0): # am osz at all
          othername = obj[nCopyTo]     
          testobj = bpy.data.objects.get(othername+nControlRoot)
          if (testobj is not None):
               OszCopyFromOther(othername,pp[0])
               print('copy ' + pp[0] + ' --> ' +  othername)    
          else:
               print('OOPS?' + othername)     
                
        return {'FINISHED'}




class SetAmpAll(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.setampall"
    bl_label  = "SetAmpAll"
    
    @classmethod
    def poll(self, context):
        has_amp = 0
        ao = context.active_object
        try:
            amp= ao[nAmplitude]
            has_amp=1
        except:  
            has_amp=0            
        return (has_amp!=0)


    def execute(self, context):
        ao = context.active_object
        amp = 1.0
        amp= ao[nAmplitude] 
        print(amp)        
        for ob in context.selected_objects:
            name = ob.name
            pp=ob.name.partition(nControlRoot)
            if (len(pp[1])>0):
                print(name)
                ob[nAmplitude]=amp
        return {'FINISHED'}

class SetFramesAll(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.setframesall"
    bl_label  = "SetFramesAll"

    @classmethod
    def poll(self, context):
        has_f = 0
        ao = context.active_object
        try:
            amp= ao[nFrames]
            has_f=1
        except:  
            has_f=0            
        return (has_f!=0)
    
    def execute(self, context):
        ao = context.active_object
        fr = 40
        fr= ao[nFrames] 
        print(fr)        
        for ob in context.selected_objects:
            name = ob.name
            pp=ob.name.partition(nControlRoot)
            if (len(pp[1])>0):
                print(name)
                ob[nFrames]=fr
        return {'FINISHED'}

class SetShiftAll(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.setshiftall"
    bl_label  = "SetShiftAll"

    @classmethod
    def poll(self, context):
        has_f = 0
        ao = context.active_object
        try:
            shift= ao[nShift]
            has_s=1
        except:  
            has_s=0            
        return (has_s!=0)
    
    def execute(self, context):
        ao = context.active_object
        sh = 0
        sh= ao[nShift] 
        print(sh)        
        for ob in context.selected_objects:
            name = ob.name
            pp=ob.name.partition(nControlRoot)
            if (len(pp[1])>0):
                print(name)
                ob[nShift]=sh
        return {'FINISHED'}
    
class SetLissajous(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.setlissajous"
    bl_label  = "SetLissajous"

    @classmethod
    def poll(self, context):
        has_l = 0
        ao = context.active_object
        try:
            dummy = ao[nLissajousCos1x]
            has_l=1
        except:  
            has_l=0            
        return (has_l!=0)
    
    def execute(self, context):
        scale = 1.0
        ao = context.active_object
        try:
            scale = ao[nLissajousScale] 

        except: 
            ao[nLissajousScale] = 1.0        
        for ob in context.selected_objects:
            name = ob.name
            pp=ob.name.partition(nControlRoot)
            if (len(pp[1])>0):
                print('to do->SetLissajous')
                truncname =(pp[0])
                print(truncname)
                targetobj = bpy.data.objects.get(truncname+nCSin1)
                if (targetobj is not None):
                    targetobj.location[0] = scale * ao[nLissajousSin1x]
                    targetobj.location[1] = scale * ao[nLissajousSin1y]
                    targetobj.location[2] = scale * ao[nLissajousSin1z]
                targetobj = bpy.data.objects.get(truncname+nCCos1)
                if (targetobj is not None):
                    targetobj.location[0] = scale * ao[nLissajousCos1x]
                    targetobj.location[1] = scale * ao[nLissajousCos1y]
                    targetobj.location[2] = scale * ao[nLissajousCos1z]

                targetobj = bpy.data.objects.get(truncname+nCSin2)
                if (targetobj is not None):
                    targetobj.location[0] = scale * ao[nLissajousSin2x]
                    targetobj.location[1] = scale * ao[nLissajousSin2y]
                    targetobj.location[2] = scale * ao[nLissajousSin2z]
                    
                targetobj = bpy.data.objects.get(truncname+nCCos2)
                if (targetobj is not None):
                    targetobj.location[0] = scale * ao[nLissajousCos2x]
                    targetobj.location[1] = scale * ao[nLissajousCos2y]
                    targetobj.location[2] = scale * ao[nLissajousCos2z]
                    
                #Doit here
        return {'FINISHED'}
    
class GetLissajous(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.getlissajous"
    bl_label  = "getLissajous"

    @classmethod
    def poll(self, context):
        return (1)
    
    def execute(self, context):
        scale = 1.0
        ao = context.active_object
        try:
            scale = ao[nLissajousScale] 

        except: 
            ao[nLissajousScale] = 1.0

        frames=bpy.context.scene.frame_end
        
        for ob in context.selected_objects:
            name = ob.name
            pp=ob.name.partition(nControlRoot)
            if (len(pp[1])>0):
                print('to do->SetLissajous')
                truncname =(pp[0])
                print(truncname)
                targetobj = bpy.data.objects.get(truncname+nCSin1)
                if (targetobj is not None):
                    ao[nLissajousSin1x] = targetobj.location[0] / scale
                    ao[nLissajousSin1y] = targetobj.location[1] / scale
                    ao[nLissajousSin1z] = targetobj.location[2] / scale

                targetobj = bpy.data.objects.get(truncname+nCCos1)
                if (targetobj is not None):
                    ao[nLissajousCos1x] = targetobj.location[0] / scale
                    ao[nLissajousCos1y] = targetobj.location[1] / scale
                    ao[nLissajousCos1z] = targetobj.location[2] / scale

                targetobj = bpy.data.objects.get(truncname+nCSin2)
                if (targetobj is not None):
                    ao[nLissajousSin2x] = targetobj.location[0] / scale
                    ao[nLissajousSin2y] = targetobj.location[1] / scale
                    ao[nLissajousSin2z] = targetobj.location[2] / scale

                targetobj = bpy.data.objects.get(truncname+nCCos2)
                if (targetobj is not None):
                    ao[nLissajousCos2x] = targetobj.location[0] / scale
                    ao[nLissajousCos2y] = targetobj.location[1] / scale
                    ao[nLissajousCos2z] = targetobj.location[2] / scale                    
                #Doit here
        return {'FINISHED'}






class OpUpdateOszDriverProps(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.updateoszdriverprops"
    bl_label = "ExpandOszDriverProps"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        name = obj.name
        pp=obj.name.partition(nControlRoot)
        if (len(pp[1])>0):
            try:
             frames =  obj[nFrames]
            except: 
             obj[nFrames] = 40
            try:
             shift  =  obj[nShift ] 
            except: 
             obj[nShift ] = 0.0         
            try:
             amp = obj[nAmplitude] 
            except: 
             obj[nAmplitude] = 1.0
             
            try:
             fo = obj[nStickyOrg] 
            except: 
             obj[nStickyOrg] = 1.0

            try:
             on = obj[nCopyFrom] 
            except: 
             obj[nCopyFrom] = ""
            try:
             on = obj[nCopyTo] 
            except: 
             obj[nCopyTo] = ""

            print(name + "Update done")
        else:
            print("nothing to update")
        return {'FINISHED'}


class op_Enable_Watch(Operator):
    """Makes watch option available"""
    #bl_idname no upper Case allowed!
    bl_idname = "object.op_enable_watch"
    bl_label = "Add_Watcher"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        obj[nIDHAWatch] = '*None*'
        #setup scene props on the fly
        sce = bpy.context.scene
        try:
            v = sce[nHA_Damp]
        except:
            sce[nHA_Damp] = 1.
        try:
            v = sce[nHA_Frames]
        except:
            sce[nHA_Frames] = 2*2*4*5*7
        return {'FINISHED'}
        
class op_HA_Integrate(Operator):
    """Makes watch option available"""
    #bl_idname no upper Case allowed!
    bl_idname = "object.op_haintegate"
    bl_label = "Integate"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        sce = bpy.context.scene
        sce[nHA_Damp] = 1.
        try:
          nof_loops = sce[nHA_Loops]
        except:
          nof_loops = 20
          sce[nHA_Loops] = nof_loops



        for loop in range (1 , nof_loops+1):
            print("HA_Integratin loop",loop)
            _runCycleOnce()
            sce[nHA_Damp] = loop
        return {'FINISHED'}
        

        


class HA_Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "HA_Panel"
    bl_idname = "OBJECT_PT_HarmonicAnalysis"
    if (False): #option to have it in the prop panel    
        bl_space_type = 'PROPERTIES'
        bl_region_type = 'WINDOW'
        bl_context = "object"
    else:
        bl_context = "object"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'


    @classmethod
    def poll(cls, context):
        obj = context.object

        res = False
        if (obj):
            c_test = OszControl
            b_result = not c_test.objHasHAParent(obj)
            res = b_result
        return res   

    def draw(self, context):
        obj = context.object
        sce = bpy.context.scene
        layout = self.layout
        row = layout.row()
        pp=obj.name.partition(nHARoot)
        if (len(pp[1])>0): 
            try:
                    v = obj[nIDHAWatch] #provoce error
                    row.prop(sce, '["%s"]' % (nHA_Damp),text="Damp") 
                    row.prop(sce, '["%s"]' % (nHA_Frames),text="Frames")
                    row = layout.row()
                    row.prop(obj, '["%s"]' % (nIDHAWatch),text="Watch") 
                    row.operator("object.addhookdriveroperator")
    
            except:
                    row.label('NoWatcher') 
                    row.operator("object.op_enable_watch")
            row = layout.row()
            row.operator("object.op_osz2json")
            row.operator("object.op_json2osz")
            row = layout.row()
            row.prop(sce, '["%s"]' % (nHA_Loops),text="Loops") 
            row.operator("object.op_haintegate",text='Integate brute force')
            row.operator("object.removehookdriveroperator",text='UnHookDrivers')
        else:
            c_test = OszControl
            b_result = c_test.objIsHA(obj)
            if (not b_result):
                row.operator('object.embedinhaoperator') 
            else:
                row.label(text=(" Attached to " + obj.name + nHARoot))

 



class LissajousPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "LissajousPanel"
    bl_idname = "OBJECT_PT_LISSAJOUSGP"
    #bl_space_type = 'PROPERTIES'
    #bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (obj is not None):
            sce = bpy.context.scene
            pp=obj.name.partition(nControlRoot)
            return (len(pp[1])>0)
        else:
            return False

    def draw(self, context):
         obj = context.object
         sce = bpy.context.scene
         layout = self.layout
         pp=obj.name.partition(nControlRoot)
         if (len(pp[1])>0):
            row = layout.row(align=True)
            row.label('sin(t)')
            row.prop(obj, '["%s"]' % (nLissajousSin1x),text="X") 
            row.prop(obj, '["%s"]' % (nLissajousSin1y),text="Y") 
            row.prop(obj, '["%s"]' % (nLissajousSin1z),text="Z") 

            row = layout.row(align=True)
            row.label('cos(t)')
            row.prop(obj, '["%s"]' % (nLissajousCos1x),text="X") 
            row.prop(obj, '["%s"]' % (nLissajousCos1y),text="Y") 
            row.prop(obj, '["%s"]' % (nLissajousCos1z),text="Z") 
                        
            row = layout.row(align=True)
            row.label('sin(2t)')
            row.prop(obj, '["%s"]' % (nLissajousSin2x),text="X") 
            row.prop(obj, '["%s"]' % (nLissajousSin2y),text="Y") 
            row.prop(obj, '["%s"]' % (nLissajousSin2z),text="Z") 
            
            row = layout.row(align=True)            
            row.label('cos(2t)')
            row.prop(obj, '["%s"]' % (nLissajousCos2x),text="X") 
            row.prop(obj, '["%s"]' % (nLissajousCos2y),text="Y") 
            row.prop(obj, '["%s"]' % (nLissajousCos2z),text="Z") 

            row = layout.row()
            row.prop(obj, '["%s"]' % (nLissajousScale),text="Scale") 
            row.operator("object.setlissajous")
            row.operator("object.getlissajous")
            row = layout.row()
            row.operator("object.op_osz2json")
            row.operator("object.op_json2osz")

         
class CycleGenPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "OscGenPanel"
    bl_idname = "OBJECT_PT_CGP"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
         obj = context.object
         layout = self.layout
         pp=obj.name.partition(nControlRoot)
         if (len(pp[1])>0):
            row = layout.row()
            row.prop(obj, '["%s"]' % (nCopyFrom),text="Source") 
            row.operator("object.copyoszoperator")
            row = layout.row()
            row.prop(obj, '["%s"]' % (nCopyTo),text="Target") 
            row.operator("object.copytooszoperator")
            row = layout.row()
            row.operator("object.duposzoperator")

            row = layout.row()
            row.prop(obj, '["%s"]' % (nAmplitude),text="Amp") 
            row.prop(obj, '["%s"]' % (nFrames),text="Frames") 
            row.prop(obj, '["%s"]' % (nShift),text="Shift") 
            row = layout.row()
            row.operator("object.setampall")
            row.operator("object.setframesall")
            row.operator("object.setshiftall")
        
            row = layout.row()
            row.operator("object.updateoszdriverprops")
                
            if (bpy.data.objects.get(nControlRoot) is not None):
                row.operator("object.copyoszroot_operator")
         row = layout.row()
         c_test = OszControl
         b_result = c_test.objIsOsz(obj)
         if (not b_result):
             row.operator("object.embedinhaoperator")
             row.operator("object.embedinoszoperator")
             row.operator("object.addoszdriveroperator")
             row.operator("object.adrotdoszdriveroperator")
         else:
             row.label(text=(" Attached to " + obj.name + nControlRoot))
             row = layout.row()
             row.label(text=(" ToDo : Update Display Path"))
         
class HAMenu(bpy.types.Menu):
    bl_label = "HAMenu"
    bl_idname = "OBJECT_MT_HA_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.embedinhaoperator")

def draw_HAMenu(self, context):
    layout = self.layout
    layout.menu(HAMenu.bl_idname)




# Put Classes to publish here 
_myclasses = (
              CopyOszRootOperator,
              CycleGenPanel,
              LissajousPanel,
              HA_Panel,
              SetLissajous,
              GetLissajous,
              EmbedInOszOperator,
              EmbedInHAOperator,
              AddOszDriverOperator,
              AddRotOszDriverOperator,
              OpUpdateOszDriverProps,
              duposzoperator,
              op_osz2Json,
              op_json2Osz,
              op_osz_hook_ha,
              op_osz_unhook_ha,
              op_Enable_Watch,
              op_HA_Integrate,
              copyoszoperator,
              copyoszoperatorto,
              SetAmpAll,
              SetFramesAll,
              SetShiftAll,
              HAMenu
              ) 
                

def register():
    bpy.app.driver_namespace["oscAxisID"] = oscAxisID
    bpy.app.driver_namespace["oscAxisIDe"] = oscAxisIDe
    bpy.app.driver_namespace["drv_cumHaFi"] = drv_cumHaFi
    bpy.app.driver_namespace["drv_HAAxisID"] = drv_HAAxisID

    for cls in _myclasses :
        bpy.utils.register_class(cls)
    #can't find why this is added twice --- this is the only spot 
    #bpy.types.VIEW3D_MT_object.append(draw_HAMenu)


def unregister():
    for cls in _myclasses :
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object.remove(draw_HAMenu)
    print("Unregistered OszHAV2 .. ")

#run from run
if __name__ == "__main__":
    GenControl('')
    register()
    test=_driverCumHaFi('sin',1,0 ,'Test')
    print('Test',test)
    print('register is done')
else:
    register()
    GenControl('')
    print('OszHYV2 register done')
