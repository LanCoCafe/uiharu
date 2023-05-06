# 初春 (ういはる/uiharu)

一個將 ChatGPT 結合至 Discord 的機器人

## 關於

在一個段考前的下午，我們意外聊到了有關友情的話題：

- N - [Nat1an][nat1an-github]
- R - [凛にゃん][rinnyanneko-github]
- C - 匿名朋友

```
C: 反正我只想要平常有人可以跟我談生活小是這樣就夠惹 但貌似也蠻困難的
N: ChatGPT
C: 窩不要
N: 我可以讓他變得有形象又有語音 這樣要嗎
R: 期待欸 (RE: N)
```

然後這個 Repository 就誕生了。

荒謬至極，對吧？

## 使用

你需要先 `clone` 這個 Repository，並安裝所有的依賴：

```shell
git clone https://github.com/Nat1anWasTaken/uiharu.git
pip install -r requirements.txt
```

以及 [Google Chrome][Chrome-Download] 和 [Chrome Web Driver][Chrome-Driver-Download]

運行機器人

將 `.env.example` 重新命名至 `.env`，並填入以下數值：

```dotenv
DISCORD_TOKEN=your_bot_token
CHATGPT_TOKEN=your_chatgpt_session_token
BRAINWASH_PATH=your_brainwash_path
```

- `DISCORD_TOKEN` - 你的 Discord Bot Token
- `CHATGPT_TOKEN` - 你的 ChatGPT Session Token，關於如何獲取，請查看 `acheong08/ChatGPT`
  的 [Setup][acheong08-ChatGPT-Setup] 文檔
- `BRAINWASH_PATH` - `brainwash.txt` 的路徑，預設為 `./brainwash.txt`

接下來，運行

```shell
python main.py
```

> 在運行前，機器人會將 `brainwash.txt` 中的每一行依序傳入 ChatGPT，你可以自訂這個檔案

## 計畫

- [x] 文字對話
- [ ] 語音辨識
- [ ] 語音合成

[nat1an-github]: https://github.com/Nat1anWasTaken

[rinnyanneko-github]: https://github.com/rinnyanneko

[acheong08-ChatGPT-Setup]: https://github.com/acheong08/ChatGPT/wiki/Setup

[Chrome-Download]: https://chrome.google.com

[Chrome-Driver-Download]: https://chromedriver.chromium.org/downloads
