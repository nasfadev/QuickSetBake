# this is the metadata for the addon
bl_info = {
    "name": "QuickSetBake",
    "author": "Cisarp",
    "version": (1, 0),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > QuickSetBake",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

# this is the import of the required object
import bpy, datetime
from bpy.props import EnumProperty, PointerProperty, CollectionProperty, IntProperty
from bpy.types import Panel, PropertyGroup, UIList, Operator

# this is the name of the addon
AddOnName = "QuickSetBake"

# This is a data list for storing texture image objects and objects with type MESH
class ListData(PropertyGroup):
    mesh: PointerProperty(type=bpy.types.Object, name="Mesh")
    image: PointerProperty(type=bpy.types.Image, name="Image")

# This data is used to store the names of texture images, nodes, node frames, 
# but the name stored is the name that was stored when the code was executed so it will not change 
# if the names of the 3 names above are changed after they have been executed
class Data(PropertyGroup):
    textureName: bpy.props.StringProperty(name="textureName")
    nodeName: bpy.props.StringProperty(name="nodeName")
    frameNodeName: bpy.props.StringProperty(name="frameNodeName")

# this is panel ui
class QSB_PT_OBJECT_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddOnName
    bl_label = AddOnName
    bl_idname = "qsb.objectpanel"
    
    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        wm = context.window_manager
        box = layout.box()
        box.label(text="Select the Image Texture below")
        row = box.row()
        row.prop_search(wm, "image_enum", bpy.data, "images", icon="IMAGE_DATA", text="")
        row = box.row()
        row.operator("qsb.objectadditem", icon="ADD", text="Add")
        row.operator("qsb.objectdeleteitem", icon="REMOVE", text="Delete")
        listbox = box.template_list("QSB_UL_OBJECT_list", "",  context.scene, "MyListData", context.scene, "list_index")
        if listbox:
            listbox.add()
            listbox.delete()
        row = box.row()
        row.operator("qsb.objectreactivenodes", icon="NODETREE", text="Reactive Nodes")
        row = layout.row()
        row.operator("qsb.objectdeleteunusedmaterials", icon="MATERIAL", text="Delete Unused Material")

# this is the list that will be included in the ui panel
class QSB_UL_OBJECT_list(UIList):
    def draw_filter(self, context, layout):
        return False
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ii = item.image
        im = item.mesh
        if ii.preview != None and ii.preview.icon_id != None:
            layout.prop(ii, "name", text="", emboss=False, icon_value=ii.preview.icon_id)
        else:
            layout.prop(ii, "name", text="", emboss=False, icon="IMAGE_DATA")
        layout.prop(im, "name", text="", emboss=False, icon="OUTLINER_OB_MESH")

# this is a function to collect data.image
def enum_image_items(self, context):    
    """EnumProperty callback"""
    items = []
    for i, img in enumerate(bpy.data.images):
        items.append((img.name, img.name, "", i))
    return items

# this is to add new data
class QSB_OT_OBJECT_add_item(Operator):
    """Select data from the input above to add new data to the list"""
    bl_idname = "qsb.objectadditem"
    bl_label = "Add Item"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object != None
    
    def execute(self, context):
        context.window_manager.image_enum = context.window_manager.image_enum
        image_enum = context.window_manager.image_enum
        object = context.active_object
        if object.type == "MESH":
            if object.material_slots:
                for item in context.scene.MyListData:
                    if item.image.name == image_enum and item.mesh.name == object.name:
                        self.report({'WARNING'}, f"{object.name} already has the {image_enum} texture image")
                        return {'CANCELLED'}
                item = context.scene.MyListData.add()
                item.mesh = bpy.context.scene.objects[context.active_object.name]
                item.image = bpy.data.images[context.window_manager.image_enum]
                index = context.scene.list_index
                AddNode(self, context, index)
                self.report({'INFO'},  f"{item.image.name} was successfully added to {item.mesh.name}")
                return {'FINISHED'}
            self.report({'WARNING'},  f"{object.name} has no materials")
            return {'CANCELLED'}
        self.report({'WARNING'},  f"{object.name} is an object of type {object.type} not MESH")
        return {'CANCELLED'}

# this is for deleting data
class QSB_OT_OBJECT_delete_item(Operator):
    """Select the data in the list below that you want to delete."""
    bl_idname = "qsb.objectdeleteitem"
    bl_label = "Delete Item"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.list_index >= 0

    def execute(self, context):
        index = context.scene.list_index
        if len(context.scene.MyListData) <= 0 :
            self.report({'WARNING'},  "The texture image is not available")
            return{'FINISHED'}
        try:
            data = context.scene.MyListData[index]
            DeleteNode(self, context, index)
            
            self.report({'INFO'},  f"{data.image.name} was successfully deleted from {data.mesh.name}")
            context.scene.MyListData.remove(index)
            return {'FINISHED'}
        except IndexError:
            self.report({'WARNING'},  "No image texture selected")
            return {'FINISHED'}

# this is to reactivate inactive nodes on active objects in the ui list
class QSB_OT_OBJECT_reactive_nodes(Operator):
    """Select the data in the list above that you want to reactivate the nodes that contain the texture image to bake.

Note : if you have already added data to the list and just added new material after adding data to the list, then new nodes will be added to your new material.

Important: the nodes that contain the texture image to be baked must be active if you want to bake, therefore you must run this command if your nodes are not active or you can do it manually"""
    
    bl_idname = "qsb.objectreactivenodes"
    bl_label = "Reactive Nodes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    
    def poll(cls, context):
        return context.active_object != None
    
    def execute(self, context):
        index = context.scene.list_index
        try:
            obj = context.scene.MyListData[index].mesh
            if len(context.scene.MyData) <= 0:
                self.report({'WARNING'},  "The texture image is not available")
                return{'FINISHED'}
            data = context.scene.MyData[index]
            material_slots = obj.material_slots
            image_name = data.textureName
            for material_slot in material_slots:
                material = material_slot.material
                if material:
                    material_node_tree = material.node_tree
                    texture_node = material.node_tree.nodes.get(data.nodeName)
                    if texture_node:
                        texture_node.select = True
                        material_node_tree.nodes.active = texture_node
                    elif texture_node != True:
                        nodeName = data.nodeName
                        frameNodeName = data.frameNodeName
                        material_node_tree = material.node_tree
                        texture_node = material_node_tree.nodes.new('ShaderNodeTexImage')
                        texture_node.name = nodeName
                        texture_node.location = (-400, 0)
                        texture_node.image = bpy.data.images[image_name]
                        texture_node.select = True
                        material_node_tree.nodes.active = texture_node
                        frame_node = material_node_tree.nodes.new('NodeFrame')
                        frame_node.name = frameNodeName
                        frame_node.label = image_name +" - "+ AddOnName
                        frame_node.location = (-450, 50)
                        frame_node.width = 400
                        frame_node.height = 300
                        frame_node.color = (0.105, 0, 1)
                        frame_node.use_custom_color = True
                        material_node_tree.nodes.active = frame_node
                        frame_node.select = True
                        material_node_tree.nodes.active = texture_node  
                        texture_node.parent = frame_node
            self.report({'INFO'},  f"The nodes in {obj.name} have been successfully reactive") 
            return{'FINISHED'}
        except IndexError:
            self.report({'WARNING'},  "No image texture selected")
            return {'FINISHED'}

# this is to delete material that is not used on the selected object, can delete material that is not used on many objects at once
class QSB_OT_OBJECT_delete_unused_materials(Operator):
    """Delete all unused material in your object, meaning if there are 10 materials in your object, and only 5 materials are used on each face in your object, then the 5 that are not used will be removed from your object, not deleted from blender, so the material is still in blender material data but it's not in the object you selected.

Note: you can delete unused material in multiple objects at once by selecting all the objects you want to delete unused material"""
    
    bl_idname = "qsb.objectdeleteunusedmaterials"
    bl_label = "Delete Unused Material"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object != None
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        objname = []
        objmat = []
        notMesh = []
        isNotMesh = False
        for obj in selected_objects:
            if obj.type != "MESH":
                print(obj.type)
                notMesh.append(obj.name)
                isNotMesh = True
                continue
            objname.append(obj.name)
            objmat.append(len(obj.material_slots))
        obj = context.active_object
        if isNotMesh :
            string = ""
            i = 0
            for item in notMesh:
                if i == len(notMesh) - 1:
                    string += f" {item} "
                    break
                string += f" {item},"
                i+=1
            self.report({'WARNING'},  f"There are objects that are not of type MESH ({string})")
            return {'CANCELLED'}
        bpy.ops.object.material_slot_remove_unused()
        string = "successfully removed "
        i = 0
        for obj in selected_objects:
            objmat[i] -= len(obj.material_slots)
            if i == len(objmat) - 1:
                string += f" {str(objmat[i])} from {objname[i]}"
                break
            string += f" {str(objmat[i])} from {objname[i]},"
            i+=1
        self.report({'INFO'},  string)
        return{'FINISHED'}

# this is additional function to delete nodes
def DeleteNode(self, context, index):
    obj = context.scene.MyListData[index].mesh
    scene = context.scene
    selectedTexture = context.scene.MyListData[index]
    item = context.scene.MyData[index]
    material_slots = obj.material_slots
    for material_slot in material_slots:
        material = material_slot.material 
        if material:
            texture_node = material.node_tree.nodes.get(item.nodeName)
            if texture_node:
                material.node_tree.nodes.remove(texture_node)
                texture_node2 = material.node_tree.nodes.get(item.frameNodeName)
                material.node_tree.nodes.remove(texture_node2)
    scene.MyData.remove(index)

# this is additional function to add nodes   
def AddNode(self, context, index):
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    obj = context.active_object
    scene = context.scene
    image_name = context.window_manager.image_enum
    material_slots = obj.material_slots
    custom_data_item = scene.MyData.add()
    for material_slot in material_slots:
        material = material_slot.material
        if material:
            nodeName = "Node_" + AddOnName + "_" + time_str
            frameNodeName =  "NodeFrame_" + AddOnName + "_" + time_str
            material_node_tree = material.node_tree
            texture_node = material_node_tree.nodes.new('ShaderNodeTexImage')
            texture_node.name = nodeName
            texture_node.location = (-400, 0)
            texture_node.image = bpy.data.images[image_name]
            texture_node.select = True
            material_node_tree.nodes.active = texture_node
            frame_node = material_node_tree.nodes.new('NodeFrame')
            frame_node.name = frameNodeName
            frame_node.label = image_name +" - "+ AddOnName
            frame_node.location = (-450, 50)
            frame_node.width = 400
            frame_node.height = 300
            frame_node.color = (0.105, 0, 1)
            frame_node.use_custom_color = True
            material_node_tree.nodes.active = frame_node
            frame_node.select = True
            material_node_tree.nodes.active = texture_node
            texture_node.parent = frame_node
    scene = context.scene
    custom_data_item.nodeName = nodeName
    custom_data_item.frameNodeName = frameNodeName
    custom_data_item.textureName = context.window_manager.image_enum

# This is the class name to be registered
classes = [ListData,Data,QSB_UL_OBJECT_list,QSB_OT_OBJECT_add_item,QSB_OT_OBJECT_delete_item,QSB_PT_OBJECT_panel,QSB_OT_OBJECT_reactive_nodes,QSB_OT_OBJECT_delete_unused_materials]

# this is register function
def register():
    from bpy.types import WindowManager
    WindowManager.image_enum = EnumProperty(
        items=enum_image_items,
        description="Select an image",
    )
    for reg in classes:
        bpy.utils.register_class(reg)
    bpy.types.Scene.MyListData = CollectionProperty(type=ListData)
    bpy.types.Scene.list_index = IntProperty(name="This is the list of data that you have added.", default=0)
    bpy.types.Scene.MyData = CollectionProperty(type=Data)

# this is unregister function
def unregister():
    from bpy.types import WindowManager
    del WindowManager.image_enum
    for unreg in classes:
        bpy.utils.unregister_class(unreg)
    del bpy.types.Scene.MyListData
    del bpy.types.Scene.list_index
    del bpy.types.Scene.MyData

# this is for registering
if __name__ == "__main__":
    register()
