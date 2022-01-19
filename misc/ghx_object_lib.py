# from lxml import etree as et

# from _typeshed import NoneType
import time
import hashlib
import uuid
from typing import Container
from misc.xml_lib import *


def generate_group_obj_xelem(object_index, nick_name, group_target, color_string="255;0;0;0"):
        dummy_instance_guid = uuid.uuid1()

        id_count = len(group_target)
        target_desc = ""
        for i, gt in enumerate(group_target):
            target_desc += """<item name="ID" index="{}" type_name="gh_guid" type_code="9">{}</item>""".format(i, gt)
        target_desc += """<item name="ID_Count" type_name="gh_int32" type_code="3">{}</item>""".format(id_count)

        xelem_desc = """
            <chunk name="Object" index="{}">
              <items count="2">
                <item name="GUID" type_name="gh_guid" type_code="9">c552a431-af5b-46a9-a8a4-0fcbc27ef596</item>
                <item name="Name" type_name="gh_string" type_code="10">Group</item>
              </items>
              <chunks count="1">
                <chunk name="Container">
                  <items count="8">
                    <item name="Border" type_name="gh_int32" type_code="3">3</item>
                    <item name="Colour" type_name="gh_drawing_color" type_code="36">
                      <ARGB>{}</ARGB>
                    </item>
                    <item name="Description" type_name="gh_string" type_code="10">A group of Grasshopper objects</item>
                    {}
                    <item name="InstanceGuid" type_name="gh_guid" type_code="9">{}</item>
                    <item name="Name" type_name="gh_string" type_code="10">Group</item>
                    <item name="NickName" type_name="gh_string" type_code="10">{}</item>
                  </items>
                  <chunks count="1">
                    <chunk name="Attributes" />
                  </chunks>
                </chunk>
              </chunks>
            </chunk>
        """.format(object_index, color_string, target_desc, dummy_instance_guid, nick_name)
        return xelem_desc

def fetch_object_xelements(changed_xelements):
    changed_object_xelements =[fetch_ancestor_by_attrib(t, "@name=\"Object\"") 
        for t in changed_xelements]
    changed_object_xelements = list(set(changed_object_xelements))
    changed_object_xelements = [t for t in changed_object_xelements if t is not None]
    return changed_object_xelements

def fetch_objects_chunks(ghx_root):
    root = ghx_root
    # ghxl.print_contents(root)
    # ghx_Definition = fetch_content(root.xpath("/Archive/chunks/*"), "@name", "Definition")[0]
    cur = root.xpath("/Archive/chunks")[0]
    ghx_Definition = fetch_children_by_attrib(cur, "@name=\"Definition\"")[0]
    # print_contents(ghx_Definition)
    cur = ghx_Definition.xpath("./chunks")[0]
    ghx_DefinitionObjects = fetch_children_by_attrib(cur, "@name=\"DefinitionObjects\"")[0]
    # print_contents(ghx_DefinitionObjects)
    cur = ghx_DefinitionObjects.xpath("./items")[0]
    ghx_ObjectCount = fetch_children_by_attrib(cur, "@name=\"ObjectCount\"")[0]
    cur = ghx_DefinitionObjects.xpath("./chunks")[0]
    ghx_DefinitionObjects_chunks = fetch_children_by_attrib(cur, "@name=\"Object\"")
    return ghx_ObjectCount, ghx_DefinitionObjects_chunks
    
def fetch_obj_class_info(obj_xelem):
    class_guid = fetch_children_by_attrib(obj_xelem.xpath("./items")[0], "@name=\"GUID\"")[0].text
    class_name = fetch_children_by_attrib(obj_xelem.xpath("./items")[0], "@name=\"Name\"")[0].text
    # print("class guid: ", class_guid, ", name: ", class_name)
    return class_guid, class_name

def fetch_instance_info_from_obj_xelement(obj_xelem):
    container = fetch_descendants_by_attrib(obj_xelem.xpath("./chunks")[0], "@name=\"Container\"")
    instance_guid = fetch_descendants_by_attrib(container[0], "@name=\"InstanceGuid\"")[0].text
    name = fetch_descendants_by_attrib(container[0], "@name=\"Name\"")[0].text
    nick_name = fetch_descendants_by_attrib(container[0], "@name=\"NickName\"")[0].text
    # print("instance_guid: ", instance_guid, ", name: ", name, ", nick_name: ", nick_name)
    return instance_guid, name, nick_name

class Ghx_Content:
    parent_table = dict()
    def __init__(self, src_xelems, instance_guid, name, nick_name):
        self.src_xelems = src_xelems
        self.instance_guid = instance_guid
        self.name = name
        self.nick_name = nick_name
        pass

class Object_Param(Ghx_Content):
    def __init__(self, src_xelems, instance_guid, name, nick_name, is_input, source, parent_object_guid, ):
        super().__init__(src_xelems, instance_guid, name, nick_name)
        self.is_input = is_input
        self.source = source
        self.parent_object_guid = parent_object_guid

        # print("param_guid: ", self.instance_guid, ", name: ", self.name, ", nick_name: ", self.nick_name)
        # print("source: ", len(self.source), ", ", self.source)
        # print("is_input: ", self.is_input)

        Ghx_Content.parent_table[self.instance_guid] = self.parent_object_guid
    @classmethod
    def object_param_from_ghx(cls, src_xelems, parent_object_guid, parent_pos):
        cur = src_xelems.xpath("./items")[0]
        guid = fetch_children_by_attrib(cur, "@name='InstanceGuid'")[0].text
        name = fetch_children_by_attrib(cur, "@name='Name'")[0].text
        nick_name = fetch_children_by_attrib(cur, "@name='NickName'")[0].text
        source = list()
        s_list =  fetch_children_by_attrib(cur, "@name='Source'")
        for s in s_list:
            source.append(s.text)

        cur = src_xelems.xpath("./chunks")[0]
        cur = fetch_children_by_attrib(cur, "@name='Attributes'")[0]
        cur = cur.xpath("./items")[0]
        ghx_Pivot = fetch_children_by_attrib(cur, "@name='Pivot'")[0]

        pos = [float(ghx_Pivot.xpath("./X")[0].text), float(ghx_Pivot.xpath("./Y")[0].text)]
        is_input = False
        if pos[0] < parent_pos[0]:
            is_input = True
        return cls(src_xelems, guid, name, nick_name, is_input, source, parent_object_guid)
    def get_display_name(self):
        ret = self.name
        if self.nick_name:
            ret = self.nick_name
        return ret

class Object(Ghx_Content):
    def __init__(self, obj_xelem, input_output_info):

        instance_guid, name, nick_name = fetch_instance_info_from_obj_xelement(obj_xelem)
        super().__init__(obj_xelem, instance_guid, name, nick_name)
        
        self.input_list = list()
        self.output_list = list()

        # print("inst guid: ", self.instance_guid, ", name: ", self.name, ", nickname: ", self.nick_name)

        for param in input_output_info:
            if param.is_input:
                self.input_list.append(param)
            else:
                self.output_list.append(param)
        print("input_list")
        for c in self.input_list:
            print("\t Name: ", c.name, c.instance_guid, c.source)

        print("output_list")
        for c in self.output_list:
            print("\t Name: ", c.name, c.instance_guid)#, c.source)
        Ghx_Content.parent_table[self.instance_guid] = self.instance_guid

    @classmethod
    def Generic_Object(cls, obj_xelem):
        instance_guid, name, nick_name = fetch_instance_info_from_obj_xelement(obj_xelem)
        print("instance_guid: ", instance_guid, ", name: ", name, ", nick_name: ", nick_name)
        cur = obj_xelem.xpath("./chunks")[0]
        container_xelem =  fetch_children_by_attrib(cur, "@name=\"Container\"")[0]
        cur = container_xelem.xpath("./chunks")[0]
        attrib_xelem = fetch_children_by_attrib(cur, "@name='Attributes'")[0]
        cur = attrib_xelem.xpath("./items")[0]
        pivot_xelem = fetch_children_by_attrib(cur, "@name='Pivot'")[0]
        pos = [float(pivot_xelem.xpath("./X")[0].text), float(pivot_xelem.xpath("./Y")[0].text)]

        input_output_info = list()
        cur = container_xelem.xpath("./chunks")[0]        
        input_output_xelems = fetch_descendants_by_attrib(cur, "@name='InstanceGuid'")
        for t in input_output_xelems:
            t = t.xpath("..")[0].xpath("..")[0]
            input_output_info.append(Object_Param.object_param_from_ghx(t, instance_guid, pos))

        return cls(obj_xelem, input_output_info)

    def escape_chars(s):
        s = s.replace("<", "\<")
        s = s.replace(">", "\>")
        s = s.replace("|", "\|")
        return s

    def derive_node_desc(self):
        # s.node('struct3', r'hello\nworld |{ b |{c|<here> d|e}| f}| g | h')`
        display_name = self.name
        if self.nick_name:
            display_name = self.nick_name

        desc = ""
        if self.input_list:
            desc += "{"
            for c in self.input_list:                
                desc += "<" + c.instance_guid + "> " + Object.escape_chars(c.get_display_name()) + " |"
            desc = desc[:-1]
            desc += "}|"
            
        desc += "{<" + self.instance_guid + "> " + Object.escape_chars(display_name) + " }"
        if self.output_list:
            desc += "|{"
            for c in self.output_list:
                print(Object.escape_chars(c.get_display_name()))
                desc += "<" + c.instance_guid + "> " + Object.escape_chars(c.get_display_name()) + " |"
            desc = desc[:-1]
            desc += "}"
            
        print(desc)
        return desc

    def derive_edge_desc(self):
        beg = list()
        end = list()
        for c in self.input_list:
            for s in c.source:
                parent = Ghx_Content.parent_table[s]
                beg.append(parent + ":" + s)
                end.append(c.parent_object_guid + ":" + c.instance_guid)
        return beg, end

    def generate_hash(self, ignore_cmp_pos):
        hash_src = ""
        ## creating new tree may be the easiest way to get all descendants.
        desc = et.ElementTree(self.src_xelems).xpath("//*")
        # print("len(desc): ", len(desc))
        ## remove the first item, because it includes an object index of .ghx.
        chunk_or_item = list()
        for c in desc[1:]:
            if c.tag in {"chunks", "chunk", "items", "item"}:
                chunk_or_item.append(c)

        for cur in chunk_or_item:
            ignore = False
            childs = et.ElementTree(cur).xpath("//*")
            if "type_name" in cur.attrib:
                if cur.attrib["type_name"] in {"gh_drawing_rectanglef", "gh_drawing_pointf"}:
                    ignore = True and ignore_cmp_pos
                    # if ignore:
                    #     print("skipping contents regarding components pos: ", cur.tag, ", ", cur.attrib)
            if not ignore:            
                for c in childs:
                    hash_src += print_contents(c, silent=True)

        # print(hashlib.sha1(hash_src.encode('utf-8')).hexdigest())
        return hashlib.sha1(hash_src.encode('utf-8')).hexdigest()

class Panel_Object(Object):
    def __init__(self, obj_xelem, input_output_info, user_text):
        super().__init__(obj_xelem, input_output_info)
        self.user_text = user_text

    @classmethod
    def Panel_Object(cls, obj_xelem):
        instance_guid, name, nick_name = fetch_instance_info_from_obj_xelement(obj_xelem)
        print("instance_guid: ", instance_guid, ", name: ", name, ", nick_name: ", nick_name)
        cur = obj_xelem.xpath("./chunks")[0]
        container_xelem =  fetch_children_by_attrib(cur, "@name=\"Container\"")[0]
        # fetch user text
        cur = container_xelem.xpath("./items")[0]
        user_text = ""
        source_count = fetch_children_by_attrib(cur, "@name=\"SourceCount\"")[0].text
        if source_count == "0":
            user_text = fetch_children_by_attrib(cur, "@name='UserText'")[0].text
        print("user_text: ", user_text)

        # fetch input
        cur = container_xelem.xpath("./items")[0]
        input_output_info = list()
        source = list()
        source_xelems = fetch_children_by_attrib(cur, "@name='Source'")
        for c in source_xelems:
            source.append(c.text)
        
        isInput = True
        input_output_info.append(Object_Param(source_xelems, instance_guid, "in", "in", isInput, source, instance_guid))
        
        return cls(obj_xelem, input_output_info, user_text)
    def derive_node_desc(self):
        # s.node('struct3', r'hello\nworld |{ b |{c|<here> d|e}| f}| g | h')`
        desc = ""
        display_name = self.name
        if self.nick_name:
            display_name += "|" + self.nick_name
        
        desc = ""
        desc += "{<" + self.instance_guid + "> " + Object.escape_chars(display_name) + " }"
        if self.user_text:
            desc += "|{ " + Object.escape_chars(self.user_text) + " }"       
        print(desc)

        return desc
