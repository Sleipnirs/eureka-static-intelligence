# Eureka-Static-Intelligence · 输入格式 v1.1
### 两种输入任选：A. 宽松文本文件（txt/md/docx，推荐商户使用） B. 定式化 JSON（进阶）

> **商户不需要会写 JSON。** 把 FAQ 随手整理成一个文本文件交给编译器即可：
> `python main.py examples/input_myshop.txt`
> 编译器自动识别问答、生成标准 `input_myshop.generated.json`（可检查、可再编辑）、再编译出成品 chatbox。

---

## A. 宽松文本格式（.txt / .md / .docx）

四种问答写法**任选其一**（编译器四种策略并行识别，取产出最多的一种）：

```text
1) 标记式（推荐）      ★问：几点营业？        ← ★ 或 * 开头 = 主线（右栏快捷十问）
                        答：上午11点到晚上10点。
                        （英文用 Q: / A:）
2) Markdown 标题式     ## 几点营业？
                        上午11点到晚上10点。
3) 编号式              1. 几点营业？
                        上午11点到晚上10点。
4) 问号分段式          几点营业？
                        上午11点到晚上10点。   ← 以 ?/？ 结尾的行视为问题，下面的段落是答案
```

文件**开头**可加品牌指令行（全部选填，不写就用文件名+默认值）：

```text
品牌: 蜀香园川菜馆              （或 Brand:）
副标题: 正宗川味·二十年老店     （或 Tagline:）
主色: #E85D2F                   （或 Accent:）
欢迎: 欢迎光临！点下方问题或直接输入。   （或 Welcome:）
按钮: 在线订座 ↗ | https://booking.example.com   （或 Anchor:，格式 文字 | 链接）
语言: zh,en                     （或 Langs:）
```

文件**结尾**可加词汇表段（强烈推荐——命中率的主要杠杆）：

```text
词汇表:
订座|订位|预订 = booking reserve table     ← 竖线 | 分隔同义变体，= 右边是英文对应词
招牌|好吃|必点|推荐 = signature dish       ← 顾客的各种口语说法都写进变体
取消|退订|改期|来不了 = cancel modify
```

规则：`=` 左边是中文变体（编译时自动织入命中节点的关键词），右边是英文词（纯中文包也会织入，供中英桥接）。**变体写得越口语、越全，顾客随口问的命中率越高。**

.docx 直接支持；旧版 .doc 会提示另存为 .docx。识别结果落盘为 `<原名>.generated.json`，不满意可手工修改后按 B 格式再编译。

---

## B. 定式化 JSON（进阶：需要 children/more/流程等精细控制时）

```jsonc
{
  "brand": {
    "name": "Sunny Dental Clinic",          // 必填：品牌名（页头显示）
    "tagline": { "en": "...", "zh": "..." }, // 选填：副标题
    "accent": "#0D9AFF",                     // 选填：主色（默认 Eureka 蓝）
    "langs": ["en", "zh"],                   // 必填：支持语言（1 或 2 个）
    "welcome": { "en": "...", "zh": "..." }, // 必填：欢迎语
    "anchor": {                              // 必填：恒驻锚点chip（FinChip 的 Create a skill 位）
      "label": { "en": "Book now ↗", "zh": "立即预约 ↗" },
      "action": "link",                      // "link" | "faq"
      "target": "https://booking.example.com"
    }
  },

  // ① FAQ 清单（≥30 条起步，100 条效果佳）
  "faq": [
    {
      "id": "opening-hours",                 // 选填：不填自动生成
      "q": { "en": "What are your opening hours?", "zh": "营业时间是什么？" },
      "a": { "en": "...", "zh": "..." },
      "keywords": ["hours", "营业"],        // 选填：不填由编译器自动抽取
      "children": ["book-visit"],           // 选填：不填由编译器按相似度自动连
      "mainline": true,                       // 选填：标记主线（右栏快捷十问）；不标则自动选中心度Top10
      "link": { "href": "...", "label": {"en":"...","zh":"..."} },  // 选填：答案附外链chip
      "more": { "en": "...", "zh": "..." }   // 选填："再详细讲讲"的深层内容
    }
  ],

  // ② 行业词汇表
  "vocab": {
    "synonyms": { "tooth": ["dental", "teeth"], "cost": ["price", "fee"] },  // 用户词→FAQ词
    "zhTerms": [["洗牙", "cleaning scaling"], ["种植牙", "implant"]],          // 中文→英文术语桥
    "smalltalkExtra": ["谢谢医生"]           // 选填：行业寒暄补充（通用700词已内置）
  },

  // ③ 可选流程任务（M2 支持；不填则右栏第二格渲染工具箱）
  "flow": null,

  // 工具箱开关（不填全开；imageGen 为预留插槽）
  "toolbox": ["calculator", "json", "timestamp", "units", "textstats", "aeo"]
}
```

**编译**：`python main.py examples/input_dental.json` → `out/<brand>-chatbox.html`
产物为自包含单文件：任何服务器可托管、任何官网可 iframe，零依赖零构建。
