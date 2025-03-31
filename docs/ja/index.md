<img src="../img/title.jpg" style="max-width:100%">


<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>


<h1>
D2 Nodes ComfyUI
</h1>

<strong>D2 Nodes ComfyUI</strong> は「ちょっと便利」「シンプル」「汎用性を失わない」をテーマに制作しているカスタムノード集です。

- 汎用性の高い XY Plot
- Checkpoint の系統ごとにクオリティタグを自動切り替えするワークフロー
- 自由に枚数を設定できる Queue ボタン
- その他、様々な「ちょっとだけ便利なノード」があります

## :exclamation: NOTICE

### 不要なカスタムノード
過去に制作した下記のカスタムノードをインストール済みの方は削除してください。

- [ComfyUI-d2-size-selector](https://github.com/da2el-ai/ComfyUI-d2-size-selector)
- [ComfyUI-d2-steps](https://github.com/da2el-ai/ComfyUI-d2-steps)
- [ComfyUI-d2-xyplot-utils](https://github.com/da2el-ai/ComfyUI-d2-xyplot-utils)


## :tomato: Nodes

- <a href="node.md#d2-ksampler--d2-ksampleradvanced">`D2 KSampler / D2 KSampler(Advanced)`</a>
  - プロンプトを STRING で入力・出力する KSampler

- <a href="node.md#d2-pipe">`D2 Pipe`</a>
  - D2 XYPlot Easy、D2 KSampler、D2 Send Eagle で使う d2_pipe の変更、取得をするノード

### Loader

- <a href="node.md#D2-Checkpoint-Loader">`D2 Checkpoint Loader`</a>
  - モデルファイルのフルパスを出力する Checkpoint Loader
- <a href="node.md#D2-Controlnet-Loader">`D2 Controlnet Loader`</a>
  - D2 KSampler に接続してシンプルなワークフローが作れる Controlnet Loader
- <a href="node.md#D2-Load-Lora">`D2 Load Lora`</a>
  - テキストで指定するLoraローダー

### Size

- <a href="node.md#D2-Get-Image-Size">`D2 Get Image Size`</a>
  - 画像サイズの表示と取得
- <a href="node.md#D2-Size-Slector">`D2 Size Slector`</a>
  - プリセットから選択できる画像サイズ、Empty latent 出力ノード
  - 画像からサイズを取得することも可能
- <a href="node.md#D2-Image-Resize">`D2 Image Resize`</a>
  - 小数点３位まで指定可能な画像リサイズ
  - 四捨五入、切り捨て、切り上げが選択できる
- <a href="node.md#D2-Resize-Calculator">`D2 Resize Calculator`</a>
  - 計算した数値は必ず8の倍数になる画像サイズ計算ノード
  - 四捨五入、切り捨て、切り上げが選択できる

### Refiner
- <a href="node.md#D2-Refiner-Steps">`D2 Refiner Steps`</a>
  - Refiner 用の steps を出力する
- <a href="node.md#D2-Refiner-Steps-A1111">`D2 Refiner Steps A1111`</a>
  - img2img で Refiner するために denoise も指定できる
- <a href="node.md#D2-Refiner-Steps-Tester">`D2 Refiner Steps Tester`</a>
  - steps を確認するためのノード

### Merge Node

- <a href="node.md#D2-Model-and-CLIP-Merge-SDXL">`D2 Model and CLIP Merge SDXL`</a>
  - ModelMergeSDXL と CLIPMergeSimple を合体させたノード


### Text

- <a href="node_text.md#D2-Regex-Replace">`D2 Regex Replace`</a>
  - 複数条件の指定が可能なテキスト置換ノード
- <a href="node_text.md#D2-Regex-Switcher">`D2 Regex Switcher`</a>
  - 入力テキストによって出力テキストを切り替えるノード
  - 文字列結合も行える
- <a href="node_text.md#D2-Multi-Output">`D2 Multi Output`</a>
  - SEED / STRING / INT / FLOAT をリスト出力する
- <a href="node_text.md#D2-List-To-String">`D2 List To String`</a>
  - 配列を文字列に変換する
- <a href="node_text.md#D2-Filename-Template">`D2 Filename Template`</a>
  - ファイルネームを作る
- <a href="node_text.md#D2-Delete-Comment">`D2 Delete Comment`</a>
  - テキストのコメントを削除する
- <a href="node_text.md#D2-Token-Counter">`D2 Token Counter`</a>
  - プロンプトのトークンを数える

### Image

- <a href="node_image.md#D2-Load-Image">`D2 Load Image`</a>
  - 画像からプロンプトを取得できる Load Image
  - StableDiffusion webui A1111、NovelAI で作成した画像にも対応
  - マスクエディターを開くボタンが付いてる
- <a href="node_image.md#D2-Load-Folder-Images">`D2 Load Folder Images`</a>
  - フォルダ内の画像を全て読み込む
- <a href="node_image.md#D2-Folder-Image-Queue">`D2 Folder Image Queue`</a>
  - フォルダ内の画像パスを順次出力する
  - 自動で画像枚数分のキューを実行する
- <a href="node_image.md#D2-Grid-Image">`D2 Grid Image`</a>
  - グリッド画像を生成
- <a href="node_image.md#D2-Image-Stack">`D2 Image Stack`</a>
  - 複数の画像をスタックして D2 Grid Image に渡すためのノード
  - 画像を直接出力する
- <a href="node_image.md#D2-EmptyImage-Alpha">`D2 EmptyImage Alpha`</a>
  - αチャンネル（透明度）付きの EmptyImage を出力


### XY Plot

- <a href="node_xy.md#D2-XY-Plot-Easy">`D2 XY Plot Easy`</a>
  - D2 KSampler の項目に限定し、ワークフローをシンプルにした XY Plot ノード
- <a href="node_xy.md#D2-XY-Plot">`D2 XY Plot`</a>
  - 汎用的な XY Plot ノード
  - 必要な回数の Queue を自動的に実行する
- <a href="node_xy.md#D2-XY-Grid-Image">`D2 XY Grid Image`</a>
  - グリッド画像を生成するノード
- <a href="node_xy.md#D2-XY-Prompt-SR">`D2 XY Prompt SR`</a>
  - テキストを検索・置換してリストで返す。D2 XY Plotの前に置くタイプ
- <a href="node_xy.md#D2-XY-Prompt-SR2">`D2 XY Prompt SR2`</a>
  - テキストを検索・置換してリストで返す。D2 XY Plotの後に置くタイプ
- <a href="node_xy.md#D2-XY-Seed">`D2 XY Seed`</a>
  - SEED のリストを出力する
- <a href="node_xy.md#D2-XY-Seed2">`D2 XY Seed2`</a>
  - 指定した個数の SEED のリストを出力する
- <a href="node_xy.md#D2-XY-Checkpoint-List">`D2 XY Checkpoint List`</a>
  - Checkpoint のリストを出力する
- <a href="node_xy.md#D2-XY-Lora-List">`D2 XY Lora List`</a>
  - Lora のリストを出力する
- <a href="node_xy.md#D2-XY-Model-List">`D2 XY Model List`</a>
  - Checkpoint / Lora のリストを出力する
- <a href="node_xy.md#D2-XY-Folder-Images">`D2 XY Folder Images`</a>
  - フォルダ内ファイルのリストを出力する
- <a href="node_xy.md#D2-XY-Annotation">`D2 XY Annotation`</a>
  - D2 Grid Image で表示する見出しテキストを作成
- <a href="node_xy.md#D2-XY-List-To-Plot">`D2 XY List To Plot`</a>
  - 配列を D2 XY Plot 用リストに変換する
- <a href="node_xy.md#D2-XY-String-To-Plot">`D2 XY String To Plot`</a>
  - 改行を含むテキストを `D2 XY Plot` 用リストに変換する



### Float Palet

- <a href="node_float.md#D2-Queue-Button">`D2 Queue Button`</a>
  - 指定した枚数（Batch count）を生成するボタン
- <a href="node_float.md#Prompt-convert-dialog">`Prompt convert dialog`</a>
  - NovelAI と StableDiffusion の weight を相互変換するダイアログ




## :blossom: Changelog

**2025.03.31**

- `D2 Token Counter`: 新規追加

**2025.03.25**

- コメントアウトのショートカットキー（ctrl + /）を追加
- `D2 XYPlot Easy Mini`: `D2 XYPlot Easy` の出力スロット制限バージョンを追加

**2025.03.23**

- `D2 Delete Comment`: 新規追加
- `D2 Load Lora`: A1111フォーマットを利用可能にするオプションを追加
- `D2 Model List`: A1111フォーマットで取得するオプションを追加

**2025.02.27**

- `D2 Load Lora`: 新規追加
- `D2 Multi Output`: x_list/ylist 出力を追加

**2025.02.23**

- `D2 Model and CLIP Merge SDXL`: checkpointのマージノードを追加

**2025.01.20**

- `D2 XY Seed2`: 新規追加
- `D2 XY Plot / D2 XY Plot Easy`: XYプロットの開始位置を指定可能にした
- `D2 XY Plot / D2 XY Plot Easy`: XYプロットの予想残り時間の表示を追加
- `D2 Regex Replace`: 置換文字列に空白を指定可能にした

**2024.12.28**

- `D2 Pipe`: 新規追加
- `D2_KSampler / D2_XYPlotEasy`: xy_pipe の名前を d2_pipe に変更

**2024.12.18**

- `D2 Filename Template`: 新規追加
- `D2 Grid Image`: グリッド画像出力のトリガーを画像枚数で指定できるようにした

**2024.12.16**

- `D2 XY String To Plot`: 新規追加
- `D2 XY Grid Image`: ラベルの改行に対応
- `D2 XY Grid Image`: ラベル出力の ON/OFF を選択可能にした
- `D2 XY Prompt SR`: 改行を含むテキストに対応
- `D2 XY Plot Easy`: seed で `-1` を指定した時に `x/y_annotation` にランダム値を登録するように変更

**2024.12.14**

- `D2 KSampler`: `D2 XY Plot Easy` と接続するための `xy_pipe` を追加
- `D2 XY Grid Image`: `D2 XY Plot`、`D2 XY Plot Easy` と接続するための `grid_pip` を追加
- `D2 XY Plot Easy`: を新規追加
- `D2 XY Model List`: ファイル名、日付ソートを追加。Sampler、Schedulerのリスト取得に対応。

**2024.12.05**

- `D2 KSampler` / `D2 KSampler` に Conditioning 出力を追加

**2024.11.27**

- `D2 Preview Image` を新規追加

**2024.11.23**

- `D2 Model List` を新規追加

**2024.11.21**

- `D2 Checkpoint Loader`: Vpred（v_prediction）に関する設定を追加
- `D2 Image Resize`: Latentを出力できるように変更した

**2024.11.20**

- `D2 Image Resize`: アップスケールモデル（SwinIR_4xなど）を使えるようにした

**2024.11.18**

- 一気にたくさん追加しました
- `D2 Controlnet Loader`、`D2 Get Image Size`、`D2 Grid Image`、`D2 Image Stack`、`D2 List To String`、`D2 Load Folder Images`
- XY Plot 関係も追加しました
- `D2 XY Annotation`、`D2 XY Checkpoint List`、`D2 XY Folder Images`、`D2 Grid Image`、`D2 XY List To Plot`、`D2 XY Lora List`、`D2 XY Plot`、`D2 XY Prompt SR`、`D2 XY Prompt SR2`、`D2 XY Seed`
- 既存のノードも変更してるので詳細はコミット履歴を参照してください

**2024.11.02**

- `D2 Regex Switcher`: 入力テキストの確認用テキストエリアの表示・非表示切り替えを追加

**2024.10.28**

- `Prompt convert`: NovelAI と StableDiffusion のプロンプトを相互変換するダイアログを追加
- `D2 Folder Image Queue`: 画像生成枚数が同じにならない不具合を修正

**2024.10.26**

- `D2 EmptyImage Alpha` を新規追加
- `D2 Image Resize` を新規追加
- `D2 Resize Calculator` を新規追加

<details>
<summary><strong>2024.10.24</strong></summary>

- `D2 Regex Replace` を新規追加
- `D2 Folder Image Queue` を新規追加
- `D2 Load Image`: 画像パスの入力を追加
- `D2 KSampler(Advanced)`: Input に Positive / Negative Conditioning を追加

</details>


<details>
  <summary><strong>2024.10.19</strong></summary>

- `D2 Queue Button` を追加

</details>


<details>
  <summary><strong>2024.10.18</strong></summary>

- `D2 Size Selector`: 画像からサイズ取得できる機能を追加
- `D2 Size Selector`: リサイズの方法を「四捨五入」と「切り落とし」から選択可能にした

</details>


<details>
<summary><strong>2024.10.14</strong></summary>

- `D2 Load Image`: Exif データのない画像（クリップボードからのペーストなど）の時にエラーになるのを修正

</details>


<details>
  <summary><strong>2024.10.11</strong></summary>

- `D2 Regex Switcher`: 文字列を結合する時に挟む文字を指定できるようにした

</details>


<details>
  <summary><strong>2024.10.10</strong></summary>

- `D2 Load Image`: "Open Mask Editor"ボタンを追加

</details>

<details>
  <summary><strong>2024.10.08</strong></summary>
  
  - `D2 Load Image`: 新規追加

</details>

<details>
  <summary><strong>2024.10.03</strong></summary>

- `D2 Regex Switcher`: 検索にマッチしても素通りする不具合を修正

</details>


<details>
  <summary><strong>2024.10.02</strong></summary>

- 既存のノードを統合して作成

</details>


