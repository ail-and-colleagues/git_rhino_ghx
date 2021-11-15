# from lxml import etree as et

def print_contents(temp_root):
    print("tag:", temp_root.tag, ", attrib: ", temp_root.attrib)
    if temp_root.text[0] != "\n":
        print("text:, ", temp_root.text)
    for c in temp_root:
        print("\t", c.tag, c.attrib)
    print("\t.")


def extruct_content(cur, att_key, att_val):
    ret = list()
    others = list()
    for c in cur:
        appended = False
        if att_key in c.attrib.keys():
            v = c.attrib[att_key]
            if v == att_val:
                appended = True
                ret.append(c)
        if not appended:
            others.append(c)
            
    return ret, others

def fetch_content(cur, att_key, att_val):
    ret, _ = extruct_content(cur, att_key, att_val)
    return ret


def fetch_objects_chunks(ghx_root):

    root = ghx_root
    # ghxl.print_contents(root)
    ghx_Definition = fetch_content(root.xpath("/Archive/chunks/*"), "name", "Definition")[0]
    # ghxl.print_contents(ghx_Definition)
    ghx_DefinitionObjects = fetch_content(ghx_Definition.xpath("./chunks/*"), "name", "DefinitionObjects")[0]
    # ghxl.print_contents(ghx_DefinitionObjects)
    ghx_ObjectCount = fetch_content(ghx_DefinitionObjects.xpath("./items/*"), "name", "ObjectCount")[0]
    # ghxl.print_contents(ghx_ObjectCount)
    # component_count = int(ghx_ObjectCount.text)
    ghx_DefinitionObjects_chunks = fetch_content(ghx_DefinitionObjects.xpath("./chunks/*"), "name", "Object")
    return ghx_ObjectCount, ghx_DefinitionObjects_chunks
    
def parse_object_chunks(ghx_object_chunk):
    ghx_Object_items = ghx_object_chunk.xpath("./items")[0]
    # print_contents(ghx_Object_items)

    ghx_Object_Container = fetch_content(ghx_object_chunk.xpath("./chunks/*"), "name", "Container")[0]
    # ghx_Object_Container_items = ghx_Object_Container.xpath("./items")[0]

    ghx_Object_Attributes, ghx_Object_others = extruct_content(ghx_Object_Container.xpath("./chunks/*"), "name", "Attributes")
    ghx_Object_Attributes = ghx_Object_Attributes[0]
    # print("ghx_Object_Attributes: ", ghx_Object_Attributes)
    # print("ghx_Object_others: ", ghx_Object_others)

    class_info, instance_info, pos, ghx_list = Object.fetch_common_info(ghx_Object_items, ghx_Object_Container, ghx_Object_Attributes, ghx_Object_others)
    return class_info, instance_info, pos, ghx_list

class Ghx_Content:

    def __init__(self):
        pass


class Object_Param(Ghx_Content):
    parent_table = dict()
    def __init__(self, InstanceGuid, Name, NickName, isInput, Source, parent_object_guid):
        self.InstanceGuid = InstanceGuid
        self.Name = Name
        self.NickName = NickName
        self.isInput = isInput
        self.Source = Source
        self.parent_object_guid = parent_object_guid
        print("InstanceGuid: ", self.InstanceGuid, ", Name: ", self.Name, ", NickName: ", self.NickName)
        print("Source: ", len(self.Source), ", ", self.Source)
        print("isInput: ", self.isInput)

        Object_Param.parent_table[self.InstanceGuid] = self.parent_object_guid


    @classmethod
    def Object_Param_from_ghx(cls, ghx_Param, parent_object_guid, parent_pos):
        
        cur = ghx_Param.xpath("./items")[0]
        InstanceGuid = fetch_content(cur, "name", "InstanceGuid")[0].text
        Name = fetch_content(cur, "name", "Name")[0].text
        NickName = fetch_content(cur, "name", "NickName")[0].text
        Source = list()
        s_list =  fetch_content(cur, "name", "Source")
        for s in s_list:
            Source.append(s.text)

        cur = ghx_Param.xpath("./chunks/*")
        cur = fetch_content(cur, "name", "Attributes")[0]
        cur = fetch_content(cur.xpath("./items/*"), "name", "Pivot")[0]

        pos = [float(cur.xpath("./X")[0].text), float(cur.xpath("./Y")[0].text)]
        isInput = False
        if pos[0] < parent_pos[0]:
            isInput = True
        return cls(InstanceGuid, Name, NickName, isInput, Source, parent_object_guid)

class Object(Ghx_Content):
    def __init__(self, class_info, instance_info, input_output_info, ghx_list):
        print("Object __init__")
        
        self.class_guid, self.class_name = class_info
        self.instance_guid, self.instance_name, self.instance_nick_name = instance_info
        self.ghx_items, self.ghx_Container, self.ghx_Attributes, self.ghx_others = ghx_list

        self.input_list = list()
        self.output_list = list()

        print("class guid: ", self.class_guid, ", name: ", self.class_name)
        print("inst guid: ", self.instance_guid, ", name: ", self.instance_name, ", nickname: ", self.instance_nick_name)


        for param in input_output_info:
            if param.isInput:
                self.input_list.append(param)
            else:
                self.output_list.append(param)
        print("input_list")
        for c in self.input_list:
            print("\t Name: ", c.Name, c.InstanceGuid, c.Source)

        print("output_list")
        for c in self.output_list:
            print("\t Name: ", c.Name, c.InstanceGuid, c.Source)

        # Ghx_Content.parent_table[self.instance_guid] = self

    @classmethod
    def fetch_common_info(cls, ghx_items, ghx_Container, ghx_Attributes, ghx_others):
        ## retrieve class info/.
        class_guid = fetch_content(ghx_items, "name", "GUID")[0].text
        class_name = fetch_content(ghx_items, "name", "Name")[0].text
        print("class guid: ", class_guid, ", name: ", class_name)

        ## retrieve instance info.
        cur = ghx_Container.xpath("./items")[0]
        instance_guid = fetch_content(cur, "name", "InstanceGuid")[0].text
        instance_name = fetch_content(cur, "name", "Name")[0].text
        instance_nick_name = fetch_content(cur, "name", "NickName")[0].text
        print("inst guid: ", instance_guid, ", name: ", instance_name, ", nickname: ", instance_nick_name)

        ## retrive instaice pos.
        cur = ghx_Attributes.xpath("./items/*")
        ghx_Pivot = fetch_content(cur, "name", "Pivot")
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
            t_guid = fetch_content(cur.xpath("./items/*"), "name", "InstanceGuid")
            # print("instance_guid: ", instance_guid)
            if t_guid:
                # input_output_list.append(Object_Param(cur, self))
                input_output_info.append(Object_Param.Object_Param_from_ghx(cur, instance_guid, pos))
            chunks = cur.xpath("./chunks/chunk")
            for chunk in chunks:
                recursive_search(chunk)
        
        input_output_info = list()
        for cur in ghx_others:
            recursive_search(cur)
        return cls(class_info, instance_info, input_output_info, ghx_list)

    
    # def fetch_input_output(self):

    def derive_node_desc(self):
        # s.node('struct3', r'hello\nworld |{ b |{c|<here> d|e}| f}| g | h')`
        if not self.instance_nick_name:
            self.instance_nick_name = self.instance_name

        desc = ""
        if self.input_list:
            desc += "{"
            for c in self.input_list:
                # <TR PORT="l2">l3</TD>
                desc += "<" + c.InstanceGuid + "> " + c.Name + " |"
            desc = desc[:-1]
            desc += "}|"
            
        desc += "{<" + self.instance_guid + "> " + self.instance_nick_name + " }"
        if self.output_list:
            desc += "|{"
            for c in self.output_list:
                # <TR PORT="l2">l3</TD>
                desc += "<" + c.InstanceGuid + "> " + c.Name + " |"
            desc = desc[:-1]
            desc += "}"         
        print(desc)
        return desc

    def derive_edge_desc(self):
        beg = list()
        end = list()
        for c in self.input_list:
            # <TR PORT="l2">l3</TD>
            for s in c.Source:
                # if s in Object_Param.parent_table.keys():
                parent = Object_Param.parent_table[s]
                beg.append(parent + ":" + s)
                end.append(c.parent_object_guid + ":" + c.InstanceGuid)
        return beg, end
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
        if fetch_content(cur, "name", "SourceCount")[0].text == "0":
            user_text = fetch_content(cur, "name", "UserText")[0].text
        # user_text = t
        print("user_text: ", user_text)

        # fetch input
        cur = ghx_Container.xpath("./items")[0]
        input_output_info = list()
        Source = list()
        for c in fetch_content(cur, "name", "Source"):
            print("c.text: ", c.text)
            Source.append(c.text)
        
        isInput = True
        input_output_info.append(Object_Param(instance_guid, "in", "in", isInput, Source, instance_guid))
        
        return cls(class_info, instance_info, input_output_info, ghx_list, user_text)
    def derive_node_desc(self):
        # s.node('struct3', r'hello\nworld |{ b |{c|<here> d|e}| f}| g | h')`
        if not self.instance_nick_name:
            self.instance_nick_name = self.instance_name

        desc = ""
        desc += "{<" + self.instance_guid + "> " + self.instance_nick_name + " }"
        if self.user_text:
            desc += "|{ " + self.user_text + " }"       
        print(desc)
        return desc
