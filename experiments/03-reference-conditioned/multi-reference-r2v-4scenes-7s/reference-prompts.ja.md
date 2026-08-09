# リファレンスシート生成プロンプト

English exact-prompt record: [reference-prompts.md](./reference-prompts.md)

## 位置づけ

以下の3枚のPNGは、複数リファレンスR2V実験の権威ある固定入力です。組み込みの`image_gen`機能で生成し、`runtime/4090/input/`へコピーして使用しました。モデルに渡したprompt本文は英語のまま保持しており、完全なpromptは英語版に収録しています。

| リファレンス | 用途 | 実行入力 |
|---|---|---|
| Background sheet | 近未来Tokyo rooftop greenhouse / observation deckの背景 | `runtime/4090/input/MiniMax_H3_R2V_background_sheet.png` |
| Mina sheet | 20代後半の日本人女性キャラクター | `runtime/4090/input/MiniMax_H3_R2V_mina_sheet.png` |
| Ren sheet | 30代前半の日本人男性キャラクター | `runtime/4090/input/MiniMax_H3_R2V_ren_sheet.png` |

## シートの役割

- Background: 夕方の屋上温室・展望デッキの建築、濡れた反射面、orange-blueの光を4パネルで固定。
- Mina: teal streakのある短いdark bob、右眉上の傷、tan utility jacket、rust-red scarfなどを4方向で固定。
- Ren: wavy black hair、左耳のsilver earpiece、charcoal long coat、olive knit sweaterなどを4方向で固定。

## 再現時の注意

英語版には各シートの完全なprompt、構図、照明、禁止事項が保存されています。新規生成時も同じ英語promptを使用し、シートを背景1枚＋キャラクター2枚の3入力としてR2V workflowへ接続してください。これは同一人物・同一背景を複数シーンで維持するための実験入力であり、X投稿の元素材であるという主張ではありません。
