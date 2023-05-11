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

import bpy
from bpy.types import Panel
from bpy.props import EnumProperty






import datetime
AddOnName = "QuickSetBake"
# Ambil waktu saat ini


# Buat objek baru


# Simpan array string ke dalam Custom Properties





class ListData(bpy.types.PropertyGroup):
    mesh: bpy.props.PointerProperty(type=bpy.types.Object)
    image: bpy.props.PointerProperty(type=bpy.types.Image)

class Data(bpy.types.PropertyGroup):
    textureName: bpy.props.StringProperty(name="textureName")
    nodeName: bpy.props.StringProperty(name="nodeName")
    frameNodeName: bpy.props.StringProperty(name="frameNodeName")
    indexTexture: bpy.props.IntProperty(name="indexTexture")

class MyCustomPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddOnName
    bl_label = AddOnName
    bl_idname = AddOnName.upper()+"_PT_panel"
    
    def draw(self, context):
        layout = self.layout

        scene = bpy.context.scene

        # Tampilkan properti pencarian dengan daftar objek di scene
        
        wm = context.window_manager

        
        
        box = layout.box()
        box.label(text="Select the Image Texture below")
        row = box.row()
        row.prop_search(wm, "image_enum", bpy.data, "images", icon="IMAGE_DATA", text="")



        row = box.row()
        row.operator("my_custom.add_item", icon="ADD", text="Add")
        row.operator("my_custom.delete_item", icon="REMOVE", text="Delete")
        # row.operator("my_custom.delete_item", icon="FILE_REFRESH", text="Recheck")
        listbox = box.template_list("MY_UL_list", "", context.scene, "MyListData", context.scene, "list_index")
        if listbox:
            listbox.add()
            listbox.delete()
        row = box.row()
        row.operator("my_custom.reactive_nodes", icon="NODETREE", text="Reactive Nodes")
        row = layout.row()
        row.operator("my_custom.delete_unused_material", icon="MATERIAL", text="Delete Unused Material")
class MY_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # layout.label(text=item.image.name, icon="IMAGE_DATA")
        # layout.label(text=item.mesh.name, icon="OUTLINER_OB_MESH")
        im = item.image
        io = item.mesh
        row = layout.row(align=True)
        row.prop(im, "name", text="", emboss=False, icon_value=im.preview.icon_id)
        row.prop(io, "name", text="", emboss=False, icon = "OUTLINER_OB_MESH")
    def draw(self, context):
        self.on_double_click(context.event)
def enum_image_items(self, context):    
    """EnumProperty callback"""
    items = []
    for i, img in enumerate(bpy.data.images):
        items.append((img.name, img.name, "", i))
    return items

class MY_OT_add_item(bpy.types.Operator):
    """Select data from the input above to add new data to the list"""
    bl_idname = "my_custom.add_item"
    bl_label = "Add Item"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        # Mengecek apakah nilai sudah ada di custom_list
        self.report({'INFO'},  "added")
        image_enum = context.window_manager.image_enum
        object = context.active_object
        if object.type == "MESH":
            if object.material_slots:
                for item in context.scene.MyListData:
                    if item.image.name == image_enum and item.mesh.name == object.name:
                        self.report({'WARNING'}, f"{object.name} already has the {image_enum} texture image")
                        return {'CANCELLED'}


                self.report({'INFO'},  "addedhmmmmmmm")
                item = context.scene.MyListData.add()
                self.report({'INFO'},  f"{len(context.scene.MyListData)}")
                item.mesh = bpy.context.scene.objects[context.active_object.name]
                item.image = bpy.data.images[context.window_manager.image_enum]
                self.report({'INFO'},  "addedh???")
                self.report({'INFO'},  f"{item.image.name}")
                # Menambahkan item baru pada custom_list
                index = context.scene.list_index
                AddNode(self, context, index)
                self.report({'INFO'},  f"{item.image.name} was successfully added to {item.mesh.name}")
                return {'FINISHED'}
            self.report({'WARNING'},  f"{object.name} has no materials")
            return {'CANCELLED'}
        self.report({'WARNING'},  f"{object.name} is an object of type {object.type} not MESH")
        return {'CANCELLED'}

class MY_OT_delete_item(bpy.types.Operator):
    """Select the data in the list below that you want to delete."""
    bl_idname = "my_custom.delete_item"
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
class ReactiveNode(bpy.types.Operator):
    """Select the data in the list above that you want to reactivate the nodes that contain the texture image to bake.

Note : if you have already added data to the list and just added new material after adding data to the list, then new nodes will be added to your new material.

Important: the nodes that contain the texture image to be baked must be active if you want to bake, therefore you must run this command if your nodes are not active or you can do it manually"""
    bl_idname = "my_custom.reactive_nodes"
    bl_label = "Reactive Nodes"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
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

                        # Seleksi dan buat node texture aktif
                        texture_node.select = True
                        material_node_tree.nodes.active = texture_node

                        # Buat frame node tree dengan nama yang sama dengan nama gambar
                        frame_node = material_node_tree.nodes.new('NodeFrame')
                        frame_node.name = frameNodeName
                        frame_node.label = image_name +" - "+ AddOnName
                        frame_node.location = (-450, 50)
                        frame_node.width = 400
                        frame_node.height = 300
                        frame_node.color = (0.105, 0, 1)
                        frame_node.use_custom_color = True
                        # Tambahkan node texture ke dalam frame
                        material_node_tree.nodes.active = frame_node
                        frame_node.select = True
                        material_node_tree.nodes.active = texture_node
                        
                        texture_node.parent = frame_node
            self.report({'INFO'},  f"The nodes in {obj.name} have been successfully reactive")
            return{'FINISHED'}
        except IndexError:
            self.report({'WARNING'},  "No image texture selected")
            return {'FINISHED'}
class DeleteUnusedMaterial(bpy.types.Operator):
    """Delete all unused material in your object, meaning if there are 10 materials in your object, and only 5 materials are used on each face in your object, then the 5 that are not used will be removed from your object, not deleted from blender, so the material is still in blender material data but it's not in the object you selected.

Note: you can delete unused material in multiple objects at once by selecting all the objects you want to delete unused material"""
    bl_idname = "my_custom.delete_unused_material"
    bl_label = "Delete Unused Material"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        obj = context.active_object
        matcount = len(obj.material_slots)
        bpy.ops.object.material_slot_remove_unused()
        if matcount == len(obj.material_slots):
            self.report({'INFO'},  "All materials have been used")
        matcount -= len(obj.material_slots)
        self.report({'INFO'},  f"Successfully removed {matcount} materials from {obj.name}")
        return{'FINISHED'}
#class Recheck(bpy.types.Operator):
    
def DeleteNode(self, context, index):
    obj = context.scene.MyListData[index].mesh
    scene = context.scene
    selectedTexture = context.scene.MyListData[index]
    item = context.scene.MyData[index]
    # Mengambil semua slot material pada objek
    material_slots = obj.material_slots

    # Looping melalui semua slot material dan menambahkan node image texture pada setiap material
    for material_slot in material_slots:
        # Mengambil material yang terkait dengan slot material
        material = material_slot.material 
        if material:
            # Membuat node image texture baru pada material
            texture_node = material.node_tree.nodes.get(item.nodeName)
            if texture_node:
                material.node_tree.nodes.remove(texture_node)
                texture_node2 = material.node_tree.nodes.get(item.frameNodeName)
                material.node_tree.nodes.remove(texture_node2)
    scene.MyData.remove(index)
        
def AddNode(self, context, index):
    now = datetime.datetime.now()

    # Format waktu menjadi string
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    # Mengambil objek yang sedang dipilih atau aktif
    obj = context.active_object
    scene = context.scene
    image_name = context.window_manager.image_enum
    # Mengambil semua slot material pada objek
    material_slots = obj.material_slots
    # Looping melalui semua slot material dan menambahkan node image texture pada setiap material
    custom_data_item = scene.MyData.add()
    for material_slot in material_slots:
        material = material_slot.material
        if material:
            nodeName = image_name + "_node_" + AddOnName + "_" + time_str
            frameNodeName = image_name + "_frameNode_" + AddOnName + "_" + time_str
            material_node_tree = material.node_tree
            
            texture_node = material_node_tree.nodes.new('ShaderNodeTexImage')
            texture_node.name = nodeName
            
            texture_node.location = (-400, 0)
            texture_node.image = bpy.data.images[image_name]

            # Seleksi dan buat node texture aktif
            texture_node.select = True
            material_node_tree.nodes.active = texture_node

            # Buat frame node tree dengan nama yang sama dengan nama gambar
            frame_node = material_node_tree.nodes.new('NodeFrame')
            frame_node.name = frameNodeName
            frame_node.label = image_name +" - "+ AddOnName
            frame_node.location = (-450, 50)
            frame_node.width = 400
            frame_node.height = 300
            frame_node.color = (0.105, 0, 1)
            frame_node.use_custom_color = True
            # Tambahkan node texture ke dalam frame
            material_node_tree.nodes.active = frame_node
            frame_node.select = True
            material_node_tree.nodes.active = texture_node
            
            texture_node.parent = frame_node
        
    scene = context.scene
    
    custom_data_item.nodeName = nodeName
    custom_data_item.frameNodeName = frameNodeName
    custom_data_item.textureName = context.window_manager.image_enum
    custom_data_item.indexTexture =len(scene.MyData)

classes = [ListData,Data,MY_UL_list,MY_OT_add_item,MY_OT_delete_item,MyCustomPanel,ReactiveNode,DeleteUnusedMaterial]
def register():
    from bpy.types import WindowManager
    WindowManager.image_enum = EnumProperty(
        items=enum_image_items,
        description="Select an image",
    )
    for reg in classes:
        bpy.utils.register_class(reg)
    # bpy.utils.register_class(Data)
    # bpy.utils.register_class(MY_UL_list)
    # bpy.utils.register_class(MY_OT_add_item)
    # bpy.utils.register_class(MY_OT_delete_item)
    # bpy.utils.register_class(MyCustomPanel)
    # bpy.utils.register_class(ReactiveNode)
    # bpy.utils.register_class(DeleteUnusedMaterial)
    bpy.types.Scene.MyListData = bpy.props.CollectionProperty(type=ListData)
    bpy.types.Scene.list_index = bpy.props.IntProperty(name="This is the list of data that you have added.", default=0)
    bpy.types.Scene.MyData = bpy.props.CollectionProperty(type=Data)
    
def unregister():
    from bpy.types import WindowManager
    
    del WindowManager.image_enum
    for unreg in classes:
        bpy.utils.unregister_class(unreg)
    # bpy.utils.unregister_class(Data)
    # bpy.utils.unregister_class(MY_UL_list)
    # bpy.utils.unregister_class(MY_OT_add_item)
    # bpy.utils.unregister_class(MY_OT_delete_item)
    # bpy.utils.unregister_class(MyCustomPanel)
    # bpy.utils.unregister_class(ReactiveNode)
    # bpy.utils.unregister_class(DeleteUnusedMaterial)
    del bpy.types.Scene.MyListData
    del bpy.types.Scene.list_index
    del bpy.types.Scene.MyData
if __name__ == "__main__":
    register()