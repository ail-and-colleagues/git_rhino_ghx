# git_rhino_ghx
test project of version control for rhinoceros grasshopper.

## ghx_diff.py
: Create a difference-indicated .ghx by specifying branches and a filename.
```
  -h, --help            show this help message and exit
  -p PATH_TO_REPO, --path_to_repo PATH_TO_REPO
                        path to a repository
  -t TARGET, --target TARGET
                        target .ghx file
  -l LEFT_BRANCH, --left_branch LEFT_BRANCH
                        left branch
  -r RIGHT_BRANCH, --right_branch RIGHT_BRANCH
                        right branch
  -i, --ignore_positon  ignore component position changes
```  
ファイル名(.ghx)と前(left)・後(right)のブランチ名を指定すると次図のような差分:diffの表現された.ghxを
*{target\_file\_name}*(*{left\_branch\_name}*\_to\_*{right\_branch\_name}*)\_diff.ghxとして出力します。
conflictした.ghxを比較する際に便利だと思われる。  
![image](https://user-images.githubusercontent.com/39890894/143173696-1133ab80-4001-4fd6-bf1f-934d37d7fc65.png)

### Assumed Workflow
1. create a new branch: *dev_something*.  
**git checkout -b *dev_something***
1. do something in *target\_file.ghx*.
1. stage *target\_file.ghx*.  
**git add *target\_file.ghx***
1. commit changes.  
**git commit -m "add something"**
1. switch to the main branch.  
**git checkout main**
1. try to merge.  
**git merge *dev_something***
1. solve conflicts using  **ghx_diff.py** in the main branch (if causes conflicts).
1. adopt the main branch and discard *dev_something* using --ours.  
**git checkout --ours *target\_file.ghx***
1. stage *target\_file.ghx*.  
**git add *target\_file.ghx***
1. commit.  
**git merge --continue**
1. remove *dev_something***  
**git branch -d *dev_something***

## ghx_to_dot.py
: Create a network-like graph by parsing .ghx.

アルゴリズムの構成をネットワークのようなグラフで表し.pngで保存します。.ghxが大凡どのような処理であったかGithub上で確認できます。コンポーネントのhashなんかを付記しても便利だと思われる。  
![image](https://user-images.githubusercontent.com/39890894/143174556-d42e2eec-5cf7-40d2-996f-404d885f84bd.png)

## links
Version control (grasshopper forum)  
https://www.grasshopper3d.com/forum/topics/version-control
