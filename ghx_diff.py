
import sys
import argparse
from logging import exception

import git
from lxml import etree as et
from misc.xml_lib import Line_to_Xml_Element, fetch_descendants_by_attrib
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

    # insert groups 
    ## removed
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
          
    ## modified
    if len(modified_guids):
        desc = ghxl.generate_group_obj_xelem(obj_count, "modified_cmps", modified_guids, "255;127;255;255")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1
    ## added
    if len(added_guids):
        desc = ghxl.generate_group_obj_xelem(obj_count, "added_cmps", added_guids, "255;127;255;127")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1

    return aft_xml


def generate_guid_hash_pair(tgt_xml, ignore_cmp_pos):
    _, obj_xelems = ghxl.fetch_objects_chunks(tgt_xml)
    component_list = list()
    for obj_xelem in obj_xelems:
        print("---")
        # ghxl.parse_object_chunks(obj_xelem)
        _, class_name = ghxl.fetch_obj_class_info(obj_xelem)
        if class_name == "Panel":
            comp = ghxl.Panel_Object.Panel_Object(obj_xelem)
            component_list.append(comp)
        elif class_name == "Group":
            pass
        else:
            comp = ghxl.Object.Generic_Object(obj_xelem)
            component_list.append(comp)
    ret = dict()
    for c in component_list:
        ret[c.instance_guid] = (c.generate_hash(ignore_cmp_pos=ignore_cmp_pos), c) 
    return ret


def escape_branch_name(branch_name):
    branch_name = branch_name.replace("/", "-")
    return branch_name

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog="ghx_diff.py",
        description="create diff.ghx by specifying .ghx file and branches.",
        epilog="-",
        add_help=True
        )
    parser.add_argument("-p", "--path_to_repo", help="path to a repository", action="store", type=str, default="./")
    parser.add_argument("-t", "--target", help="target .ghx file", action="store", type=str, required=True)
    parser.add_argument("-l", "--left_branch", help="left branch", action="store", type=str, required=True)
    parser.add_argument("-r", "--right_branch", help="right branch", action="store", type=str, required=True)
    parser.add_argument("-i", "--ignore_positon", help="ignore component position changes", action="store_true", default=True)

    args = parser.parse_args()
    print("args.path_to_repo: ", args.path_to_repo)
    print("args.target: ", args.target)
    print("args.left_branch: ", args.left_branch)
    print("args.right_branch: ", args.right_branch)
    print("args.ignore_positon: ", args.ignore_positon)

    ## specify repo, branch, and blob.
    repo = git.Repo(args.path_to_repo.replace("\\", "/"))
    target_file_name = args.target.replace("\\", "/")
    bef_branch = Branch(repo, args.left_branch)
    aft_branch = Branch(repo, args.right_branch)
    
    bef_blob = bef_branch.fetch_blob(target_file_name)
    bef_decoded = bef_blob.data_stream.read().decode("utf-8")
    aft_blob = aft_branch.fetch_blob(target_file_name)
    aft_decoded = aft_blob.data_stream.read().decode("utf-8")

    ## load .ghx as xml.
    bef_xml = et.fromstring(bef_decoded)
    aft_xml = et.fromstring(aft_decoded)

    ## create pairs of component guid and its hash.
    print("args.left_branch: ", args.left_branch, ", args.target: ", args.target)
    bef_guid_hash = generate_guid_hash_pair(bef_xml, ignore_cmp_pos=args.ignore_positon)
    print("args.right_branch: ", args.right_branch, ", args.target: ", args.target)
    aft_guid_hach = generate_guid_hash_pair(aft_xml, ignore_cmp_pos=args.ignore_positon)

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

    ## to reperesent diff in outputted .ghx:
    ## - insert and group removed components with nick name "removed_cmps".
    ## - group modified components as "modified_cmps" 
    ## - group added components as "added_cmps"
    modified_guids = [t.instance_guid for t in modified_comps]
    added_guids = [t.instance_guid for t in added_comps]
    aft_xml = indicate_changed_objects_as_group(aft_xml, removed_comps, modified_guids, added_guids)
    out_filename = target_file_name[:target_file_name.rfind(".")]
    # name output file as {original file name}_diff({from-branch-name}_to_{to-branch-name})
    bef_branch_name = escape_branch_name(bef_branch.branch.name)
    aft_branch_name = escape_branch_name(aft_branch.branch.name)
    out_filename += "_diff({}_to_{}).ghx".format(bef_branch_name, aft_branch_name)
    et.ElementTree(aft_xml).write(
        out_filename,
        pretty_print = True,
        xml_declaration = True,
        encoding = "utf-8" )
