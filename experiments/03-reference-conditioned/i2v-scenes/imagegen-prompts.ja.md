# ImageGen開始フレーム記録

English exact-prompt record: [imagegen-prompts.md](./imagegen-prompts.md)

## 位置づけ

以下の4枚のPNGは、組み込みの`image_gen`機能で生成した後、リポジトリのruntime入力ディレクトリへコピーし、I2V workflowで変更せずに使用した固定入力です。モデル入力promptは再現性のため英語のまま保持しており、完全なprompt本文は英語版に収録しています。

ImageGenの出力サイズは`1672×941`、MiniMax-H3 workflowの目標サイズは`1344×768`です。

| シーン | 実行入力 | bytes | SHA-256 |
|---|---|---:|---|
| Car / 車 | `runtime/4090/input/MiniMax_H3_I2V_scene_car_imagegen_start.png` | 1,979,098 | `AA18AB747483D6761E897456EED5F12CFB82402CC891B64484893D1AEF5A8B0A` |
| Sports / スポーツ | `runtime/4090/input/MiniMax_H3_I2V_scene_sports_imagegen_start.png` | 1,945,542 | `33B52086889F97ADE8FB2EA8F23C3F25214498A5015881D33B9E8E42F3D3130C` |
| Illustration / イラスト | `runtime/4090/input/MiniMax_H3_I2V_scene_illustration_imagegen_start.png` | 2,108,414 | `09D56EF3CD1947CE66E5BC9F019FA4DED2A636A14D42947022268134546D7A6F` |
| Battle / バトル | `runtime/4090/input/MiniMax_H3_I2V_scene_battle_imagegen_start.png` | 2,350,823 | `80D12E69F6E8B629D91A7E1F490C620A77D6CEC37D63B559CBADFDC497E9421A` |

## 再現時の注意

- `Source output`の一時パスはImageGen実行環境に依存します。再現時は英語版のpromptを使って新しい開始フレームを生成するか、追跡済みのruntime入力を用います。
- PNGのコピー先、prompt本文、生成時の制約、各ファイルのhashは英語版を正本として確認できます。
- この入力はLightX2Vのシーン汎化実験に対応し、X投稿が同じ画像を使ったという意味ではありません。
