# assist-create-package-design

学士論文のための研究で制作した，包装紙デザインを自動生成するアプリケーション

## 概要

近年様々な分野で自動化が進む中で，手土産等のラッピングは手作業で行われることが多い．だが出来栄えが個人の経験や技術に左右されたり，包装後の模様の見た目に破断が生じたりといった問題がある．ここでは，包装後に模様の連続性が保たれるような包装紙デザイン(ストライプ模様)を自動生成するアプリケーションを制作した．

[学生大会での概要](https://www.ipsj.or.jp/event/taikai/83/ipsj_web2021/data/pdf/6Y-03.html)
[先行研究](https://www.iieej.org/journal-of-the-society/)

## インストール

リポジトリをクローンする

```bash
git clone https://github.com/s-marika/assist-create-package-design.git
```

依存ライブラリをインストールする
今回はpipenvを使用する

### Python3のインストール

Python3.7以上をインストールする([参考](https://www.python.jp/install/windows/install.html))

### pipenvのインストール

```bash
pip install pipenv
```

### pipenvで依存ライブラリをインストール

```bash
pipenv install
```

## 使い方

### アプリの起動

app.pyを実行する．

```bash
pipenv run python app.py
```

もしくは

```bash
pipenv shell  # 仮想環境に入る
python app.py
```

### 起動後の使い方

1. 初めに，包みたい箱の3辺の長さをmm単位で入力．

1. オプションにチェックを入れ，詳細設定をする．
    * ストライプの幅，ストライプ間の幅，オフセット，ストライプの角度などを入力可能．単色ストライプを生成する場合はストライプの色を，画像を使用したストライプの場合は使用する画像を入力する．

1. 最適化をクリックすると，プレビューが出力される．

1. プレビューを確認し，問題がなければ画面左上のメニューバーから画像を保存する．  
保存形式は，単色ストライプの場合はSVGとPDFを，画像ストライプの場合はPDFを選択できる．

1. 保存したPDFを印刷する．PDFに包装のためのガイドラインが含まれている場合は，両面印刷にする．

1. 紙を適切な大きさに切り，包装する．

## 開発環境

* Windoows10 Home
* Python3.8
