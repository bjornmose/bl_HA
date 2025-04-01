import bpy


'''
wrapper to create Epmties along the 'python API debelopers moods'
'''

def createEmpty(OName,draw_size,draw_type):
    #print('Create {:}'.format(OName))
    Cobj = bpy.data.objects.new( OName, None )
    ver = bpy.app.version[1]
    ver0 = bpy.app.version[0]
    #print(ver)
    if (ver < 80 and ver0 < 3):
        bpy.context.scene.objects.link( Cobj )
        Cobj.empty_draw_size = draw_size
        Cobj.empty_draw_type = draw_type
        Cobj.show_name=1
    
    if (ver > 79 and ver0 < 3):
        bpy.context.scene.collection.objects.link( Cobj )
        Cobj.empty_display_size = draw_size
        Cobj.empty_display_type = draw_type
        Cobj.show_name=1

    if (ver < 99 and ver0 > 2):
        view_layer = bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link( Cobj )
        Cobj.empty_display_size = draw_size
        Cobj.empty_display_type = draw_type
        Cobj.show_name=1

    return Cobj   

def deleteObject35(name):
    try:
        objs = [bpy.context.scene.objects[name]]
        with bpy.context.temp_override(selected_objects=objs):
            bpy.ops.object.delete()
        return('FINISHED')
    except Exception as error:
        print('ERROR',error)
        print('NOT Deleted',name)
        return('FAILED')
    
    
def deleteObject(name):
    obj = bpy.data.objects.get(name)
    ver = bpy.app.version[1]
    ver0 = bpy.app.version[0]
    #print(ver)
    if (ver < 80 and ver0 < 3):
     if (obj is not None):
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        # Select the object
        bpy.data.objects[name].select = True    # Blender 2.7x        
        # Delete the object
        bpy.ops.object.delete() 
        #print('deleted',name)
        return('FINISHED')
        
    if (ver < 99 and ver0 > 2):
     try:
        objs = [bpy.context.scene.objects[name]]
        with bpy.context.temp_override(selected_objects=objs):
            bpy.ops.object.delete()
        print('deleted',name)
        return('FINISHED')
     except Exception as error:
        print('ERROR',error)
        print('NOT Deleted',name)
        return('FAILED')

def create_armature(name,bonename):
    C = bpy.context
    D = bpy.data
    #Create armature object
    armature = D.armatures.new(name)
    armature_object = D.objects.new(name, armature)
    #Link armature object to our scene
    ver = bpy.app.version[1]
    ver0 = bpy.app.version[0]
    '''
    we need to select our new object and go to edit mode once
    '''
    if (ver < 99 and ver0 > 2):
        C.collection.objects.link(armature_object)
        armature_object.show_name=1 
        armature_data = D.objects[armature_object.name]
        C.view_layer.objects.active = armature_data
        armature_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        #bones = C.active_object.data.edit_bones

    if (ver > 79 and ver0 < 3):
        print('Sorry no 2.8x')
        return None

    
    if (ver < 80 and ver0 < 3):
        C.scene.objects.link(armature_object)
        armature_object.show_name=1
        C.scene.objects.active = armature_object
        armature_object.select=True
        bpy.ops.object.mode_set(mode='EDIT')
        #bones = C.active_object.data.edit_bones
    '''
    bone = bones.new(bonename)
    bone.head = (0.,0.,0.)
    bone.tail = (0.,0.,1.)
    '''
    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_object
        

    
    

if __name__ == "__main__":
    createEmpty('CreateEmpty',0.5,'ARROWS')
