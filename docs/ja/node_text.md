<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



<h1>
Node
</h1>



## :tomato: Text Node




### D2 Regex Replace

<figure>
  <img src="../img/regex_replace_2.png">
</figure>

- 正規表現を使って置換ができる
- 複数の条件を指定できる
- 正規表現によるマッチ文字列の再利用ができる（\1、\2 など）
- 対象文字列を「タグ単位」と「全体」で指定できる

#### Input

- `text`
    - 検索対象文字列
- `mode`
  - `Tag`: `text` を改行と「,」で分解し、個別に置換する
  - `Advanced`: `text` をまとめて置換する
- `regex_and_output`
    - 検索文字列と出力文字列の一覧
    - 下記のフォーマットで記入する
    - 出力文字列に何も記載されてない時はマッチした部分を削除する
    - 個数に上限は無い

```
検索文字 1
--
出力文字列 1
--
検索文字 2
--
出力文字列 2
```

#### Output

- `text`
    - 置換処理をしたテキスト

#### Sample

Pony系列のクオリティタグを削除するサンプル。

Mode: `Tag`

Input text
```
score_9, score_8_up, (score_7_up, score_6_up:0.8) , rating_explicit, source_anime, BREAK
1girl, swimsuit
```
Regex Replace
```
.*(score_|rating_|source_).*
--
--
BREAK
--

```

Output text
```
1girl, swimsuit
```


---




### D2 Regex Switcher

  <img src="../img/regex_switcher_1.png">

- 入力テキストを正規表現で検索し、該当したテキストを出力
- 主な目的は Checkpoint 毎のクオリティタグの切り替え
- 入力した `text` の中に合致する文字列を発見すると、対象文字列と、何番目に合致したか（0 から開始）を出力する
- 上の画像では `ioliPonyMixV4.safetensors` を受け取り、検索条件 `pony` に合致したので `score_9` が出力されている
- 最初の検索条件に合致したので `index` は `0` が出力される
- 全ての条件に合致しないと `-1` が出力される
- 文字列の前方結合、後方結合もできる。

#### Input

- `text`
    - 検索対象文字列
- `prefix`
    - 前方に結合する文字列
- `suffix`
    - 後方に結合する文字列
- `regex_and_output`
    - 検索文字列と出力文字列の一覧
    - 下記のフォーマットで記入する
- `pre_delim`
    - `prefix` と `regex_and_output` を接続する時に挟む文字
    - `Comma`: `,` / `Line break`: 改行 / `None`: 何も挟まない
- `suf_delim`
    - `suffix` と `regex_and_output` を接続する時に挟む文字

```
検索文字 1（正規表現も使用可能）
--
出力文字列 1
--
検索文字 2（正規表現も使用可能）
--
出力文字列 2
--
--
合致するものが無い時に出力する文字
```

#### Output

- `combined_text`
    - `prefix` + 出力文字列 + `suffix` を結合した文字列
- `prefix` / `suffix`
    - Input のパススルー

#### 使用例

  <img src="../img/regex_switcher_2.png">

この例では合致した番号（`index`）を [Easy Use](https://github.com/yolain/ComfyUI-Easy-Use) の Text Index Switch に渡して切り替えている。

合致しないと `-1` になってしまうので、全ての文字列に合致する正規表現 `.+` を使ってデフォルト出力の代わりにしている。


---


### D2 Multi Output

<figure>
  <img src="../img/multi.png">
</figure>

- seed や cfg など汎用的なパラメータをリスト出力するノード

#### Input

- `type`
    - `FLOAT`: 浮動小数点数。CFG など
    - `INT`: 整数。steps など
    - `STRING`: 文字列。sampler など
    - `SEED`: 乱数生成ボタンで seed 値を入力できる
- `Add Random`
    - 入力欄に乱数を追加する
    - `type` が `SEED` の時だけ表示される


---

### D2 Filename Template / D2 Filename Template2

<figure>
  <img src="../img/filename_template_2.png">
</figure>

- 日付や他のノードのパラメーターを取り込んで文字列テンプレートを作るためのノード
- `D2 Filename Template2` は複数行対応版です
- 配列、辞書、オブジェクトから値を取得することも可能
- Stable Diffusion webui A1111風のメタデータ書式など、よく使う書式をプリセット登録が可能
  - `custom_nodes/d2-nodes-comfyui/config/template_config.yaml` を編集することで追加可能


#### Input

- `arg_{数字}`
  - 他のノードから値を取り込む
- `format`
    - `%date:{yyyy/MM/dd/hh/mm/ss}%`
      - `yyyy`: 年
      - `MM`: 月
      - `dd`: 日
      - `hh`: 時
      - `mm`: 分
      - `ss`: 秒
    - `%{ノード名}.{key}%`
      - ノード名と、項目名を指定して値を取得する
      - 例：`%Empty Latent Image.width%`: Empty Latent Image のノードから width を取得
    - `%node:{id}.{key}%`
      - ノードIDと、項目名を指定して値を取得する
      - 例：`%node:8.width%`: ID 8 のノードから width を取得
    - `%arg_{数字}%`
      - 入力した値を埋め込む
    - `%arg_{数字}:ckpt_name%`
      - チェックポイント名から `.safetensors` を除外したものを埋め込む
    - `%arg_{数字}:preset.{プリセット名}%`
      - プリセットは `custom_nodes/d2-nodes-comfyui/config/template_config.yaml` を編集することで追加可能
    - `%exec_{数字}[{index}]%`
      - `arg_{数字}` に入力された**配列**から `{index}` の値を取得
    - `%exec_{数字}['{key}']%`
      - `arg_{数字}` に入力された**辞書**から `{key}` の値を取得
    - `%exec_{数字}.{key}%`
      - `arg_{数字}` に入力された**オブジェクト**から `{key}` の値を取得
- `arg_count`
  - 入力項目の増減

<figure>
  <img src="../img/filename_template_3.png">
  <figucaption>`arg_N`に接続したノード情報や、ノード名などを使って取得している</figucaption>
</figure>

<figure>
  <img src="../img/filename_template_4.png">
  <figucaption>生成パラメーターをまとめたオブジェクト `d2_pipe` から `steps`,`sampler_name` を取得している</figucaption>
</figure>

<figure>
  <img src="../img/filename_template_5.png?3">
  <figucaption>`arg_1` に入力された値をプリセット `a1111` を使って出力している。チェックポイント名を追加するために `D2 Pipe` を使用</figucaption>
</figure>

---

### D2 Prompt

<figure>
  <img src="../img/prompt.png?2">
</figure>

- `CHOOSE`ボタンからLoRAを選択し、A1111方式のLoRAプロンプトを挿入できる
- テキスト内のコメントを削除する
- 行頭「#」、行頭「//」、「/\*」〜「\*/」の間が対象
- トークン数を下部に表示
- トークン数の計測のCLIPは"ViT-L/14"を使用。他のCLIPを使いたい時は `D2 Token Counter` をご利用ください


#### コメントアウトのショートカットキーについて

- 全てのテキストボックスでコメントアウトのショートカットキー（ctrl + /）が使用可能
- ショートカットキーは `Settings > D2 > shortcutKey` で変更可能
- 無効にしたい場合は上記の内容を削除する


---

### D2 Token Counter

<figure>
  <img src="../img/token_counter.png">
</figure>

- プロンプトのトークンを数える