# Sunwood X投稿シミュレーション — MiniMax-H3 3060 約720p

- 作成日時: 2026-08-07 JST
- 対象アカウント: `@hAru_mAki_ch`
- 状態: **承認後に投稿完了**
- 構成: **2スレッド**。T2VとI2Vを分離し、各メイン投稿に実生成動画を1本だけ添付
- プロジェクトのGitHub: 未作成。`<repo-root>` はGitリポジトリではない
- artifact link: <https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo>
- 調査元: <https://x.com/TlanoAI/status/2084940455809286397>

## シミュレータ

Tailscale URL:

<https://madesk.tail8be30.ts.net:8879/>

ローカルサーバーを次の条件で起動している。

```powershell
python -m http.server 8791 --bind 127.0.0.1 --directory <repo-root>\sunwood-x-simulator-2026-08-07
tailscale funnel --bg --yes --https=8879 8791
```

シミュレータはX APIを呼ばず、投稿本文・線形返信順・実MP4・実ファイルパスを表示する。公開ルートはシミュレータ専用ディレクトリに限定し、`assets` 内の動画・ポスターは元ファイルとSHA-256が一致するプレビューコピーである。

## スレッドA — 3060 T2V

### Main post（動画1本）

```text
MiniMax-H3 × Docker Compose、RTX 3060で約720p T2Vやってみた！！！

WSL再起動後に、1280×704、25 steps、124 framesを生成。
実測wall 16分01秒、OOMなし、blackdetectも0。

3060でも約720p、できたぞ🔥
```

Attachment:

- path: `<repo-root>\runtime\3060\output\video\MiniMax_H3_T2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4`
- provenance: 3060 Docker Compose実験で生成した実MP4
- SHA-256: `BB7BC89D6279FA639165D80F1E894B43DCA3907AC2AF84BCCA3F52DA85222BB4`
- media: H.264 / 1280×704 / 24fps / 124 frames / 5.166667秒
- runner wall: 961.655秒（16分01秒）
- blackdetect interval count: 0
- crop/edit/redaction: なし

### Reply 1（調査元URLのみ1件）

```text
元にした3060条件の投稿はこちら。
今回のDocker Compose検証では、WSL再起動後の1280×704まで追加で試したぞ。
https://x.com/TlanoAI/status/2084940455809286397
```

### Reply 2（artifact URLのみ1件、Reply 1への返信）

```text
使ったComfyUIノードと、今回の実験ログ。
workflow／処理時間／出力SHA-256まで記録しているぞ。
https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo
```

## スレッドB — 3060 I2V

### Main post（動画1本）

```text
MiniMax-H3 × imagegen、RTX 3060で約720p I2Vやってみた！！！

imagegenで作った開始フレームを接続して、1280×704、25 steps、124 framesを生成。
実測wall 13分21秒、OOMなし、blackdetectも0。

開始画像の構図を保ったまま霧が動いた。これは熱い🔥
```

Attachment:

- path: `<repo-root>\runtime\3060\output\video\MiniMax_H3_I2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4`
- provenance: 3060 Docker Compose実験で生成した実MP4。開始フレームのみimagegenで作成
- SHA-256: `5437ADD0A093793E72DE178F0F8744A4D0539805319A8C4797E831B0C7011BC4`
- media: H.264 / 1280×704 / 24fps / 124 frames / 5.166667秒
- runner wall: 800.840秒（13分21秒）
- blackdetect interval count: 0
- crop/edit/redaction: なし
- start frame: `<repo-root>\runtime\3060\input\MiniMax_H3_I2V_1280x704_start.png`
- start frame SHA-256: `BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8`
- imagegen prompt record: `assets\i2v_start_frame_generation.md`

### Reply 1（調査元URLのみ1件）

```text
比較の起点にした3060条件の投稿。
T2Vだけでなく、同じCompose環境でI2Vも確認したぞ。
https://x.com/TlanoAI/status/2084940455809286397
```

### Reply 2（artifact URLのみ1件、Reply 1への返信）

```text
I2Vの開始フレームはimagegenで作成。生成記録と処理時間を残しているぞ。
使ったComfyUIノードはこちら。
https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo
```

## 事前検証

Sunwoodの `scripts/preflight.ps1` を、各スレッドについて「対象アカウント・本文・全返信・実MP4・Tailscale URL」をそのまま渡して実行した。

- T2V: `ok: true`
- I2V: `ok: true`
- メイン本文: URLなし
- 各返信: URLは1件ずつ
- 各スレッド: メディア1件、実MP4、H.264、1280×704、横長
- 重複本文: ローカル履歴と一致なし
- writer: `scripts/maki-x-write.py` を事前検証に指定
- Xへの書き込み: 完了。6投稿を読み戻して検証済み

Exact payload JSON:

`sunwood-x-thread-payload-2026-08-07.json`

実験根拠:

- `runtime\3060\benchmark\h3-291fee87-c0b1-4cf3-a63c-df62f5ee6262.md`
- `runtime\3060\benchmark\h3-b6ab37fa-1af5-4f45-b7e3-7d92d34056a9.md`
- `benchmark-results-2026-08-07.json`

この内容から本文・返信・動画・順序を変更する場合は、再シミュレーションと再preflightが必要。

## 投稿結果

投稿前に対象アカウント `@hAru_mAki_ch` のidentity確認と、T2V／I2Vそれぞれの最終preflight `ok: true` を実行した。

### T2V thread

- main: <https://x.com/hAru_mAki_ch/status/2085730512677855266>
- 調査元 reply: <https://x.com/hAru_mAki_ch/status/2085730980636316050>
- artifact reply: <https://x.com/hAru_mAki_ch/status/2085731132197527934>
- 線形関係: main → 調査元 reply → artifact reply
- 動画media key: `7_2085730499633520640`

### I2V thread

- main: <https://x.com/hAru_mAki_ch/status/2085731260169953315>
- 調査元 reply: <https://x.com/hAru_mAki_ch/status/2085731363010093554>
- artifact reply: <https://x.com/hAru_mAki_ch/status/2085731439577034821>
- 線形関係: main → 調査元 reply → artifact reply
- 動画media key: `7_2085731245888245761`

X APIの読み戻しでも、各mainはmedia key 1件、各replyのURLは1件、replyの親IDは直前投稿IDになっていることを確認した。投稿直後のAPI返却テキストに表示されるURLはXの `t.co` 表記だが、実体のexpanded URLは承認payloadのURLと一致する。
