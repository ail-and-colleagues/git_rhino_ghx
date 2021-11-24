# git_rhino_ghx
test project of version control for rhinoceros grasshopper.

## ghx_diff.py
: Create a difference-indicated .ghx by specifying branches and a filename.

ファイル名（.ghx）と前・後のブランチ名を指定すると次図のような差分:diffの表現された.ghxを{_original file name_}\_diff({_from-branch-name_}\_to_{_to-branch-name_}).ghxとして出力します。
conflictした.ghxを比較する際に便利だと思われる。  
![image](https://user-images.githubusercontent.com/39890894/143173696-1133ab80-4001-4fd6-bf1f-934d37d7fc65.png)

## ghx_to_dot.py
: Create a network-like graph by parsing .ghx.

アルゴリズムの構成をネットワークのようなグラフで表し.pngで保存します。.ghxが大凡どのような処理であったかGithub上で確認できます。コンポーネントのhashなんかを付記しても便利だと思われる。
![image](https://user-images.githubusercontent.com/39890894/143174556-d42e2eec-5cf7-40d2-996f-404d885f84bd.png)

## links
Version control (grasshopper forum)  
https://www.grasshopper3d.com/forum/topics/version-control
