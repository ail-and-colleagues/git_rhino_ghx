from lxml import etree as et
from misc import ghx_object_lib as ghxl

import graphviz
##https://graphviz.readthedocs.io/en/stable/api.html

def parse_components(tgt_xml):
    _, obj_xelems = ghxl.fetch_objects_chunks(tgt_xml)
    component_list = list()
    for obj_xelem in obj_xelems:
        print("---")
        _, class_name = ghxl.fetch_obj_class_info(obj_xelem)
        ## grasshopper components do not have unified description format on .ghx(xml).
        ## so we have to implement a derived class to address a component that
        ## fails to parse or indicate its contents(e.g. slider) with the base class (Generic_Object).
        if class_name == "Panel":
            comp = ghxl.Panel_Object.Panel_Object(obj_xelem)
            component_list.append(comp)
            comp.generate_hash()
        elif class_name == "Group":
            pass
        else:
            comp = ghxl.Object.Generic_Object(obj_xelem)
            component_list.append(comp)
            comp.generate_hash()
    return component_list

def output_ghx_as_dotpng(component_list, out_filename):
    s = graphviz.Digraph('structs',
        filename=out_filename,
        # engine="dot",
        format='png',
        graph_attr={'rankdir': 'LR'},
        node_attr={'shape': 'Mrecord', 'rankdir': 'TB', "fontname":"Consolas"})

    for c in component_list:
        s.node(c.instance_guid, c.derive_node_desc())

    for c in component_list:    
        beg, end = c.derive_edge_desc()
        for b, e in zip(beg, end):
            s.edges([(b, e)])
            print(b, e)
    s.render()



if __name__ == '__main__':
    target_file_name = "./sample/xmlTest.ghx"
    tgt_ghx = et.parse(target_file_name).getroot()
   
    component_list = parse_components(tgt_ghx)
    out_filename = target_file_name[:target_file_name.rfind(".")] + ".dot"
    print(out_filename)
    output_ghx_as_dotpng(component_list, out_filename)

