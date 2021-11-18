import sys
from logging import exception


import git
from git import diff
from lxml import etree as et
import difflib
from misc.xml_lib import Line_to_Xml_Element

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
        # remove spaces and the last "@@" from the header.
        self.header = diff_chunk[0].replace(" ", "")[:-2]
        self.content = diff_chunk[1:]
        print("Diff_Chnk head: ", self.header)

class Diff_Mgr:
    def __init__(self, unified_diff):
        diff = "\n".join([str(d) for d in unified_diff])
        # print(diff)
        diff = diff.split("\n@@")
        self.diff_chunk_list = list()
        # diff[0] is a header-like description of unified_diff.
        for i, d in enumerate(diff[1:]):
            self.diff_chunk_list.append(Diff_Chunk(d))


repo = git.Repo("./")

left_branch = Branch(repo, "main")
right_branch = Branch(repo, "test")
print(left_branch.blob_dict.keys())

target_file_name = "./sample/xmlTest.ghx"
left = left_branch.fetch_blob(target_file_name)
right = right_branch.fetch_blob(target_file_name)

left_decoded = left.data_stream.read().decode("utf-8")
right_decoded = right.data_stream.read().decode("utf-8")

# print(left_decoded)
parser = et.XMLParser(target=Line_to_Xml_Element())
parser.feed(left_decoded)
l_map = parser.close()

parser = et.XMLParser(target=Line_to_Xml_Element())
parser.feed(right_decoded)
r_map = parser.close()

print("l_map[:15]")
print(l_map[:15])

print("r_map[:15]")
print(r_map[:15])

unified_diff = difflib.unified_diff(left_decoded.split("\n"), right_decoded.split("\n"))
print("unified_diff: ", unified_diff)

# for i, d in enumerate(unified_diff):
#     print(d)

diff_mgr = Diff_Mgr(unified_diff)

# k = 88 - 1
# l_xml = et.fromstring(left_decoded)
# print(l_xml)
# # t_elem = l_xml
# t_idx = l_map[k]
# t_elem = l_xml.xpath("//*")[t_idx]
# print(t_elem.tag, t_elem.attrib, t_elem.text)
# print(left_decoded.split("\n")[k])

test_diff = """
@@ -85,9 +85,9 @@

         </chunk>
         <chunk name="DefinitionObjects">
           <items count="1">
-            <item name="ObjectCount" type_name="gh_int32" type_code="3">14</item>
+            <item name="ObjectCount" type_name="gh_int32" type_code="3">16</item>
           </items>
-          <chunks count="14">
+          <chunks count="16">
             <chunk name="Object" index="0">
               <items count="2">
                 <item name="GUID" type_name="gh_guid" type_code="9">59e0b89a-e487-49f8-bab8-b5bab16be14c</item>
"""