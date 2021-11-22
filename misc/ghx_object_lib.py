# from lxml import etree as et

# from _typeshed import NoneType
import time
import hashlib
import uuid
from typing import Container
from misc.xml_lib import *


def generate_group_obj_xelem(object_index, nick_name, group_target, color_string="255;0;0;0"):
        dummy_instance_guid = uuid.uuid1()#hashlib.shake_128(str(time.time()).encode()).hexdigest()
        # a95ea66b-4927-11ec-864c-f02f7421c407
        # d169e6c5-a060-4cf0-895b-5843e2761cf6
        print("dummy_instance_guid: ", dummy_instance_guid)

        # <item name="ID" index="0" type_name="gh_guid" type_code="9">d169e6c5-a060-4cf0-895b-5843e2761cf6</item>
        # <item name="ID" index="1" type_name="gh_guid" type_code="9">21b8775e-9d96-4913-9a35-4f729905192c</item>
        # <item name="ID_Count" type_name="gh_int32" type_code="3">2</item>
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
    changed_object_xelements =[fetch_parent_by_attrib(t, "@name=\"Object\"") 
        for t in changed_xelements]
    changed_object_xelements = list(set(changed_object_xelements))
    changed_object_xelements = [t for t in changed_object_xelements if t is not None]
    return changed_object_xelements

def fetch_objects_chunks(ghx_root):

    root = ghx_root
    # ghxl.print_contents(root)
    ghx_Definition = fetch_content(root.xpath("/Archive/chunks/*"), "@name", "Definition")[0]
    print_contents(ghx_Definition)
    ghx_DefinitionObjects = fetch_content(ghx_Definition.xpath("./chunks/*"), "@name", "DefinitionObjects")[0]
    # ghxl.print_contents(ghx_DefinitionObjects)
    ghx_ObjectCount = fetch_content(ghx_DefinitionObjects.xpath("./items/*"), "@name", "ObjectCount")[0]
    ghx_DefinitionObjects_chunks = fetch_content(ghx_DefinitionObjects.xpath("./chunks/*"), "@name", "Object")
    return ghx_ObjectCount, ghx_DefinitionObjects_chunks
    
def parse_object_chunks(ghx_object_chunk):
    ghx_Object_items = ghx_object_chunk.xpath("./items")[0]
    # print_contents(ghx_Object_items)

    ghx_Object_Container = fetch_content(ghx_object_chunk.xpath("./chunks/*"), "@name", "Container")[0]
    # ghx_Object_Container_items = ghx_Object_Container.xpath("./items")[0]

    ghx_Object_Attributes = fetch_content(ghx_Object_Container.xpath("./chunks/*"), "@name", "Attributes")[0]

    ghx_Object_others  = fetch_content(ghx_Object_Container.xpath("./chunks/*"), "@name!", "Attributes")
    # print("ghx_Object_Attributes: ", ghx_Object_Attributes)
    # print("ghx_Object_others: ", ghx_Object_others)

    class_info, instance_info, pos, ghx_list = Object.fetch_common_info(ghx_Object_items, ghx_Object_Container, ghx_Object_Attributes, ghx_Object_others)
    return class_info, instance_info, pos, ghx_list

class Ghx_Content:

    def __init__(self, instance_guid, name, nick_name):
        self.instance_guid = instance_guid
        self.name = name
        self.nick_name = nick_name
        pass


class Object_Param(Ghx_Content):
    parent_table = dict()
    def __init__(self, instance_guid, name, nick_name, is_input, source, parent_object_guid):
        super().__init__(instance_guid, name, nick_name)
        self.is_input = is_input
        self.source = source
        self.parent_object_guid = parent_object_guid

        print("instance_guid: ", self.instance_guid, ", name: ", self.name, ", nick_name: ", self.nick_name)
        print("source: ", len(self.source), ", ", self.source)
        print("is_input: ", self.is_input)

        Object_Param.parent_table[self.instance_guid] = self.parent_object_guid
    @classmethod
    def object_param_from_ghx(cls, ghx_Param, parent_object_guid, parent_pos):
        cur = ghx_Param.xpath("./items")[0]
        guid = fetch_content(cur, "@name", "InstanceGuid")[0].text
        name = fetch_content(cur, "@name", "Name")[0].text
        nick_name = fetch_content(cur, "@name", "NickName")[0].text
        source = list()
        s_list =  fetch_content(cur, "@name", "Source")
        for s in s_list:
            source.append(s.text)

        cur = ghx_Param.xpath("./chunks/*")
        cur = fetch_content(cur, "@name", "Attributes")[0]
        cur = fetch_content(cur.xpath("./items/*"), "@name", "Pivot")[0]

        pos = [float(cur.xpath("./X")[0].text), float(cur.xpath("./Y")[0].text)]
        is_input = False
        if pos[0] < parent_pos[0]:
            is_input = True
        return cls(guid, name, nick_name, is_input, source, parent_object_guid)
    def get_display_name(self):
        ret = self.name
        if self.nick_name:
            ret = self.nick_name
        return ret

class Object(Ghx_Content):
    def __init__(self, class_info, instance_info, input_output_info, ghx_list):
        
        print("Object __init__")
        
        self.class_guid, self.class_name = class_info
        instance_guid, name, nick_name = instance_info
        super().__init__(instance_guid, name, nick_name)
        self.ghx_items, self.ghx_Container, self.ghx_Attributes, self.ghx_others = ghx_list

        self.input_list = list()
        self.output_list = list()

        print("class guid: ", self.class_guid, ", name: ", self.class_name)
        print("inst guid: ", self.instance_guid, ", name: ", self.name, ", nickname: ", self.nick_name)

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

    @classmethod
    def fetch_common_info(cls, ghx_items, ghx_Container, ghx_Attributes, ghx_others):
        ## retrieve class info/.
        class_guid = fetch_content(ghx_items, "@name", "GUID")[0].text
        class_name = fetch_content(ghx_items, "@name", "Name")[0].text
        print("class guid: ", class_guid, ", name: ", class_name)

        ## retrieve instance info.
        cur = ghx_Container.xpath("./items")[0]
        instance_guid = fetch_content(cur, "@name", "InstanceGuid")[0].text
        instance_name = fetch_content(cur, "@name", "Name")[0].text
        instance_nick_name = fetch_content(cur, "@name", "NickName")[0].text
        print("inst guid: ", instance_guid, ", name: ", instance_name, ", nickname: ", instance_nick_name)

        ## retrive instaice pos.
        cur = ghx_Attributes.xpath("./items/*")
        ghx_Pivot = fetch_content(cur, "@name", "Pivot")
        if ghx_Pivot:
            pos = [float(ghx_Pivot[0].xpath("./X")[0].text), float(ghx_Pivot[0].xpath("./Y")[0].text)]
            print("inst pos: ", pos)
            class_info = (class_guid, class_name)
            instance_info = (instance_guid, instance_name, instance_nick_name)
        else:
            # Group doesn't have pos
            pos = None
        return class_info, instance_info, pos, (ghx_items, ghx_Container, ghx_Attributes, ghx_others)

    @classmethod
    def Generic_Object(cls, class_info, instance_info, pos, ghx_list):
        class_guid, class_name = class_info
        instance_guid, instance_name, instance_nick_name = instance_info
        ghx_items, ghx_Container, ghx_Attributes, ghx_others = ghx_list

        # fetch input
        def recursive_search(cur):
            # print_contents(cur)
            t_guid = fetch_content(cur.xpath("./items/*"), "@name", "InstanceGuid")
            # print("instance_guid: ", instance_guid)
            if t_guid:
                # input_output_list.append(Object_Param(cur, self))
                input_output_info.append(Object_Param.object_param_from_ghx(cur, instance_guid, pos))
            chunks = cur.xpath("./chunks/chunk")
            for chunk in chunks:
                recursive_search(chunk)
        
        input_output_info = list()
        for cur in ghx_others:
            recursive_search(cur)
        return cls(class_info, instance_info, input_output_info, ghx_list)

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
            # <TR PORT="l2">l3</TD>
            for s in c.source:
                # if s in Object_Param.parent_table.keys():
                parent = Object_Param.parent_table[s]
                beg.append(parent + ":" + s)
                end.append(c.parent_object_guid + ":" + c.instance_guid)
        return beg, end




    def generate_hash_src(self, cur, print_src=False):
        src = ""
        ret = fetch_content_recursive(cur.xpath("./*"), "@name", "Attributes")
        for t in ret:
            src += print_contents(t, silent=print_src) + "\n"
        return src

    def generate_hash(self):
    
        src = self.generate_hash_src(self.ghx_items)
        class_hash =  hashlib.sha1(src.encode('utf-8')).hexdigest()

        src = self.generate_hash_src(self.ghx_Container)
        container_hash =  hashlib.sha1(src.encode('utf-8')).hexdigest()

        src = ""
        for cur in self.ghx_others:
            src += self.generate_hash_src(cur)
        io_param_hash = hashlib.sha1(src.encode('utf-8')).hexdigest()


        print(hashlib.sha1(src.encode('utf-8')).hexdigest())



class Panel_Object(Object):
    def __init__(self, class_info, instance_info, input_output_info, ghx_list, user_text):
        super().__init__(class_info, instance_info, input_output_info, ghx_list)
        self.user_text = user_text

    @classmethod
    def Panel_Object(cls, class_info, instance_info, pos, ghx_list):
        class_guid, class_name = class_info
        instance_guid, instance_name, instance_nick_name = instance_info
        ghx_items, ghx_Container, ghx_Attributes, ghx_others = ghx_list

        # fetch user text
        cur = ghx_Container.xpath("./items")[0]
        user_text = ""
        if fetch_content(cur, "@name", "SourceCount")[0].text == "0":
            user_text = fetch_content(cur, "@name", "UserText")[0].text
        # user_text = t
        print("user_text: ", user_text)

        # fetch input
        cur = ghx_Container.xpath("./items")[0]
        input_output_info = list()
        Source = list()
        for c in fetch_content(cur, "@name", "Source"):
            print("c.text: ", c.text)
            Source.append(c.text)
        
        isInput = True
        input_output_info.append(Object_Param(instance_guid, "in", "in", isInput, Source, instance_guid))
        
        return cls(class_info, instance_info, input_output_info, ghx_list, user_text)
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
