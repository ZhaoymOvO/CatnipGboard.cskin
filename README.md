# Catnip Gboard - 倉輸入法 / 元書輸入法 鍵盤皮膚

這是一款借鑑 **Gboard** 佈局靈感，專為 **倉輸入法 / 元書輸入法 (Hamster Keyboard v3)** 打造的現代化多層鍵盤皮膚。

本皮膚嚴格根據自訂佈局規範構建，實現了 **頂部數字行**、**右上角提示字元與上滑手勢**、**中英獨立的雙層符號面板**、**直接跳轉元書內嵌預設分類符號面板（Fallback）**，以及**分別返回中文和英文鍵盤的獨立數字九宮格鍵盤**。

---

## 核心設計亮點 (ฅ'ω'ฅ)

1. **Gboard 風格 5 行主鍵盤**：
   * **中文主鍵盤 (PINYIN)** 與 **英語主鍵盤 (ALPHA)** 第一行皆自帶獨立數字行 `1 2 3 4 5 6 7 8 9 0`，快速鍵入數字無需切換面板。
   * 字母按鍵右上角標記次要符號，支援**直接上滑鍵入**（Swipe Up）。
   * **直引號特殊邏輯**：遵循設定，除了中文鍵盤中的直引號 `"` (`x"` 上滑) 傳遞給輸入法引擎（走 Rime 智慧引號/分詞）之外，其他符號全部使用 `symbol` 直接上屏，不經過輸入法干擾。

2. **中英各自獨立的「雙層 5 行符號面板」**：
   * **全鍵盤高度統一**：所有面板統一為 5 行佈局，按鍵高度、底欄位置與主鍵盤 100% 對齊無跳動，點選符號後持續停留在符號面板（不自動切回主鍵盤），需返回時再點選底部的「返回 / ABC」。
   * **符號層 1 (`ZH_SYM1` / `EN_SYM1`)**：頂部配置 8 個文字編輯與游標控制按鈕（`⬅️` `⬆️` `全選` `剪下` `複製` `黏貼` `⬇️` `➡️`，採用 SF Symbols），次行包含完整數字行 `1..0`，以及全半形標點符號。
   * **符號層 2 (`ZH_SYM2` / `EN_SYM2`)**：頂部同樣保留完整數字行 `1..0`，涵蓋數學貨幣符號、特殊括號與冷門標點。
   * **預設符號兜底 (`GOTO_DEFAULT_SYM`)**：在第二層符號面板的底部正中央配置跳轉鍵，點選即可打開元書輸入法**內嵌的預設分類符號面板 (`symbolic` Fallback)**。

3. **分別返回中英的「雙份數字九宮格鍵盤」**：
   * **中文數字鍵盤 (`ZH_NUM`)**：底部 `[BACK]` 鍵標記為「**返回**」，點選直接回到中文主鍵盤 (`PINYIN`)；`!?#` 鍵跳轉回中文符號頁面 (`ZH_SYM1`)。
   * **英文數字鍵盤 (`EN_NUM`)**：底部 `[BACK]` 鍵標記為「**ABC**」，點選直接回到英文主鍵盤 (`ALPHA`)；`!?#` 鍵跳轉回英文符號頁面 (`EN_SYM1`)。

---

## 面板跳轉拓撲圖

```text
[中文主鍵盤 PINYIN] ──── ?123(custom:zh_sym1) ───► [中文符號1 ZH_SYM1] ───── =\< ─────► [中文符號2 ZH_SYM2]
       ▲                                                    │                                     │
       │                                                   123                                   更多 (symbolic)
       │                                                    ▼                                     ▼
       └──────────────────── 返回 ────────────────── [中文九宮數字 ZH_NUM]            [元書內嵌預設符號面板]


[英文主鍵盤 ALPHA]  ──── ?123(custom:en_sym1) ───► [英文符號1 EN_SYM1] ───── =\< ─────► [英文符號2 EN_SYM2]
       ▲                                                    │                                     │
       │                                                   123                                   更多 (symbolic)
       │                                                    ▼                                     ▼
       └──────────────────── ABC ─────────────────── [英文九宮數字 EN_NUM]            [元書內嵌預設符號面板]
```

---

## 目錄結構

```text
cskin/
├── config.yaml                    # 核心映射表（含 pinyin, alphabetic, numeric, zh_sym1, zh_sym2, en_sym1, en_sym2, en_num）
├── layout.txt                     # 鍵位與手勢原始配置表
├── README.md                      # 使用與設計說明文檔
├── demo.png                       # 預覽展示圖
├── dist/
│   └── CatnipGboard.cskin         # 打包完成的皮膚安裝包
├── light/                         # 淺色模式 8 大面板 YAML
│   ├── pinyinPortrait.yaml / pinyinLandscape.yaml
│   ├── alphabeticPortrait.yaml / alphabeticLandscape.yaml
│   ├── zhSym1Portrait.yaml / zhSym1Landscape.yaml
│   ├── zhSym2Portrait.yaml / zhSym2Landscape.yaml
│   ├── enSym1Portrait.yaml / enSym1Landscape.yaml
│   ├── enSym2Portrait.yaml / enSym2Landscape.yaml
│   ├── zhNumPortrait.yaml / zhNumLandscape.yaml
│   └── enNumPortrait.yaml / enNumLandscape.yaml
├── dark/                          # 深色模式 8 大面板 YAML
├── jsonnet/                       # 模組化原始碼
└── scripts/
    └── build.py                   # Python 3 建置工具（基於 Homebrew Python）
```

---

## 建置與安裝

使用 Homebrew Python 重新編譯或打包皮膚：

```bash
# 重新建置所有面板並打包成 .cskin
/opt/homebrew/bin/python3 scripts/build.py --package
```

打包完成後將 `dist/CatnipGboard.cskin` 傳送到 iPhone，使用「倉輸入法 / 元書輸入法」打開即可套用喵！
