# 每日早報

每日國際新聞早報與 AI 科技發展，依日期與分類保存。網站：https://ktungl.github.io/News/

## 運作方式

- 每天早上由 Claude Code Routine 依 [`PROMPT.md`](PROMPT.md) 搜尋新聞，寫入 `data/YYYY-MM-DD.json` 並推到 `main`。
- `scripts/build.py` 會驗證資料、產生同名 Markdown（`data/YYYY-MM-DD.md`），並更新 `data/index.json`。
- `index.html` 是純靜態頁面，讀取 JSON 後顯示當日早報、分類瀏覽、歷史日期與標題搜尋。GitHub Pages 直接從 `main` 根目錄提供。

## 本機預覽

```sh
python3 -m http.server 8000   # 開啟 http://localhost:8000
```

## 調整內容

要改早報的主題、篇幅或分類，修改 `PROMPT.md` 即可。如果新增分類，也要同步更新 `scripts/build.py` 的 `CATEGORIES`。
