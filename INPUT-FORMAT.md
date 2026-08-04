# Eureka-Static-Intelligence · 定式化输入格式 v1
### 一份 JSON，三块内容：FAQ 清单 ① + 行业词汇表 ② + 可选流程 ③

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
