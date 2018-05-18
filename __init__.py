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

def getParticleTypeItems(self, context):
    items = []
    for node in self.id_data.nodes:
        if isinstance(node, ParticleNode):
            items.append((node.particleName, node.particleName, ""))
    if len(items) == 0:
        items.append(("NONE", "None", ""))
    return items

def getGateNameItems(self, context):
    items = []
    for node in self.id_data.nodes:
        if isinstance(node, GateNode):
            items.append((node.gateName, node.gateName, ""))
    if len(items) == 0:
        items.append(("NONE", "None", ""))
    return items

class ParticleNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ParticleNode"
    bl_label = "Particle"

    particleName = StringProperty(name = "Name", default = "Main")

    def init(self, context):
        self.newInput("pn_EmitterSocket", "Emitter")
        self.newInput("pn_ModifierSocket", "Modifiers")
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
    densityGroup = StringProperty(name = "Density",
        description = "Control density on surface using a vertex group.")

    def init(self, context):
        self.newInput("pn_ObjectSocket", "Source").showName = False
        self.newInput("pn_FloatSocket", "Rate")
        self.newOutput("pn_FlowControlSocket", "On Birth")
        self.newOutput("pn_EmitterSocket", "Emitter")

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "emitterType", text = "")
        if self.emitterType in ("VERTICES", "EDGES", "FACES"):
            col.prop(self, "densityGroup", icon = "GROUP_VERTEX", text = "")

class CurveEmitterNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_CurveEmitterNode"
    bl_label = "Curve Emitter"

    def init(self, context):
        self.newInput("pn_ObjectSocket", "Source").showName = False
        self.newInput("pn_FloatSocket", "Rate")
        self.newOutput("pn_FlowControlSocket", "On Birth")
        self.newOutput("pn_EmitterSocket", "Emitter")

class GateNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_GateNode"
    bl_label = "Gate"

    gateName = StringProperty(name = "Gate Name", default = "Gate 1")
    isEnabled = BoolProperty(name = "Pass Through", default = False,
        description = "True if modifiers are passed through by default.")

    def init(self, context):
        self.newInput("pn_ModifierSocket", "Modifiers")
        self.newOutput("pn_ModifierSocket", "Modifiers")

    def draw_buttons(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "gateName", text = "", icon = "GAME")
        col.prop(self, "isEnabled",
            text = "Enabled" if self.isEnabled else "Disabled",
            icon = "LOCKVIEW_OFF" if self.isEnabled else "LOCKVIEW_ON")

class ToggleGateNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ToggleGateNode"
    bl_label = "Toggle Gate"

    enableGate = BoolProperty(name = "Open Gate", default = True)
    gateName = EnumProperty(name = "Gate Name", items = getGateNameItems)

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newOutput("pn_FlowControlSocket", "Next")

    def draw_buttons(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "enableGate",
            text = "Enable" if self.enableGate else "Disable",
            icon = "LOCKVIEW_OFF" if self.enableGate else "LOCKVIEW_ON")
        col.prop(self, "gateName", text = "", icon = "GAME")


class GravityForceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_GravityForceNode"
    bl_label = "Gravity Force"

    def updateInputs(self, context = None):
        self.inputs.clear()
        if not self.useSceneGravity:
            self.newInput("pn_VectorSocket", "Gravity").value = (0, 0, -1)

    useSceneGravity = BoolProperty(name = "Use Scene Gravity", default = True,
        update = updateInputs)

    def init(self, context):
        self.updateInputs()
        self.newOutput("pn_ModifierSocket", "Force")

    def draw_buttons(self, context, layout):
        layout.prop(self, "useSceneGravity")

class FollowForceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_FollowForceNode"
    bl_label = "Follow Force"

    leaderType = EnumProperty(name = "Leader", items = getParticleTypeItems)

    def init(self, context):
        self.newOutput("pn_ModifierSocket", "Force")

    def draw_buttons(self, context, layout):
        layout.prop(self, "leaderType", icon = "MOD_PARTICLES")

class AttractForceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_AttractForceNode"
    bl_label = "Attract Force"

    def init(self, context):
        self.newInput("pn_VectorSocket", "Position")
        self.newInput("pn_FloatSocket", "Strength")
        self.newOutput("pn_ModifierSocket", "Force")

class StickToSurfaceNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_StickToSurfaceNode"
    bl_label = "Stick to Surface"

    def init(self, context):
        self.newInput("pn_ObjectSocket", "Object").showName = False
        self.newOutput("pn_ModifierSocket", "Constraint")

class FreezeNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_FreezeNode"
    bl_label = "Freeze"

    freezePosition = BoolProperty(name = "Position", default = True)
    freezeRotation = BoolProperty(name = "Rotation", default = True)

    def init(self, context):
        self.newOutput("pn_ModifierSocket", "Constraint")

    def draw_buttons(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "freezePosition", icon = "MAN_TRANS")
        col.prop(self, "freezeRotation", icon = "MAN_ROT")

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
    "AGE" : "pn_FloatSocket",
    "POSITION" : "pn_VectorSocket"
}

attributeItems = [
    ("COLOR", "Color", ""),
    ("VELOCITY", "Velocity", ""),
    ("SIZE", "Size", ""),
    ("AGE", "Age", ""),
    ("POSITION", "Position", "")
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

class ChangeColorNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ChangeColorNode"
    bl_label = "Change Color"

    def updateSockets(self, context = None):
        if len(self.inputs) == 3:
            self.inputs.remove(self.inputs[2])
            self.outputs.remove(self.outputs[1])
        if self.fade:
            self.newInput("pn_FloatSocket", "Duration")
            self.newOutput("pn_FlowControlSocket", "After Fade")

    fade = BoolProperty(name = "Fade", default = False,
        update = updateSockets)

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newInput("pn_ColorSocket", "Color")
        self.newOutput("pn_FlowControlSocket", "Next")
        self.updateSockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "fade")

class WaitNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_WaitNode"
    bl_label = "Wait"

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newInput("pn_FloatSocket", "Duration")
        self.newOutput("pn_FlowControlSocket", "Next")
        self.newOutput("pn_FlowControlSocket", "After Wait")

class RandomColorNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_RandomColorNode"
    bl_label = "Random Color"

    def init(self, context):
        self.newInput("pn_ColorSocket", "Base")
        self.newInput("pn_FloatSocket", "Jitter")
        self.newOutput("pn_ColorSocket", "Color")

class ChangeDirectionNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ChangeDirectionNode"
    bl_label = "Change Direction"

    changeTypeItems = [
        ("SET", "Set", ""),
        ("RANDOMIZE", "Randomize", "")
    ]

    def updateSockets(self, context = None):
        while len(self.inputs) > 1: self.inputs.remove(self.inputs[-1])
        while len(self.outputs) > 1: self.outputs.remove(self.outputs[-1])

        if self.changeType == "SET":
            self.newInput("pn_VectorSocket", "Direction")
        elif self.changeType == "RANDOMIZE":
            self.newInput("pn_FloatSocket", "Strength")

        if self.fade:
            self.newInput("pn_FloatSocket", "Duration")
            self.newOutput("pn_FlowControlSocket", "After Fade")

    changeType =  EnumProperty(name = "Change Type", default = "RANDOMIZE", 
        update = updateSockets, items = changeTypeItems)

    fade = BoolProperty(name = "Fade", default = False,
        update = updateSockets)

    def init(self, context):
        self.newInput("pn_FlowControlSocket", "Previous")
        self.newOutput("pn_FlowControlSocket", "Next")
        self.updateSockets()

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "changeType", text = "")
        col.prop(self, "fade")

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
        items = getParticleTypeItems)
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

class VertexGroupWeightNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_VertexGroupWeightNode"
    bl_label = "Vertex Group Weight"

    groupName = StringProperty("Group")

    def init(self, context):
        self.newOutput("pn_FloatSocket", "Weight")

    def draw_buttons(self, context, layout):
        layout.prop(self, "groupName", text = "", icon = "GROUP_VERTEX")

class ImageColorNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_ImageColorNode"
    bl_label = "Image Color"

    uvMapName = StringProperty("UV Map")
    image = PointerProperty(name = "Image", type = bpy.types.Image)

    def init(self, context):
        self.newOutput("pn_ColorSocket", "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "uvMapName", text = "", icon = "GROUP_UVS")
        layout.prop(self, "image", text = "")

class VertexColorNode(BaseNode, bpy.types.Node):
    bl_idname = "pn_VertexColorNode"
    bl_label = "Vertex Color"

    vertexColorName = StringProperty(name = "Vertex Color")

    def init(self, context):
        self.newOutput("pn_ColorSocket", "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "vertexColorName", text = "", icon = "GROUP_VCOL")


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
    bl_idname = "pn_ModifierSocket"
    drawColor = (0.9, 0.3, 0.3, 1)
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
    insertNode(layout, "pn_FollowForceNode", "Follow")
    insertNode(layout, "pn_StickToSurfaceNode", "Stick to Surface")
    insertNode(layout, "pn_FreezeNode", "Freeze")
    layout.separator()
    insertNode(layout, "pn_CollisionTriggerNode", "Collision Trigger")
    insertNode(layout, "pn_AgeTriggerNode", "Age Trigger")
    layout.separator()
    insertNode(layout, "pn_GateNode", "Gate")
    insertNode(layout, "pn_ToggleGateNode", "Toogle Gate")
    layout.separator()
    insertNode(layout, "pn_RandomColorNode", "Random Color")
    insertNode(layout, "pn_ChangeColorNode", "Change Color")
    insertNode(layout, "pn_SetAttributeNode", "Set Attribute")
    insertNode(layout, "pn_GetAttributeNode", "Get Attribute")
    insertNode(layout, "pn_BounceOnCollisionNode", "Bounce on Collision")
    insertNode(layout, "pn_KillParticleNode", "Kill Particle")
    insertNode(layout, "pn_ConditionNode", "Condition")
    insertNode(layout, "pn_SpawnParticleNode", "Spawn Particle")
    insertNode(layout, "pn_RandomizeAttributeNode", "Randomize")
    insertNode(layout, "pn_WaitNode", "Wait")
    insertNode(layout, "pn_ChangeDirectionNode", "Change Direction")
    layout.separator()
    insertNode(layout, "pn_VertexGroupWeightNode", "Vertex Group Weight")
    insertNode(layout, "pn_ImageColorNode", "Image Color")
    insertNode(layout, "pn_VertexColorNode", "Vertex Color")
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
