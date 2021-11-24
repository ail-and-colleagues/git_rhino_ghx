from os import remove
import sys
from logging import exception
from typing import Container


import git
from git import diff
from lxml import etree as et
import difflib


from misc.xml_lib import Line_to_Xml_Element, fetch_descendants_by_attrib, string_parser, fetch_children_by_attrib
# from misc.ghx_object_lib import fetch_object_xelements, generate_group_obj_xelem

from misc import ghx_object_lib as ghxl

class Branch:
    def __init__(self, repo, branch_name):
    #     try:
        self.branch = None
        try:
            local_branches = repo.branches
            for b in local_branches:
                if b.name == branch_name:
                    self.branch = b
            if not self.branch:
                remote_branches = repo.remotes.origin.fetch()
                for b in remote_branches:
                    if b.name == branch_name:
                        self.branch = b
            if not self.branch:
                msg = "\"{}\" can not find in the repo {}\n and the remote {}.".format(
                    branch_name,
                    [b.name for b in local_branches],
                    [b.name for b in remote_branches]) 
                raise Exception(msg)
        except Exception as e:
            print(e)
            sys.exit()

        self.blob_dict = self.fetch_blobs_data(self.branch.commit.tree)
    def fetch_blobs_data(self, cur):
        ret = dict()
        def rec(tree):
            for b in tree.blobs:
                ret["./" + b.path] = b
            for t in tree.trees:
                rec(t)
        rec(cur)
        return ret

    def fetch_blob(self, filename):
        try:
            ret = self.blob_dict[filename]
        except Exception as e:
            print(str(e) + "can not find")
            print( "in " + str(self.blob_dict.keys()))
            sys.exit()
        return ret

# def indicate_changed_objects_as_group(tgt_xml, removed_guids, modified_guids, added_guids):
#     ## updates obj(=component) count
#     ## obj count is noted at:
#     ## - <chunk name="DefinitionObjects">/<item name="ObjectCount"~>
#     ## - <chunk name="DefinitionObjects">/<chunks count="16">

#     object_count_xelem = fetch_descendants_by_attrib(tgt_xml, "@name=\"ObjectCount\"")[0]
#     obj_count = int(object_count_xelem.text)
#     p = 1 if len(removed_guids) else 0
#     p = p + 1 if len(modified_guids) else p
#     p = p + 1 if len(added_guids) else p

#     object_count_xelem.text = str(obj_count + p)
#     definition_objects_xelem = fetch_descendants_by_attrib(tgt_xml, "@name=\"DefinitionObjects\"")[0]
#     def_objs_chunks_xelem = definition_objects_xelem.xpath("chunks")[0]
#     def_objs_chunks_xelem.attrib["count"] = object_count_xelem.text

#     # insert group 
#     # removed
#     if len(removed_guids):
#         desc = ghxl.generate_group_obj_xelem(obj_count, "removed_cmps", removed_guids, "255;255;127;127")
#         def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
#         obj_count += 1
#     if len(modified_guids):
#         desc = ghxl.generate_group_obj_xelem(obj_count, "modified_cmps", modified_guids, "255;127;255;255")
#         def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
#         obj_count += 1
#     if len(added_guids):
#         desc = ghxl.generate_group_obj_xelem(obj_count, "added_cmps", added_guids, "255;127;255;127")
#         def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
#         obj_count += 1

#     return tgt_xml

def indicate_changed_objects_as_group(aft_xml, removed_comps, modified_guids, added_guids):
    ## updates obj(=component) count
    ## obj count is noted at:
    ## - <chunk name="DefinitionObjects">/<item name="ObjectCount"~>
    ## - <chunk name="DefinitionObjects">/<chunks count="16">

    object_count_xelem = fetch_descendants_by_attrib(aft_xml, "@name=\"ObjectCount\"")[0]
    obj_count = int(object_count_xelem.text)
    p = len(removed_comps)
    p = p + 1 if len(removed_comps) else p
    p = p + 1 if len(modified_guids) else p
    p = p + 1 if len(added_guids) else p

    object_count_xelem.text = str(obj_count + p)
    definition_objects_xelem = fetch_descendants_by_attrib(aft_xml, "@name=\"DefinitionObjects\"")[0]
    def_objs_chunks_xelem = definition_objects_xelem.xpath("chunks")[0]
    def_objs_chunks_xelem.attrib["count"] = object_count_xelem.text

    # insert group 
    # removed

    for removed_comp in removed_comps:
        removed_comp.src_xelems.attrib["index"] = str(obj_count)
        t = et.ElementTree(removed_comp.src_xelems).getroot()
        print(t)
        def_objs_chunks_xelem.insert(obj_count, t)
        obj_count += 1
    if len(removed_comps):
        removed_guids = [t.instance_guid for t in removed_comps]
        desc = ghxl.generate_group_obj_xelem(obj_count, "removed_cmps", removed_guids, "255;255;127;127")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1
          
    if len(modified_guids):
        desc = ghxl.generate_group_obj_xelem(obj_count, "modified_cmps", modified_guids, "255;127;255;255")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1
    if len(added_guids):
        desc = ghxl.generate_group_obj_xelem(obj_count, "added_cmps", added_guids, "255;127;255;127")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1

    return aft_xml


repo = git.Repo("./")

bef_branch = Branch(repo, "main")
aft_branch = Branch(repo, "test")
print(bef_branch.blob_dict.keys())

target_file_name = "./sample/xmlTest.ghx"
bef_blob = bef_branch.fetch_blob(target_file_name)
bef_decoded = bef_blob.data_stream.read().decode("utf-8")
aft_blob = aft_branch.fetch_blob(target_file_name)
aft_decoded = aft_blob.data_stream.read().decode("utf-8")


bef_xml = et.fromstring(bef_decoded)
aft_xml = et.fromstring(aft_decoded)


def Generate_guid_hash_pair(tgt_xml):
    _, obj_xelems = ghxl.fetch_objects_chunks(tgt_xml)
    component_list = list()
    for obj_xelem in obj_xelems:
        print("---")
        # ghxl.parse_object_chunks(obj_xelem)
        _, class_name = ghxl.fetch_obj_class_info(obj_xelem)
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
    ret = dict()
    for c in component_list:
        ret[c.instance_guid] = (c.generate_hash(), c) 
    return ret

bef_guid_hash = Generate_guid_hash_pair(bef_xml)
aft_guid_hach = Generate_guid_hash_pair(aft_xml)


removed_comps= [comp for guid, (hash, comp) in bef_guid_hash.items() if guid not in aft_guid_hach.keys()]
print("removed_guids: ", [t.instance_guid for t in removed_comps])

modified_comps = [comp for guid, (hash, comp) in bef_guid_hash.items()
    if (guid in aft_guid_hach.keys() and hash != aft_guid_hach[guid][0])]
print("modified_guids: ", [t.instance_guid for t in modified_comps])

unmodified_comps = [comp for guid, (hash, comp) in bef_guid_hash.items()
    if (guid in aft_guid_hach.keys() and hash == aft_guid_hach[guid][0])]
print("unmodified_guids: ", [t.instance_guid for t in unmodified_comps])

added_comps = [comp for guid, (hash, comp) in aft_guid_hach.items() if guid not in bef_guid_hash.keys()]
print("added_guids: ", [t.instance_guid for t in added_comps])

# bef_xml = indicate_changed_objects_as_group(bef_xml, removed_guids, modified_guids, [])
# out_filename = target_file_name[:target_file_name.rfind(".")]
# out_filename += "(bef)_{}.ghx".format(bef_branch.branch.name) 
# et.ElementTree(bef_xml).write(
#     out_filename,
#     pretty_print = True,
#     xml_declaration = True,
#     encoding = "utf-8" )
modified_guids = [t.instance_guid for t in modified_comps]
added_guids = [t.instance_guid for t in added_comps]
aft_xml = indicate_changed_objects_as_group(aft_xml, removed_comps, modified_guids, added_guids)
out_filename = target_file_name[:target_file_name.rfind(".")]
out_filename += "_ditt({}_to_{}).ghx".format(bef_branch.branch.name, aft_branch.branch.name) 
et.ElementTree(aft_xml).write(
    out_filename,
    pretty_print = True,
    xml_declaration = True,
    encoding = "utf-8" )


