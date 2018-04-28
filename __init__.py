bl_info = {
    "name":        "Particle Nodes Prototype",
    "description": "",
    "author":      "Jacques Lucke",
    "version":     (2, 1, 1),
    "blender":     (2, 79, 0),
    "location":    "Node Editor",
    "category":    "Node",
    "warning":     "This version is still in development."
}

import bpy
from bpy.props import *

class ParticlesNodeTree(bpy.types.NodeTree):
    bl_idname = "pn_ParticleNodeTree"
    bl_icon = "PARTICLES"
    bl_label = "Particle Nodes"


# Nodes
###################################################

class BaseNode:
    pass

class ParticleNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ParticleNode"
    bl_label = "Particle"

    particleName = StringProperty(name = "Name", default = "Main")

    def init(self, context):
        self.inputs.new("pn_EmitterSocket", "Emitter").link_limit = 0
        self.inputs.new("pn_ForcesSocket", "Forces").link_limit = 0
        self.inputs.new("pn_ConstraintsSocket", "Constraints").link_limit = 0
        self.outputs.new("pn_ParticleSocket", "Particle")
        self.outputs.new("pn_RenderSocket", "Render")

    def draw_buttons(self, context, layout):
        layout.prop(self, "particleName")

class SurfaceEmitterNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_SurfaceEmitterNode"
    bl_label = "Surface Emitter"

    def init(self, context):
        self.inputs.new("pn_ObjectSocket", "Object").showName = False
        self.outputs.new("pn_EmitterSocket", "Emitter")

class GravityForceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_GravityForceNode"
    bl_label = "Gravity Force"

    def init(self, context):
        self.outputs.new("pn_ForcesSocket", "Force")

class AttractForceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_AttractForceNode"
    bl_label = "Attract Force"

    def init(self, context):
        self.outputs.new("pn_ForcesSocket", "Force")

class StickToSurfaceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_StickToSurfaceNode"
    bl_label = "Stick to Surface"

    def init(self, context):
        self.outputs.new("pn_ConstraintsSocket", "Constraint")

class CollisionTriggerNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_CollisionTriggerNode"
    bl_label = "Collision Trigger"

    def init(self, context):
        self.inputs.new("pn_ParticleSocket", "Particle")
        self.outputs.new("pn_FlowControlSocket", "Next").link_limit = 1

class BounceOnCollisionNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_BounceOnCollisionNode"
    bl_label = "Bounce on Collision"

    def init(self, context):
        self.inputs.new("pn_FlowControlSocket", "Previous").link_limit = 0
        self.outputs.new("pn_FlowControlSocket", "Next").link_limit = 1

attributeSocketTypes =  {
    "COLOR" : "pn_ColorSocket",
    "VELOCITY" : "pn_VectorSocket",
    "SIZE" : "pn_FloatSocket",
    "AGE" : "pn_FloatSocket"
}

attributeItems = [
    ("COLOR", "Color", ""),
    ("VELOCITY", "Velocity", ""),
    ("SIZE", "Size", ""),
    ("AGE", "Age", "")
]

class SetAttributeNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_SetAttributeNode"
    bl_label = "Set Attribute Node"

    def buildDataInputSocket(self, context = None):
        if len(self.inputs) == 2:
            self.inputs.remove(self.inputs[1])
        socketType = attributeSocketTypes[self.attribute]
        self.inputs.new(socketType, "Value").showName = False


    attribute = EnumProperty(items = attributeItems, update = buildDataInputSocket)

    def init(self, context):
        self.inputs.new("pn_FlowControlSocket", "Previous").link_limit = 0
        self.outputs.new("pn_FlowControlSocket", "Next").link_limit = 1
        self.buildDataInputSocket()

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text = "")

class KillParticleNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_KillParticleNode"
    bl_label = "Kill Particle"

    def init(self, context):
        self.inputs.new("pn_FlowControlSocket", "Previous").link_limit = 0

class GetAttributeNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_GetAttributeNode"
    bl_label = "Get Attribute"

    def buildOutputSocket(self, context = None):
        if len(self.outputs) == 1:
            self.outputs.remove(self.outputs[0])
        self.outputs.new(attributeSocketTypes[self.attribute], "Value")

    attribute = EnumProperty(items = attributeItems, update = buildOutputSocket)

    def init(self, context):
        self.buildOutputSocket()

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text = "")

class ConditionNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ConditionNode"
    bl_label = "Condition"

    comparisonTypeItems = [
        ("SMALLER", "A < B", ""),
        ("GREATER", "A > B", "")
    ]

    comparisonType = EnumProperty(items = comparisonTypeItems)

    def init(self, context):
        self.inputs.new("pn_FlowControlSocket", "Previous").link_limit = 0
        self.inputs.new("pn_FloatSocket", "A")
        self.inputs.new("pn_FloatSocket", "B")
        self.outputs.new("pn_FlowControlSocket", "If True").link_limit = 1
        self.outputs.new("pn_FlowControlSocket", "If False").link_limit = 1

    def draw_buttons(self, context, layout):
        layout.prop(self, "comparisonType", text = "")

class SpawnParticleNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_SpawnParticleNode"
    bl_label = "Spawn Particle"

    def getParticleNameItems(self, context):
        items = []
        for node in self.id_data.nodes:
            if isinstance(node, ParticleNode):
                items.append((node.particleName, node.particleName, ""))
        return items

    spawnTypeItems = [
        ("EMITTER", "Emitter", ""),
        ("COPY", "Copy", ""),
        ("MANUAL", "Manual", "")
    ]

    particleName = EnumProperty(items = getParticleNameItems)
    spawnType = EnumProperty(items = spawnTypeItems)

    def init(self, context):
        self.inputs.new("pn_FlowControlSocket", "Previous").link_limit = 0
        self.outputs.new("pn_FlowControlSocket", "Next").link_limit = 1

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "particleName", text = "")
        col.prop(self, "spawnType")



# Sockets
######################################################

class BaseSocket:
    def draw_color(self, context, node):
        return self.drawColor

    def draw(self, context, layout, node, text):
        if not (self.is_linked or self.is_output) and hasattr(self, "drawProperty"):
            self.drawProperty(layout, text if self.showName else "", node)
        else:
            layout.label(text)

class ValueSocket(BaseSocket):
    showName = BoolProperty(default = True)
    drawColor = (0, 0, 0, 1)

class EmitterSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_EmitterSocket"
    drawColor = (1, 1, 1, 1)

class ForcesSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ForcesSocket"
    drawColor = (0.9, 0.3, 0.3, 1)

class ConstraintsSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ConstraintsSocket"
    drawColor = (0.3, 0.3, 0.3, 1)

class ParticleSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ParticleSocket"
    drawColor = (0.9, 0.9, 0.1, 1)

class RenderSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_RenderSocket"
    drawColor = (0.4, 0.4, 0.9, 1)

class FlowControlSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_FlowControlSocket"
    drawColor = (0.5, 0.5, 0.3, 1)

class ObjectSocket(ValueSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ObjectSocket"

    value = PointerProperty(type = bpy.types.Object)

    def drawProperty(self, layout, text, node):
        layout.prop(self, "value", text = text)

class ColorSocket(ValueSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ColorSocket"

    value = FloatVectorProperty(
        default = [0.5, 0.5, 0.5], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0)

    def drawProperty(self, layout, text, node):
        layout.prop(self, "value", text = text)

class FloatSocket(ValueSocket, bpy.types.NodeSocket):
    bl_idname = "pn_FloatSocket"

    value = FloatProperty()

    def drawProperty(self, layout, text, node):
        layout.prop(self, "value", text = text)

class VectorSocket(ValueSocket, bpy.types.NodeSocket):
    bl_idname = "pn_VectorSocket"

    value = FloatVectorProperty(subtype = "XYZ")

    def drawProperty(self, layout, text, node):
        layout.column().prop(self, "value", text = text)




def drawMenu(self, context):
    if context.space_data.tree_type != "pn_ParticleNodeTree":
        return

    layout = self.layout
    insertNode(layout, "pn_ParticleNode", "Particle")
    insertNode(layout, "pn_SurfaceEmitterNode", "Surface Emitter")
    insertNode(layout, "pn_GravityForceNode", "Gravity")
    insertNode(layout, "pn_AttractForceNode", "Attract")
    insertNode(layout, "pn_StickToSurfaceNode", "Stick to Surface")
    insertNode(layout, "pn_CollisionTriggerNode", "Collision Trigger")
    insertNode(layout, "pn_BounceOnCollisionNode", "Bounce on Collision")
    insertNode(layout, "pn_SetAttributeNode", "Set Attribute")
    insertNode(layout, "pn_GetAttributeNode", "Get Attribute")
    insertNode(layout, "pn_KillParticleNode", "Kill Particle")
    insertNode(layout, "pn_ConditionNode", "Condition")
    insertNode(layout, "pn_SpawnParticleNode", "Spawn Particle")


def insertNode(layout, type, text, settings = {}, icon = "NONE"):
    operator = layout.operator("node.add_node", text = text, icon = icon)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator



def register():
    bpy.utils.register_class(ParticlesNodeTree)
    for nodeCls in BaseNode.__subclasses__():
        bpy.utils.register_class(nodeCls)
    for socketCls in BaseSocket.__subclasses__() + ValueSocket.__subclasses__():
        if socketCls is ValueSocket:
            continue
        bpy.utils.register_class(socketCls)
    bpy.types.NODE_MT_add.append(drawMenu)

def unregister():
    pass
