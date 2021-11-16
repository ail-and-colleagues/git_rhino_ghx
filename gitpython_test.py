
import git

# https://gitpython.readthedocs.io/en/stable/reference.html


repo = git.Repo("./")
print("repo: ", repo)

remote_repo = repo.remotes

print("remote_repo: ", remote_repo)
print("remote_repo.origin: ", remote_repo.origin)
print("remote_repo.origin.url: ", remote_repo.origin.url)
# print("remote_repo.origin.url: ", remote_repo.origin.commit)

fetched = remote_repo.origin.fetch()
print("fetched: ", fetched[0].name)
for f in fetched:
    print(f.commit.tree.blobs)



aa
# true means some modified files exist
print("is_dirty: ", repo.is_dirty())

heads = repo.heads
print("heads: ", heads)
# -> heads:  [<git.Head "refs/heads/main">]

print("heads.master.commit: ", heads.main.commit)
# -> heads.master.commit:  14abcb7e89f17944cea2d70cb9f91038e7694bbd

# a tag is a special mark to indicate milestone-like commit
print(repo.tags)

blobs = repo.heads.main.commit.tree.blobs
print("blobs: ", blobs)
for b in blobs:
    print(b.name)
    print(b.data_stream.read())

# Git objects consist Blobs, Trees, Commits and Tags.
# These have common fields: type, size, hexsha and binsha.
t = heads.main.commit.tree
print("type: ", t.type, ", size: ", t.size, ", hexsha: ", t.hexsha)



# hcommit = repo.head.commit
# print(hcommit.diff())                  # diff tree against index
# print(hcommit.diff('HEAD~1'))          # diff tree against previous tree
# print(hcommit.diff(None))              # diff tree against working tree

# index = repo.index
# index.diff()                    # diff index against itself yielding empty diff
# index.diff(None)                # diff index against working copy
# index.diff('HEAD')      