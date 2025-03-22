# This script defines functions to be used directly in drivers expressions to
# extend the builtin set of python functions.
#
# This can be executed on manually or set to 'Register' to
# initialize thefunctions on file load.

import bpy
import math
from math import sin, cos, sqrt, radians
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

# empty_draw_type [‘PLAIN_AXES’, ‘ARROWS’, ‘SINGLE_ARROW’, ‘CIRCLE’, ‘CUBE’, ‘SPHERE’, ‘CONE’, ‘IMAGE’]

# this next part forces a reload in case you edit the source after you first start the blender session
import importlib
importlib.reload(BVT)

from BVT import *


nIDHAWatch    = "IDHAWatch"
nHA_Damp      = "HA_Damp"
nHA_Loops     = "HA_Loops"
nControlRoot = "ControlRoot"
nHARoot      = "HARoot"
nHAPlayBackOrder  = "HAPlayBackOrder"

nHASin        = "HASin"
nHACos        = "HACos" 
nHAOrder      = "HAOrder" 
nCSin1       = "CSin1"
nCCos1       = "CCos1" 
nCSin2       = "CSin2"
nCCos2       = "CCos2" 


nFrames      = "Osz_Frames"
nShift       = "Osz_Shift"
nAmplitude   = "Osz_Amplitude"
nStickyOrg   = "Osz_StickyOrg"
nCopyFrom    = "Osz_CopyFrom"
nCopyTo      = "Osz_CopyTo"
nClock       = "Osz_Clock"

nDefaultPeriod =2*2*3*5*7

nControlDefaultDefaultShape = "SPHERE"

def completescene():
    scene = bpy.context.scene
    try:
        v = scene[nHAPlayBackOrder]
    except:
        scene[nHAPlayBackOrder] = 100


def _runCycleOnce():
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end
    actual = start
    bpy.context.scene.frame_set(actual)
    while (actual < end + 1):
     msg =  "actual:{:}/{:}".format(actual,end)
     print(msg,end="\r")
     bpy.context.scene.frame_set(actual)
     actual += 1


def oszUniqueName(namein):
        name = namein
        pp=name.partition(nControlRoot)
        if (len(pp[1])>0):
            name = pp[0] + 'I'+nControlRoot
        return(name)   



def drv_HAAxisID(t,axis,ID):
    obj = bpy.data.objects.get(ID+nHARoot)
    if (not obj):
        return 0
    pa = obj.parent
    if (obj.parent is not None):
        try:
            frames = pa[nFrames]
            #brute force synchronizing
            obj[nFrames] = frames
        except:
            frames = obj[nFrames]
    else:
        frames = obj[nFrames]
    # half a potato sure you can make chef menu of it   
    if frames < 7 :
        return 0

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
        try:
            now = pa[nClock] 
        except:
            now = t
    try:
        nOrder = min(bpy.context.scene[nHAPlayBackOrder],nOrder)
    except:
        pass

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


def drv_cumHaFiDiff(axis,fu,n,ID,objorg,t,v):
    #calculate base fequency
    obj = bpy.data.objects.get(ID)
    #objorg = bpy.data.objects.get(IDorg)
    frames = objorg[nFrames]
    damp = bpy.context.scene[nHA_Damp]
    if damp > 999:
        return v
    if damp < 2: 
        return 0
    damp = HA.calcDamp(frames)
    timebase = frames/(2.*math.pi)
    magic = 2.
    f=(t)/timebase 
    c=0
    diffloc = obj.location[axis] - objorg.location[axis]
    if (fu == 'sin'): 
        c = magic*(diffloc) * sin(n*f)
    elif (fu == 'cos'): 
        c = magic*(diffloc) * cos(n*f)
    else:
        print('drv_cumHaFi fU?')
    r = ((damp-1)*v + c)/damp
    return r

def drv_cumLocDiff(axis,ID,objorg,t,v):
    #calculate base fequency
    obj = bpy.data.objects.get(ID)
    frames = objorg[nFrames]
    damp = HA.calcDamp(frames)
    if damp > 999:
        return v
    if (damp == 0): 
        return 0
    timebase = frames/(2.*math.pi)
    f=(t)/timebase 
    c = (obj.location[axis] - v)
    r = v + c/damp
    return r



def _driverCumHaFi(fu,n,index ,ID):
    txt = "drv_cumHaFiDiff({:},'{:}',{:},'{:}',self.parent,frame,self.location[{:}])".format(index,fu,n,ID,index)
    return txt
     

def add_driverCumHaFi(consumer,fu,n,index ,ID):
    d = consumer.driver_add( 'location', index ).driver
    d.use_self = True
    d.expression = _driverCumHaFi(fu,n,index ,ID) 

def add_driverLocDiff(consumer,index ,ID):
    d = consumer.driver_add( 'location', index ).driver
    d.use_self = True
    txt = "drv_cumLocDiff({:},'{:}',self,frame,self.location[{:}])".format(index,ID,index)
    d.expression = txt 
    
def _osz_hook_HA(consumer,IDwatched):
    name = consumer.name
    order = consumer[nHAOrder]
    pp=name.partition(nHARoot)
    prefix = pp[0]

    add_driverLocDiff(consumer,0,IDwatched)
    add_driverLocDiff(consumer,1,IDwatched)
    add_driverLocDiff(consumer,2,IDwatched)

    for o in range(1,order+1):
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
    consumer.driver_remove('location')
    for o in range(1,order+1):
        OName ="{:}{:}{:}".format(prefix,nHASin,o)
        cso = bpy.data.objects.get(OName)
        cso.driver_remove('location')
        OName ="{:}{:}{:}".format(prefix,nHACos,o)
        cso = bpy.data.objects.get(OName)
        cso.driver_remove('location')

def _osz_unhook_HAchildren(parent):
    for child in parent.children:
        try :
            # _osz_unhook_HA(child) throws exeption when child has no nHAOrder prop so no extra checks here
            _osz_unhook_HA(child)
            del child[nIDHAWatch]
        except :
            continue


class op_osz_unhook_hachildren(bpy.types.Operator):
    bl_idname = "object.op_oszunhookhachildren"
    bl_label = "DetachWatch"

    def execute(self,context):
        obj = context.object
        _osz_unhook_HAchildren(obj)
        return{'FINISHED'}

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
        _osz_unhook_HA(obj)
        return{'FINISHED'}
    
 
class HA():

    def objIsOsz(obj):
        to_name = obj.name + nControlRoot
        Cobj = bpy.data.objects.get(to_name)
        if (Cobj is not None ):
            return True
        else:
            return False
    
    @staticmethod
    def generateHAprefix(name):
        for n in range(1,999):
            prefix = "HA{:}".format(n)
            to_name = prefix +'_'+name
            Cobj = bpy.data.objects.get(to_name)
            if Cobj is None:
                return prefix + '_'
        return None



    @staticmethod
    def _objNameTaggedHA(obj):
        name = obj.name
        pp=name.partition(nHARoot)
        if (len(pp[1])>0):
            return True
        else:
            return False 

    @staticmethod
    def calcDamp(frames):
        damp = frames/2 * bpy.context.scene[nHA_Damp]
        return damp
    
    @staticmethod
    def PlotChildrenSpectrum(obj):
        i = 0
        arrsum = np.array([0.0])
        nSpec = 'Spec'
        pa = bpy.data.objects.get(nSpec)
        if pa is None:
            pa = createEmpty(nSpec,0.1,'ARROWS')
            pa.location[0] = 0.0
            pa.location[1] = 1.0
            pa.location[2] = 0.0
        for child in pa.children:
            deleteObject(child.name)
        
        for child in obj.children:
            res = HA.getObjSpectrum(child)
            pp  = child.name.partition(nHARoot)
            newname = pp[0]


            #print
            if (False):
                s = []
                for data in res:
                    t = '{:6.3f}'.format(data)
                    s.append(t)
                print(s,child.name)
                #plot
            if len(res) > 2:
                i +=1
                if(True):
                    plt = plot_spec(res,'SP_'+newname)
                    plt.location[1] = i * 0.05
                    plt.parent = pa
            #add
            a1=np.array(arrsum)
            a2=np.array(res)
            arrsum = a1+a2
        arrsum = arrsum/i
        #print(arrsum)
        plt = plot_spec(arrsum,'Average')
        plt.location[1] = -0.1
        plt.location[0] = i*0.05
        plt.parent = pa
        return arrsum

    @staticmethod
    def getChildrenSpectrumAverage(obj):
        i = 0
        arrsum = np.array([0.0])
        for child in obj.children:
            res = HA.getObjSpectrum(child)
            if len(res) > 2:
                i +=1
            a1=np.array(arrsum)
            a2=np.array(res)
            arrsum = a1+a2
        arrsum = arrsum/i
        return arrsum

    


    @staticmethod
    def getObjSpectrum(obj):
        res = [0.0]
        try:
            order = obj[nHAOrder]
        except:
            return(res)
            
        pp=obj.name.partition(nHARoot)
        prefix = pp[0]
        for o in range(1,order+1):
            res.append(0.0)
            OName ="{:}{:}{:}".format(prefix,nHASin,o)
            cso = bpy.data.objects.get(OName)
            x = cso.location[0]
            y = cso.location[1]
            z = cso.location[2]
            res[o] = sqrt(x*x+y*y+z*z)
            OName ="{:}{:}{:}".format(prefix,nHACos,o)
            cso = bpy.data.objects.get(OName)
            x = cso.location[0]
            y = cso.location[1]
            z = cso.location[2]
            res[o] += sqrt(x*x+y*y+z*z)
        return(res)

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

    @classmethod
    def objHasHACildren(self,obj):
        for child in obj.children:
            if self._objNameTaggedHA(child):
                return True
        return False

def plot_spec(data,Name):
    # Set curve coordinates
    points = np.zeros((len(data), 3))
    for N in range(len(data)):
        x = 0.1 * N
        y = 0
        z = data[N]
        points[N] = [x, y, z]

    # Create the curve and set its points
    curve_data = bpy.data.curves.new(name=Name, type='CURVE')

    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(points) - 1)

    for N in range(len(points)):
        x, y, z = points[N]
        polyline.points[N].co = (x, y, z, 1)

    curve_object = bpy.data.objects.new(Name, curve_data)
    bpy.context.scene.objects.link( curve_object )
    return curve_object

    #bpy.context.collection.objects.link(curve_object)

    
    

def GenHAControl(ID,nOrder):
     w_empty_draw_size = 0.1
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
         obj.hide = True
         obj.parent = Cobj
        OName ="{:}{:}{:}".format(ID,nHACos,order)
        obj = bpy.data.objects.get(OName)
        if (not obj):
         obj = createEmpty(OName,w_empty_draw_size,'ARROWS')
         obj.hide = True
         obj.parent = Cobj

     return(Cobj)
     


def AddHAdriver(source,ID):
    for n in range(3):
        d = source.driver_add( 'location', n ).driver
        d.expression = "drv_HAAxisID(frame,"+str(n)+",'"+ID+"')" 

    
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

def _copy_toHA_make_all_children_watch(obj,order,frames):
    paName=obj.name
    prefix=HA.generateHAprefix(paName)
    newParent = createEmpty(prefix+paName,0.1,'PLAIN_AXES')
    newParent[nFrames] = frames
    try:
        newParent['~armature'] = obj['~armature']
        newParent['skeleton'] = obj['skeleton']
        newParent['metrabs'] = obj['metrabs']
    except:
        pass

    for child in obj.children :
        chName=child.name


        newchild = createEmpty(prefix+chName,0.1,'CUBE')
        pobj = GenHAControl(newchild.name,order)
        pobj.location = obj.location
        pobj.parent = newParent
        pobj[nFrames] = frames
        newchild.parent = pobj
        AddHAdriver(newchild,newchild.name)


        pobj[nIDHAWatch] = chName
        _osz_hook_HA(pobj,chName)
    return {'FINISHED'} 

class EmbedChildrenHAOperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.embedchildrehaoperator"
    bl_label = "Make_All_Children_HA"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        sce = bpy.context.scene        
        try:
            order = sce[nHAOrder]
        except:
            order = 5
            sce[nHAOrder] = order
        try:
            frames = sce[nFrames]
        except:
            frames = 40
            sce[nFrames] = frames

        return _copy_toHA_make_all_children_watch(obj,order,frames)


    





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

    

class EmbedInHAOperator(bpy.types.Operator):
    #bl_idname no upper Case allowed!
    bl_idname = "object.embedinhaoperator"
    bl_label = "MakeHAChild"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        sce = bpy.context.scene

        try:
            order = sce[nHAOrder]
        except:
            order = 5
            sce[nHAOrder] = order

        name = obj.name
        pobj = GenHAControl(name,order)
        pobj.location = obj.location
        obj.parent = pobj
        AddHAdriver(obj,name)
        return {'FINISHED'}

class op_Print_Object_Spectrum(Operator):
    """Makes watch option available"""
    #bl_idname no upper Case allowed!
    bl_idname = "object.op_pso"
    bl_label = "Print_Object_Spectrum"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        res = HA.getObjSpectrum(obj)
        s = []
        for data in res:
            t = '{:6.3f}'.format(data)
            s.append(t)
        print(obj.name,s)
        plot_spec(res,'SP_'+obj.name)
        return {'FINISHED'}

class op_Print_Chidren_Spectrum(Operator):
    """Makes watch option available"""
    #bl_idname no upper Case allowed!
    bl_idname = "object.op_psc"
    bl_label = "Print_Object_Spectrum"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.object
        HA.PlotChildrenSpectrum(obj)
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
            v = sce[nHA_Loops]
        except:
            sce[nHA_Damp] = 1
            sce[nHA_Loops] = 1
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
        obj = context.object
        errlimit = 0.000001
        #sce[nHA_Damp] = 1.
        storePBO = sce[nHAPlayBackOrder]
        sce[nHAPlayBackOrder] = 0
        try:
          nof_loops = sce[nHA_Loops]
        except:
          nof_loops = 1
          sce[nHA_Loops] = nof_loops


        specPrev=HA.getChildrenSpectrumAverage(obj)
        #print('old')
        #print(specPrev)
        for loop in range (1 , nof_loops+1):
            print("HA_Integratin loop",loop,end='\r')
            _runCycleOnce()
            print('dif')
            specNow=HA.getChildrenSpectrumAverage(obj)
            a1 = np.array(specPrev)
            a2 = np.array(specNow)
            dif = a1 -a2
            max = dif.max()
            min = dif.min()
            err = max-min
            print('E',err,'L',errlimit)
            if (err < errlimit):
                break
            #print(dif)
            specPrev = specNow
            # todo find better shedule
            # sce[nHA_Damp] = sce[nHA_Damp] +1
        sce[nHAPlayBackOrder] = storePBO
        HA.PlotChildrenSpectrum(obj)
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
            b_result = (not HA.objHasHAParent(obj) or HA.objHasHACildren(obj)) and (obj.type == 'EMPTY')
            res = b_result
        return res   

    def draw(self, context):
        obj = context.object
        sce = bpy.context.scene
        layout = self.layout
        row = layout.row()
        pp=obj.name.partition(nHARoot)
        watch = 0
        if (len(pp[1])>0): 
            try:
                    v = obj[nIDHAWatch] #provoce error
                    row.prop(sce, '["%s"]' % (nHA_Damp),text="Damp") 
                    row = layout.row()
                    row.prop(obj, '["%s"]' % (nIDHAWatch),text="Watch") 
                    row.operator("object.addhookdriveroperator")
                    watch = 1 
    
            except:
                    row.label('NoWatcher') 
                    row.operator("object.op_enable_watch")

            row = layout.row()
            row.operator("object.op_osz2json")
            row.operator("object.op_json2osz")
            row.operator("object.op_pso")
            row = layout.row()
            if watch :
                row.prop(sce, '["%s"]' % (nHA_Loops),text="Loops") 
                row.operator("object.op_haintegate",text='Integate brute force')
                row.operator("object.removehookdriveroperator",text='UnHookDrivers')
            layout.label(text='Object')
            row = layout.row()
            row.prop(obj, '["%s"]' % (nAmplitude),text="Amp") 
            row.prop(obj, '["%s"]' % (nFrames),text="Frames") 
            row.prop(obj, '["%s"]' % (nShift),text="Shift") 
        else:
            if HA.objHasHACildren(obj):
                #row.prop(obj, '["%s"]' % (nAmplitude),text="Amp") 
                row.prop(obj, '["%s"]' % (nFrames),text="Frames") 
                row.prop(sce, '["%s"]' % (nHA_Damp),text="Damp") 
                row.prop(sce, '["%s"]' % (nHAPlayBackOrder),text="PBO") 
                #row.prop(obj, '["%s"]' % (nShift),text="Shift")
                row = layout.row()
                row.prop(sce, '["%s"]' % (nHA_Loops),text="Loops")
                row.operator("object.op_haintegate",text='Integate brute force')
                row = layout.row()
                row.operator("object.op_oszunhookhachildren",text='WatchDetach')
                row = layout.row()
                row.operator("object.op_psc",text='PSC')
            else:
                row = layout.row()
                if len(obj.children) > 0:
                    row.prop(sce, '["%s"]' % (nHAOrder),text="HAO") 
                    row.operator("object.embedchildrehaoperator") 
                if (not HA.objIsHA(obj)):
                    row = layout.row()
                    row.operator('object.embedinhaoperator') 
                else:
                    row.label(text=(" Attached to " + obj.name + nHARoot))


# Put Classes to publish here 
_myclasses = (
              HA_Panel,
              EmbedInHAOperator,
              op_osz2Json,
              op_json2Osz,
              op_osz_hook_ha,
              op_osz_unhook_ha,
              op_Enable_Watch,
              op_HA_Integrate,
              EmbedChildrenHAOperator,
              op_osz_unhook_hachildren,
              op_Print_Object_Spectrum,
              op_Print_Chidren_Spectrum
              ) 
                

def register():
    bpy.app.driver_namespace["drv_HAAxisID"] = drv_HAAxisID
    bpy.app.driver_namespace["drv_cumHaFiDiff"] = drv_cumHaFiDiff
    bpy.app.driver_namespace["drv_cumLocDiff"] = drv_cumLocDiff

    for cls in _myclasses :
        bpy.utils.register_class(cls)
    completescene()
    #can't find why this is added twice --- this is the only spot 
    #bpy.types.VIEW3D_MT_object.append(draw_HAMenu)

def unregister():
    for cls in _myclasses :
        bpy.utils.unregister_class(cls)
    #bpy.types.VIEW3D_MT_object.remove(draw_HAMenu)
    print("Unregistered OszHAV2 .. ")

#run from run
if __name__ == "__main__":
    register()
    test=_driverCumHaFi('sin',1,0 ,'Test')
    print('Test',test)
    print('register is done')
else:
    register()
    print('OszHYV2 register done')
