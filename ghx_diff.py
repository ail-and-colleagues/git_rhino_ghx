import sys
from logging import exception
import git

from ghx_to_dot import parse_components
import xml.etree.ElementTree as et

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


# from xml.etree.ElementTree import XMLParser
# >>> class MaxDepth:                     # The target object of the parser
# ...     maxDepth = 0
# ...     depth = 0
# ...     def start(self, tag, attrib):   # Called for each opening tag.
# ...         self.depth += 1
# ...         if self.depth > self.maxDepth:
# ...             self.maxDepth = self.depth
# ...     def end(self, tag):             # Called for each closing tag.
# ...         self.depth -= 1
# ...     def data(self, data):
# ...         pass            # We do not need to do anything with data.
# ...     def close(self):    # Called when all data has been parsed.
# ...         return self.maxDepth

# class line_to_xml_element:
#     def __init__(self):
#         self.is_end = False
#         self.map = list()
#         self.depth = 0
#         self.element_idx = 0
#         def start(self, tag, attrib):
#             self.depth += 1
#             print("start: ", tag, attrib)



repo = git.Repo("./")

left_branch = Branch(repo, "main")
right_branch = Branch(repo, "test")
print(left_branch.blob_dict.keys())

left = left_branch.fetch_blob("./sample/xmlTest.ghx")

print(left.data_stream.read().decode("utf-8"))
# print(left.branch.commit.tree.trees[0].path)