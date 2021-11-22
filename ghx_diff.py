from os import remove
import sys
from logging import exception
from typing import Container


import git
from git import diff
from lxml import etree as et
import difflib


from misc.xml_lib import Line_to_Xml_Element, string_parser, fetch_children_by_attrib
from misc.ghx_object_lib import fetch_object_xelements, generate_group_obj_xelem

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

class Diff_Chunk:
    def __init__(self, diff_chunk):
        diff_chunk = diff_chunk.split("\n")
        # parse header
        # remove spaces and the last "@@" from the header.
        self.header = diff_chunk[0].replace(" ", "")[:-2]
        try:
            if "-" in self.header and "+" in self.header:
                ret = string_parser("-{},{}+{},{}", self.header)
                ret = [int(t) for t in ret]
                remove_beg, remove_range , add_beg, add_range = ret
                # print("Diff_Chnk head remove: ", remove_beg, "(", remove_range, "), add: ", add_beg, "(" , add_range, ")")
                # unified_diff line count start from 1. Apply -1 to match list subscript.
                self.remove_beg = remove_beg - 1
                self.add_beg = add_beg - 1
            else:
                msg = self.header + "is not @@-add_beg,add_range+remove_beg,remove_range@@ format."
                raise Exception(msg)
        except Exception as e:
            print(e)
            sys.exit()
        
        # parse content
        # difflib.unified_diff inserts a blank line under headers as separator.
        # remove the blank line by [2:] to count an actual line number.
        self.content = diff_chunk[2:]
        self.removed_line_idxs, self.added_line_idxs = self.parse_content()
        # print("removed line_idxs: ", self.removed_line_idxs)
        # print("added line_idxs: ", self.added_line_idxs)

    def parse_content(self):
        removed = list()
        added = list()
        line_count = self.remove_beg
        for c in self.content:
            if c[0] == "+":
                continue
            if c[0] == "-":
                removed.append(line_count)
            line_count += 1
         
        line_count = self.add_beg
        for c in self.content:
            if c[0] == "-":
                continue
            if c[0] == "+":
                added.append(line_count)
            line_count += 1
        return removed, added



class Diff_Mgr:
    def __init__(self, unified_diff, bef_xml, bef_line_xelem_map, aft_xml, aft_line_xelem_map,):
        diff = "\n".join([str(d) for d in unified_diff])
        # print(diff)
        diff = diff.split("\n@@")
        self.diff_chunk_list = list()
        # diff[0] is a header-like description of unified_diff.
        for i, d in enumerate(diff[1:]):
            self.diff_chunk_list.append(Diff_Chunk(d))
        self.bef_xml = bef_xml
        self.bef_line_xelem_map = bef_line_xelem_map
        self.aft_xml = aft_xml
        self.aft_line_xelem_map = aft_line_xelem_map
    def fetch_changed_xelements(self):
        def lines_to_xelements(xml, line_idxs, line_xelement_map):
            # remove duplicates.
            line_idxs = sum(line_idxs, [])
            # print("line_idxs: ", line_idxs)
            xelements_idx = set([line_xelement_map[i] for i in line_idxs])
            xelements = [xml.xpath("//*")[i] for i in xelements_idx]
            return xelements
        def fetch_instance_guid_from_obj_xelement(obj_xelem):
            container = fetch_children_by_attrib(obj_xelem.xpath("./chunks")[0], "@name=\"Container\"")
            instance_guid = fetch_children_by_attrib(container[0], "@name=\"InstanceGuid\"")[0].text
            # print("instance_guid: ", instance_guid)
            return instance_guid
        ## removed line(s) may not exist in the inputted xml and line_xelement_map?
        removed_line_idxs = [t.removed_line_idxs for t in self.diff_chunk_list]
        removed_xelements = lines_to_xelements(self.bef_xml, removed_line_idxs, self.bef_line_xelem_map)
        removed_object_xelems = fetch_object_xelements(removed_xelements)
        removed_instance_guids = [fetch_instance_guid_from_obj_xelement(t) for t in removed_object_xelems]
        added_line_idx = [t.added_line_idxs for t in self.diff_chunk_list]
        added_xelements = lines_to_xelements(self.aft_xml, added_line_idx, self.aft_line_xelem_map)
        added_object_xelems = fetch_object_xelements(added_xelements)
        added_instance_guids = [fetch_instance_guid_from_obj_xelement(t) for t in added_object_xelems]
        
        print("removed_instance_guids: ", len(removed_instance_guids))
        for t in removed_instance_guids:
            print("instance_guid: ", t)
        print("added_instance_guids: ", len(added_instance_guids))
        for t in added_instance_guids:
            print("instance_guid: ", t)


        ## note: set() reordered contents like dictionary.
        modified_instance_guids = set(removed_instance_guids).intersection(added_instance_guids)
        print("modified_instance_guids xelements: ", len(modified_instance_guids))
        for i, t in enumerate(modified_instance_guids):
            print(i, " instance_guid: ", t)

        removed_instance_guids = set(removed_instance_guids).difference(modified_instance_guids)
        added_instance_guids = set(added_instance_guids).difference(modified_instance_guids)

        print("removed xelements: ", len(removed_instance_guids))
        for i, t in enumerate(removed_instance_guids):
            print(i, " instance_guid: ", t)
        print("added xelements: ", len(added_instance_guids))
        for i, t in enumerate(added_instance_guids):
            print(i, " instance_guid: ", t)
        
        removed_instance_guids = list(removed_instance_guids)
        modified_instance_guids = list(modified_instance_guids)
        added_instance_guids = list(added_instance_guids)
        return removed_instance_guids, modified_instance_guids, added_instance_guids


repo = git.Repo("./")

bef_branch = Branch(repo, "test")
aft_branch = Branch(repo, "main")
print(bef_branch.blob_dict.keys())

target_file_name = "./sample/xmlTest.ghx"
bef_blob = bef_branch.fetch_blob(target_file_name)
bef_decoded = bef_blob.data_stream.read().decode("utf-8")
aft_blob = aft_branch.fetch_blob(target_file_name)
aft_decoded = aft_blob.data_stream.read().decode("utf-8")

# print(left_decoded)
parser = et.XMLParser(target=Line_to_Xml_Element())
parser.feed(bef_decoded)
bef_line_xelem_map = parser.close()

parser = et.XMLParser(target=Line_to_Xml_Element())
parser.feed(aft_decoded)
aft_line_xelem_map = parser.close()

print("bef_line_xelem_map[:15]")
print(bef_line_xelem_map[:15])

print("aft_line_xelem_map[:15]")
print(aft_line_xelem_map[:15])


# Should I get diff between under "chunk name="DefinitionObjects""?? 
# The unified_diff misunderstands xml hierarchy in the case gh-header-like contents are changed.
unified_diff = difflib.unified_diff(bef_decoded.split("\n"), aft_decoded.split("\n"),
    fromfile=bef_branch.branch.name + ": " + bef_blob.name,
    tofile=aft_branch.branch.name + ": " + aft_blob.name)

# for i, d in enumerate(unified_diff):
#     print(d)

bef_xml = et.fromstring(bef_decoded)
aft_xml = et.fromstring(aft_decoded)

# retrieve removed/ modified/ added instance guids from diff.
diff_mgr = Diff_Mgr(unified_diff, bef_xml, bef_line_xelem_map, aft_xml, aft_line_xelem_map)
removed_guids, modified_guids, added_guids = diff_mgr.fetch_changed_xelements()

# indicating changed objects as group.

##
def indicate_changed_objects_as_group(tgt_xml, removed_guids, modified_guids, added_guids):
    ## updates obj(=component) count
    ## obj count is noted at:
    ## - <chunk name="DefinitionObjects">/<item name="ObjectCount"~>
    ## - <chunk name="DefinitionObjects">/<chunks count="16">

    object_count_xelem = fetch_children_by_attrib(tgt_xml, "@name=\"ObjectCount\"")[0]
    print("tag: ", object_count_xelem.tag, ", attrib:", object_count_xelem.attrib)
    obj_count = int(object_count_xelem.text)
    p = 1 if len(removed_guids) else 0
    p = p + 1 if len(modified_guids) else p
    p = p + 1 if len(added_guids) else p
    print("p: ", p)

    object_count_xelem.text = str(obj_count + p)
    definition_objects_xelem = fetch_children_by_attrib(tgt_xml, "@name=\"DefinitionObjects\"")[0]
    print("definition_objects_xelem")
    print("tag: ", definition_objects_xelem.tag, ", attrib:", definition_objects_xelem.attrib)
    def_objs_chunks_xelem = definition_objects_xelem.xpath("chunks")[0]
    print("def_objs_chunks_xelem")
    print("tag: ", def_objs_chunks_xelem.tag, ", attrib:", def_objs_chunks_xelem.attrib)
    def_objs_chunks_xelem.attrib["count"] = object_count_xelem.text

    # insert group 
    # removed
    if len(removed_guids):
        desc = generate_group_obj_xelem(obj_count, "removed_cmps", removed_guids, "255;255;127;127")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1
    if len(modified_guids):
        desc = generate_group_obj_xelem(obj_count, "modified_cmps", modified_guids, "255;255;255;127")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1
    if len(added_guids):
        desc = generate_group_obj_xelem(obj_count, "added_cmps", added_guids, "255;127;255;127")
        def_objs_chunks_xelem.insert(obj_count, et.fromstring(desc))
        obj_count += 1

    return tgt_xml

bef_xml = indicate_changed_objects_as_group(bef_xml, [], modified_guids, added_guids)
out_filename = target_file_name[:target_file_name.rfind(".")]
out_filename += "(bef)_{}.ghx".format(bef_branch.branch.name) 
et.ElementTree(bef_xml).write(
    out_filename,
    pretty_print = True,
    xml_declaration = True,
    encoding = "utf-8" )

aft_xml = indicate_changed_objects_as_group(aft_xml, [], modified_guids, added_guids)
out_filename = target_file_name[:target_file_name.rfind(".")]
out_filename += "(aft)_{}.ghx".format(aft_branch.branch.name) 
et.ElementTree(aft_xml).write(
    out_filename,
    pretty_print = True,
    xml_declaration = True,
    encoding = "utf-8" )



# l_xml_object_count_xelem = fetch_children_by_attrib(bef_xml, "@name=\"ObjectCount\"")[0]
# print("l_xml_object_count_xelem")
# print("tag: ", l_xml_object_count_xelem.tag, ", attrib:", l_xml_object_count_xelem.attrib)
# l_xml_object_count_xelem.text = str(int(l_xml_object_count_xelem.text) + 1)

# l_xml_def_objs = fetch_children_by_attrib(bef_xml, "@name=\"DefinitionObjects\"")[0]
# print("l_xml_def_objs")
# print("tag: ", l_xml_def_objs.tag, ", attrib:", l_xml_def_objs.attrib)

# l_xml_def_objs_chunks = l_xml_def_objs.xpath("chunks")[0]
# print("l_xml_def_objs_chunks")
# print("tag: ", l_xml_def_objs_chunks.tag, ", attrib:", l_xml_def_objs_chunks.attrib)
# l_xml_def_objs_chunks.attrib["count"] = l_xml_object_count_xelem.text
# l_xml_object_xelem = fetch_children_by_attrib(bef_xml, "@name=\"Object\"")
# print("l_xml_object_xelem")
# for c in l_xml_object_xelem:
#     print("tag: ", c.tag, ", attrib:", c.attrib)


# t = ["90e88581-03d1-45dd-9f0a-3442e4e55919"]
# obj_idx = int(l_xml_object_count_xelem.text) - 1
# ret = generate_group_obj_xelem(obj_idx, "added_group", t)
# print(ret)
# g = et.fromstring(ret)
# print(g)
# l_xml_def_objs_chunks.insert(obj_idx, g)


# et.ElementTree(l_xml).write(
#     "./test-output.ghx",
#     pretty_print = True,
#     xml_declaration = True,
#     encoding = "utf-8" )

