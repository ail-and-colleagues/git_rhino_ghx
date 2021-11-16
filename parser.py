# from _typeshed import Self
from lxml import etree as et
from misc import ghx_object_lib as ghxl

if __name__ == '__main__':
    ghx_path = "./sample/xmlTest.ghx"
    tree = et.parse(ghx_path).getroot()
    ghx_ObjectCount, ghx_DefinitionObjects_chunks = ghxl.fetch_objects_chunks(tree)
   
    component_list = list()
    for ghx_Object in ghx_DefinitionObjects_chunks:

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

        ghx_items, ghx_Container, ghx_Attributes, ghx_others = ghx_list
        # 
        # print("--ghx_items")
        # obj_hash_src = ghx_items.xpath(".//*")
        # for t in obj_hash_src:
        #     ghxl.print_contents(t)

        # print("--ghx_Container", ghx_Container)
        # ret = list()        
        # for t in ret:
            # ghxl.print_contents(t)

        # for t in obj_hash_src:
        #     ghxl.print_contents(t)

        # print("--ghx_others")
        # ret = ghxl.fetch_content_recursive(ghx_others, "@name", "Attributes")
        # for t in ret:
        #     ghxl.print_contents(t)
        component_list.append(comp)
        # comp.generate_hash()

for comp in component_list:
    comp.generate_hash()

            

    



# import graphviz
# ##https://graphviz.readthedocs.io/en/stable/api.html


# s = graphviz.Digraph('structs',
#     filename='g',
#     engine="dot",
#     format='png',
#     graph_attr={'rankdir': 'LR'},
#     node_attr={'shape': 'Mrecord', 'rankdir': 'TB', "fontname":"Consolas"})

# # s.node('struct1', '<f0> left|<f1> middle|<f2> right')

# for c in component_list:
#     s.node(c.instance_guid, c.derive_node_desc())


# for c in component_list:    
#     beg, end = c.derive_edge_desc()
#     for b, e in zip(beg, end):
#         s.edges([(b, e)])
#         print(b, e)

# with s.subgraph(name='group') as c:
#     c.attr(style='filled', color='lightgrey')
#     c.node("90e88581-03d1-45dd-9f0a-3442e4e55919")
#     c.node("cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec")


# s.render()
