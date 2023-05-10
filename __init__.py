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

        row = layout.row()
        
        box = layout.box()
        box.label(text="Image Texture For Bake")
        row = box.row()
        row.prop_search(wm, "image_enum", bpy.data, "images", icon="IMAGE_DATA", text="")



        row = box.row()
        row.operator("my_custom.add_item", icon="ADD", text="Add")
        row.operator("my_custom.delete_item", icon="REMOVE", text="Delete")
        # row.operator("my_custom.delete_item", icon="FILE_REFRESH", text="Recheck")
        listbox = box.template_list("MY_UL_list", "", context.scene, "custom_list", context.scene, "custom_list_index")
        if listbox:
            listbox.add()
            listbox.delete()
        row = box.row()
        row.operator("my_custom.reactive_nodes", icon="NODETREE", text="Reactive Nodes")
        row = box.row()
        row.operator("my_custom.delete_unused_material", icon="MATERIAL", text="Delete Unused Material")
class MY_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, icon="IMAGE_DATA")
        layout.label(text=context.a, icon="OUTLINER_OB_MESH")
def enum_image_items(self, context):    
    """EnumProperty callback"""
    items = []
    for i, img in enumerate(bpy.data.images):
        items.append((img.name, img.name, "", i))
    return items

class MY_OT_add_item(bpy.types.Operator):
    bl_idname = "my_custom.add_item"
    bl_label = "Add Item"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        # Mengecek apakah nilai sudah ada di custom_list
        for item in context.scene.custom_list:
            if item.name == context.window_manager.image_enum:
                self.report({'WARNING'}, "The image texture is already in the list")
                return {'CANCELLED'}

        # Menambahkan item baru pada custom_list
        item = context.scene.custom_list.add()
        item.name = context.window_manager.image_enum
        context.scene.custom_string = ""
        index = context.scene.custom_list_index
        AddNode(self, context, index)
        self.report({'INFO'},  "The "+ item.name +" was successfully added")
        return {'FINISHED'}

class MY_OT_delete_item(bpy.types.Operator):
    bl_idname = "my_custom.delete_item"
    bl_label = "Delete Item"

    @classmethod
    def poll(cls, context):
        return context.scene.custom_list_index >= 0

    def execute(self, context):
        index = context.scene.custom_list_index
        if len(context.scene.custom_list) <= 0 :
            self.report({'WARNING'},  "The texture image is not available")
            return{'FINISHED'}
        try:
            name = context.scene.custom_list[index].name 
            DeleteNode(self, context, index)
            context.scene.custom_list.remove(index)
            self.report({'INFO'},  "The "+ name +" has been successfully deleted")
            return {'FINISHED'}
        except IndexError:
            self.report({'WARNING'},  "No image texture selected")
            return {'FINISHED'}
class ReactiveNode(bpy.types.Operator):
   
    bl_idname = "my_custom.reactive_nodes"
    bl_label = "Reactive Nodes"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        index = context.scene.custom_list_index
        try:
            obj = bpy.context.active_object
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
            self.report({'INFO'},  "The nodes have been successfully reactivated")
            return{'FINISHED'}
        except IndexError:
            self.report({'WARNING'},  "No image texture selected")
            return {'FINISHED'}
class DeleteUnusedMaterial(bpy.types.Operator):
   
    bl_idname = "my_custom.delete_unused_material"
    bl_label = "Delete Unused Material"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        obj = bpy.context.active_object
        matcount = len(obj.material_slots)
        bpy.ops.object.material_slot_remove_unused()
        if matcount == len(obj.material_slots):
            self.report({'INFO'},  "All materials have been used")
        matcount -= len(obj.material_slots)
        self.report({'INFO'},  "Removing "+ str(matcount) +" unused materials has been successful")
        return{'FINISHED'}
#class Recheck(bpy.types.Operator):
    
def DeleteNode(self, context, index):
    obj = bpy.context.active_object
    scene = context.scene
    selectedTexture = context.scene.custom_list[index]
    i = 0;
    for item in scene.MyData:
        if selectedTexture.name == item.textureName:
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
            scene.MyData.remove(i)
        i+=1
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

classes = [Data,MY_UL_list,MY_OT_add_item,MY_OT_delete_item,MyCustomPanel,ReactiveNode,DeleteUnusedMaterial]
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
    bpy.types.Scene.custom_string = bpy.props.StringProperty(name="Custom String")
    bpy.types.Scene.custom_list_index = bpy.props.IntProperty(name="Custom List Index", default=0)
    bpy.types.Scene.custom_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="Custom List")
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
    del bpy.types.Scene.custom_string
    del bpy.types.Scene.custom_list_index
    del bpy.types.Scene.custom_list
    del bpy.types.Scene.MyData
if __name__ == "__main__":
    register()