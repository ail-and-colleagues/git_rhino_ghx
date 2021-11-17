from lxml import etree as et
from misc import ghx_object_lib as ghxl

import graphviz
##https://graphviz.readthedocs.io/en/stable/api.html

def parse_components(ghx_DefinitionObjects_chunks):
    component_list = list()

    for ghx_Object in ghx_DefinitionObjects_chunks:
        comp = None
        print("\n")
        ghxl.print_contents(ghx_Object)
        
        class_info, instance_info, pos, ghx_list = ghxl.parse_object_chunks(ghx_Object)
        class_guid, class_name = class_info
        if class_name == "Panel":
            comp = ghxl.Panel_Object.Panel_Object(class_info, instance_info, pos, ghx_list)
        elif class_name == "Group":
            pass
        else:
            comp = ghxl.Object.Generic_Object(class_info, instance_info, pos, ghx_list)
        
        if comp:
            component_list.append(comp)
    return component_list

def output_ghx_as_dotpng(component_list, out_filename):
    s = graphviz.Digraph('structs',
        filename=out_filename,
        # engine="dot",
        format='png',
        graph_attr={'rankdir': 'LR'},
        node_attr={'shape': 'Mrecord', 'rankdir': 'TB', "fontname":"Consolas"})

# s.node('struct1', '<f0> left|<f1> middle|<f2> right')

    for c in component_list:
        s.node(c.instance_guid, c.derive_node_desc())

    for c in component_list:    
        beg, end = c.derive_edge_desc()
        for b, e in zip(beg, end):
            s.edges([(b, e)])
            print(b, e)
    s.render()

    pass

if __name__ == '__main__':
    ghx_path = "./sample/xmlTest.ghx"
    tree = et.parse(ghx_path).getroot()
    ghx_ObjectCount, ghx_DefinitionObjects_chunks = ghxl.fetch_objects_chunks(tree)
   
    component_list = parse_components(ghx_DefinitionObjects_chunks)
    out_filename = ghx_path[:ghx_path.rfind(".")] + ".dot"
    print(out_filename)
    output_ghx_as_dotpng(component_list, out_filename)

