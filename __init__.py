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
    def newInput(self, idname, name):
        socket = self.inputs.new(idname, name)
        socket.link_limit = socket.inputLinkLimit
        return socket

    def newOutput(self, idName, name):
        socket = self.outputs.new(idName, name)
        socket.link_limit = socket.outputLinkLimit
        return socket

class ParticleNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ParticleNode"
    bl_label = "Particle"

    particleName = StringProperty(name = "Name", default = "Main")

    def init(self, context):
        self.newInput("pn_EmitterSocket", "Emitter")
        self.newInput("pn_ModifiersSocket", "Modifiers")
        self.newInput("pn_ConstraintsSocket", "Constraints")
        self.newOutput("pn_ParticleSocket", "Particle")
        self.color = (1, 0.7, 0.3)
        self.use_custom_color = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "particleName", text = "", icon = "MOD_PARTICLES")

class MeshEmitterNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_MeshEmitterNode"
    bl_label = "Mesh Emitter"

    emitterTypeItems = [
        ("VERTICES", "Vertices", "", "VERTEXSEL", 0),
        ("EDGES", "Edges", "", "EDGESEL", 1),
        ("FACES", "Faces", "", "FACESEL", 2),
        ("VOLUME", "Volume", "", "SNAP_VOLUME", 3)
    ]

    emitterType = EnumProperty(name = "Emitter Type", items = emitterTypeItems)

    def init(self, context):
        self.newInput("pn_ObjectSocket", "Source").showName = False
        self.newInput("pn_FloatSocket", "Rate")
        self.newOutput("pn_FlowControlSocket", "On Birth")
        self.newOutput("pn_EmitterSocket", "Emitter")

    def draw_buttons(self, context, layout):
        layout.prop(self, "emitterType", text = "")

class CurveEmitterNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_CurveEmitterNode"
    bl_label = "Curve Emitter"

    def init(self, context):
        self.newInput("pn_ObjectSocket", "Source").showName = False
        self.newInput("pn_FloatSocket", "Rate")
        self.newOutput("pn_FlowControlSocket", "On Birth")
        self.newOutput("pn_EmitterSocket", "Emitter")

class GravityForceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_GravityForceNode"
    bl_label = "Gravity Force"

    def init(self, context):
        self.newOutput("pn_ModifiersSocket", "Force")

class AttractForceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_AttractForceNode"
    bl_label = "Attract Force"

    def init(self, context):
        self.newOutput("pn_ModifiersSocket", "Force")

class StickToSurfaceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_StickToSurfaceNode"
    bl_label = "Stick to Surface"

    def init(self, context):
        self.newOutput("pn_ConstraintsSocket", "Constraint")

class AgeTriggerNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_AgeTriggerNode"
    bl_label = "Age Trigger"

    triggerTypeItems = [
        ("REACHED", "Aged Reached", ""),
        ("INTERVAL", "Interval", "")
    ]

    def createInputSocket(self, context = None):
        if len(self.inputs) == 2:
            self.inputs.remove(self.inputs[1])
        if self.triggerType == "REACHED":
            self.inputs.new("pn_FloatSocket", "Age")
        elif self.triggerType == "INTERVAL":
            self.inputs.new("pn_FloatSocket", "Interval")

    triggerType = EnumProperty(items = triggerTypeItems, update = createInputSocket)

    def init(self, context):
        self.newInput("pn_ParticleSocket", "Particle")
        self.newOutput("pn_FlowControlSocket", "Next")
        self.createInputSocket()

    def draw_buttons(self, context, layout):
        layout.prop(self, "triggerType", text = "")


class CollisionTriggerNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_CollisionTriggerNode"
    bl_label = "Collision Trigger"

    def init(self, context):
        self.newInput("pn_ParticleSocket", "Particle")
        self.newOutput("pn_FlowControlSocket", "Next")

class BounceOnCollisionNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_BounceOnCollisionNode"
    bl_label = "Bounce on Collision"

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newOutput("pn_FlowControlSocket", "Next")

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
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newOutput("pn_FlowControlSocket", "Next")
        self.buildDataInputSocket()

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text = "")

class KillParticleNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_KillParticleNode"
    bl_label = "Kill Particle"

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")

class RandomizeAttributeNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_RandomizeAttributeNode"
    bl_label = "Randomize Attribute"

    attribute = EnumProperty(items = attributeItems)

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newInput("pn_FloatSocket", "Strength")
        self.newOutput("pn_FlowControlSocket", "Next")

    def draw_buttons(self, context, layout):
        layout.prop(self, "attribute", text = "")

class GetAttributeNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_GetAttributeNode"
    bl_label = "Get Attribute"

    def buildOutputSocket(self, context = None):
        if len(self.outputs) == 1:
            self.outputs.remove(self.outputs[0])
        self.newOutput(attributeSocketTypes[self.attribute], "Value")

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
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newInput("pn_FloatSocket", "A")
        self.newInput("pn_FloatSocket", "B")
        self.newOutput("pn_FlowControlSocket", "If True")
        self.newOutput("pn_FlowControlSocket", "If False")

    def draw_buttons(self, context, layout):
        layout.prop(self, "comparisonType", text = "")

def getParticleNameItems(self, context):
    items = []
    for node in self.id_data.nodes:
        if isinstance(node, ParticleNode):
            items.append((node.particleName, node.particleName, ""))
    return items

class SpawnParticleNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_SpawnParticleNode"
    bl_label = "Spawn Particle"

    def updateSockets(self, context):
        if len(self.inputs) == 2:
            self.inputs.remove(self.inputs[1])

        if self.spawnType == "EMITTER":
            self.newInput("pn_EmitterSocket", "Emitter")

    spawnTypeItems = [
        ("DEFAULT_EMITTER", "Default Emitter", ""),
        ("EMITTER", "Emitter", ""),
        ("COPY", "Copy", "")
    ]

    particleName = EnumProperty(name = "Particle Type",
        items = getParticleNameItems)
    spawnType = EnumProperty(name = "Spawn Type", default = "DEFAULT_EMITTER",
        update = updateSockets, items = spawnTypeItems)

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newOutput("pn_FlowControlSocket", "Next")
        self.newOutput("pn_FlowControlSocket", "New Particle Next")

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "particleName", text = "", icon = "MOD_PARTICLES")
        col.prop(self, "spawnType", text = "")

class RenderPrimitiveNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_RenderPrimitiveNode"
    bl_label = "Render Primitive"

    primitiveTypeItems = [
        ("BILLBOARD", "Billboard", "", "MESH_PLANE", 0),
        ("SPHERE", "Sphere", "", "MATSPHERE", 1)
    ]

    primitiveType = EnumProperty(name = "Primitive Type",
        items = primitiveTypeItems)

    material = PointerProperty(name = "Material", type = bpy.types.Material)

    def init(self, context):
        self.newInput("pn_ParticleSocket", "Particle")
        self.newInput("pn_FloatSocket", "Size").value = 1

    def draw_buttons(self, context, layout):
        layout.prop(self, "primitiveType", text = "")
        layout.prop(self, "material", text = "")

class RenderInstanceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_RenderInstanceNode"
    bl_label = "Render Instance"

    def init(self, context):
        self.newInput("pn_ParticleSocket", "Particle")
        self.newInput("pn_ObjectSocket", "Object").showName = False
        self.newInput("pn_FloatSocket", "Size").value = 1

class RenderTrailNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_RenderTrailNode"
    bl_label = "Render Trail"

    def init(self, context):
        self.newInput("pn_ParticleSocket", "Particle")
        self.newInput("pn_FloatSocket", "Length").value = 10


# Sockets
######################################################

class BaseSocket:
    inputLinkLimit = 1
    outputLinkLimit = 0

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
    inputLinkLimit = 0

class ModifiersSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ModifiersSocket"
    drawColor = (0.9, 0.3, 0.3, 1)
    inputLinkLimit = 0

class ConstraintsSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ConstraintsSocket"
    drawColor = (0.3, 0.3, 0.3, 1)
    inputLinkLimit = 0

class ParticleSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_ParticleSocket"
    drawColor = (0.9, 0.9, 0.1, 1)

class FlowControlSocket(BaseSocket, bpy.types.NodeSocket):
    bl_idname = "pn_FlowControlSocket"
    drawColor = (0.3, 0.9, 0.5, 1)
    inputLinkLimit = 0
    outputLinkLimit = 1

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
    layout.operator_context = "INVOKE_DEFAULT"

    insertNode(layout, "pn_ParticleNode", "Particle")
    layout.separator()
    insertNode(layout, "pn_MeshEmitterNode", "Mesh Emitter")
    insertNode(layout, "pn_CurveEmitterNode", "Curve Emitter")
    layout.separator()
    insertNode(layout, "pn_GravityForceNode", "Gravity")
    insertNode(layout, "pn_AttractForceNode", "Attract")
    layout.separator()
    insertNode(layout, "pn_StickToSurfaceNode", "Stick to Surface")
    layout.separator()
    insertNode(layout, "pn_CollisionTriggerNode", "Collision Trigger")
    insertNode(layout, "pn_AgeTriggerNode", "Age Trigger")
    layout.separator()
    insertNode(layout, "pn_BounceOnCollisionNode", "Bounce on Collision")
    insertNode(layout, "pn_SetAttributeNode", "Set Attribute")
    insertNode(layout, "pn_GetAttributeNode", "Get Attribute")
    insertNode(layout, "pn_KillParticleNode", "Kill Particle")
    insertNode(layout, "pn_ConditionNode", "Condition")
    insertNode(layout, "pn_SpawnParticleNode", "Spawn Particle")
    insertNode(layout, "pn_RandomizeAttributeNode", "Randomize")
    layout.separator()
    insertNode(layout, "pn_RenderPrimitiveNode", "Render Primitive")
    insertNode(layout, "pn_RenderInstanceNode", "Render Instance")
    insertNode(layout, "pn_RenderTrailNode", "Render Trail")


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
