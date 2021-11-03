# assist-create-package-design



[先行研究](https://www.iieej.org/journal-of-the-society/)

## install

リポジトリをクローンする

```bash
$ git clone https://github.com/s-marika/assist-create-package-design.git
```

依存ライブラリをインストールする
今回はpipenvを使用する

### pipenvのインストール

```bash
$ pip install pipenv
```

### pipenvで依存ライブラリをインストール

```bash
$ pipenv install
```

## usage

### アプリの起動

app.pyを実行する．

```bash
$ pipenv run python app.py
```

もしくは

```bash
$ pipenv shell  # 仮想環境に入る
$ python app.py
```

### 起動後の使い方

本アプリでは，包装が終了した時に模様が破綻しないようなストライプ柄の包装紙を生成し，出力する．

初めに，包みたい箱の3辺の長さをmm単位で入力．

オプションにチェックを入れ，詳細設定をする．

最適化をクリックすると，プレビューが出力される．

プレビューを確認し，問題がなければ画面左上のメニューバーから画像を保存する．

保存形式は，単色ストライプの場合はSVGとPDFを，画像ストライプの場合はPDFを選択できる．
