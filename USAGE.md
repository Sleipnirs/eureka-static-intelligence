# Eureka-Static-Intelligence · 调度手册（CLI / Claude Code）

> 单文件编译器：把商户 FAQ（宽松文本或标准 JSON）编译成零依赖、可双击运行的静态智能 chatbox（单 HTML）。
> 仓库：https://github.com/Sleipnirs/eureka-static-intelligence

---

## 0. 环境要求

- Python 3.8+（无需 pip install，零第三方依赖）
- Windows 下若 `python` 不可用，用 `py` 替代

## 1. 获取 / 更新

```powershell
git clone https://github.com/Sleipnirs/eureka-static-intelligence.git   # 首次
cd eureka-static-intelligence
git pull                                                                 # 更新
```

## 2. CLI 调度（唯一入口：main.py）

```
python main.py <输入文件>
```

| 输入类型 | 命令示例 | 说明 |
|---|---|---|
| 宽松文本 .txt | `python main.py examples\input_restaurant.txt` | 商户主路径，自动识别问答 |
| Markdown .md | `python main.py 我的店FAQ.md` | 同上 |
| Word .docx | `python main.py 我的店FAQ.docx` | 同上（.doc 会提示另存为 .docx） |
| 标准 JSON | `python main.py examples\input_dental.json` | 进阶路径，精细控制 children/more/flow |

**产物**：
- 宽松文本会先落盘 `<原名>.generated.json`（可检查、可手改后重编译）
- 成品：`out\<品牌名>-chatbox.html`（约 50–60 KB，单文件零依赖）
- stdout 尾部输出 JSON 状态：`nodes` / `quick` / `size_kb` / `warnings`（色值兜底等提示在此）

**两步走工作流**（推荐给需要质检的场景）：

```powershell
python main.py 我的店FAQ.txt              # 第1步: 识别 → 我的店FAQ.generated.json + 成品
notepad 我的店FAQ.generated.json          # 第2步: 人工检查/修改
python main.py 我的店FAQ.generated.json   # 第3步: 用修改版重编译
```

**打开成品**：

```powershell
ii out\蜀香园川菜馆-chatbox.html    # 默认浏览器打开
```

## 3. 输入文件怎么写

详见 `INPUT-FORMAT.md`。速记版：

- 问答四种写法任选：`★问：/答：`（★=主线，进右栏快捷十问）、`## 标题`、`1. 编号`、问号分段
- 文件头选填品牌指令：`品牌:` `副标题:` `主色:` `欢迎:` `按钮: 文字 | 链接` `语言: zh,en`
- 文件尾强烈建议写 `词汇表:` 段：`订座|订位|预订 = booking reserve table`——竖线变体是命中率的主要杠杆
- 主色鲁棒：`#E85D2F` / `E85D2F` / `#e85` / `红色` / `orange` / `rgb(...)` 均可，认不出兜底 Eureka 蓝并出 warning

## 4. Claude Code 调度约定

在 Claude Code 中操作本仓库时，遵循以下约定：

**触发**：用户给出一个 FAQ 文件（或要求"生成 chatbox / 静态智能客服"）→ 运行 `python main.py <文件>`，把 stdout 的 JSON 状态和 warnings 转述给用户。

**质检**（改动引擎/模板后必做）：
1. `python main.py examples\input_restaurant.txt` 和 `python main.py examples\input_dental.json` 都必须编译通过
2. 回归口径：餐饮 15 条口语改述探针 + 牙科 16 条中英探针 + 寒暄 8 条 + 防复读 + 算式（探针清单见 examples\example_run.md）
3. 引擎测试方法：从成品 HTML 抽出 `/* ENGINE_START */ … /* ENGINE_END */` 段与 `esi-pack` JSON，拼成 node 可 require 的测试桩，直接调 `score()/isSmallTalk()/evalExpr()` 断言

**改动分区**（先读后写）：
- `main.py` = 编译器（摄入层 parse_loose/ingest、词汇表反向织入、norm_accent、自动 keywords/children/quick-10）
- `template\chatbox.template.html` = 成品骨架 + 引擎（五层匹配、SMALLTALK、FILLER、CJK 单字层）
- `template\ui.js` = 成品界面（banner/composer/chip/AEO 卡）
- 引擎与 UI 严格继承 FinChip Generator 的行为与视觉；**不得在任何用户可见文本中提及"无 LLM/规则引擎"等实现机密**

**红线**：不引入运行时遥测/数据回传——静态智能哲学：智能升级只发生在设计对话中，成果冻结发布。

## 5. 交付给商户的三种玩法

1. 双击本地用（培训/内部 FAQ）
2. 静态托管变在线客服页：Vercel / GitHub Pages / OSS，拖上去即可
3. `<iframe src=".../xxx-chatbox.html">` 嵌入商户现有官网

## 6. 常见报错

| 报错 | 处理 |
|---|---|
| `Legacy .doc is a binary format...` | 另存为 .docx 或 .txt 再跑 |
| `no Q&A pairs found` | 检查四种问答写法是否至少成立一种 |
| `python: command not found` | 用 `py main.py ...` |
| warnings 里出现 accent 兜底提示 | 主色没写对，按第 3 节格式改 |
