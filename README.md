# sensitive-stop-words

中文敏感词检测词库和测试工具，主要用于在模型输入前做敏感词预检测。

项目提供：

- 本地敏感词词库，按 `.txt` 文件分类维护
- 简洁测试前端，输入整段文本后返回 `True` / `False`
- 命中归因，返回完整审核说明、分类、来源文件和命中词条
- 词库统计脚本
- 词库格式校验脚本
- 外部词库导入脚本，可从 `konsheng/Sensitive-lexicon` 扩充词库

## 功能说明

### 前端检测

启动本地服务后，在浏览器里输入完整文本并点击“检测”。文本框中的所有内容都会作为一整段输入处理，换行不会被拆成多次检测。

输出规则：

- `True`：文本未命中敏感词
- `False`：文本命中敏感词
- `reasons`：命中原因，包含完整审核归因、分类、来源文件、命中词条

命中结果示例：

```json
{
  "ok": false,
  "reasons": [
    {
      "category": "广告",
      "source": "广告.txt",
      "word": "招聘",
      "reason": "输入内容涉及广告推广信息。"
    }
  ],
  "length": 6
}
```

### 词库维护

敏感词统一放在：

```text
data/sensitive_words/
```

新增词库时，只需要新增一个 `.txt` 文件放到这个目录下，检测工具会自动加载。

推荐格式是每行一词：

```text
词条A
词条B
词条C
```

也兼容逗号分隔：

```text
词条A,词条B,词条C
```

## 文件结构

```text
sensitive-stop-words/
├── data/
│   ├── sensitive_words/
│   │   ├── 广告.txt
│   │   ├── 政治类.txt
│   │   ├── 涉枪涉爆违法信息关键词.txt
│   │   ├── 网址.txt
│   │   ├── 色情类.txt
│   │   └── konsheng_*.txt
│   ├── sources/
│   │   ├── konsheng-Sensitive-lexicon.LICENSE
│   │   └── konsheng-Sensitive-lexicon.md
│   └── stopwords/
│       └── stopword.dic
├── scripts/
│   ├── check_text.py
│   ├── import_konsheng_lexicon.py
│   ├── stats.py
│   ├── validate.py
│   └── web_server.py
├── web/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── examples/
│   ├── SensitiveWordFilter.java
│   ├── go_example.go
│   ├── node_example.js
│   └── python_example.py
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

目录说明：

| 路径 | 说明 |
|------|------|
| `data/sensitive_words/` | 敏感词词库目录，检测工具会自动加载这里的 `.txt` 文件 |
| `data/stopwords/` | 停止词目录，主要用于 NLP 分词场景，不参与敏感检测 |
| `data/sources/` | 外部词库来源和许可证说明 |
| `scripts/web_server.py` | 本地测试前端服务 |
| `scripts/check_text.py` | 命令行检测逻辑和可选交互入口 |
| `scripts/import_konsheng_lexicon.py` | 从外部项目导入扩展词库 |
| `scripts/stats.py` | 统计词库数量 |
| `scripts/validate.py` | 校验词库编码、空项、重复词 |
| `web/` | 测试前端页面 |
| `examples/` | Python、Node.js、Java、Go 示例 |

## 环境配置

只需要 Python，不需要安装第三方依赖。

### 1. 进入项目目录

```bash
cd sensitive-stop-words
```

### 2. 确认 Python 可用

```bash
python3 --version
```

建议使用 Python 3.8 或更高版本。

### 3. 启动测试前端

```bash
python3 scripts/web_server.py
```

看到类似输出就说明服务已启动：

```text
检测前端已启动: http://127.0.0.1:8765
已加载词条: 18377
```

然后在浏览器打开：

```text
http://127.0.0.1:8765
```

## 使用方法

### 网页检测

1. 启动服务：

```bash
python3 scripts/web_server.py
```

2. 打开页面：

```text
http://127.0.0.1:8765
```

3. 在文本框里输入或粘贴完整内容。

4. 点击“检测”。

5. 查看右侧结果面板。

如果端口被占用，可以换一个端口：

```bash
python3 scripts/web_server.py --port 8899
```

### API 检测

本地服务同时提供接口：

```text
POST /api/check
```

示例：

```bash
curl -s http://127.0.0.1:8765/api/check \
  -H 'Content-Type: application/json' \
  -d '{"text":"这里有招聘信息","maxReasons":5}'
```

### 命令行检测

仍然可以使用命令行脚本：

```bash
python3 scripts/check_text.py
```

命令行模式支持多行输入，输入 `/check` 后统一检测。

## 添加自己的敏感词

在 `data/sensitive_words/` 下新增文件，例如：

```text
data/sensitive_words/自定义词库.txt
```

内容使用每行一词：

```text
示例词A
示例词B
示例词C
```

保存后重启 `scripts/web_server.py` 即可生效。

## 导入外部扩展词库

项目支持从 `konsheng/Sensitive-lexicon` 的 `Vocabulary/` 目录导入扩展词库。

运行：

```bash
python3 scripts/import_konsheng_lexicon.py
```

脚本会：

- 下载外部 `.txt` 词库
- 去掉空行
- 去掉单文件内重复项
- 写入 `data/sensitive_words/konsheng_*.txt`
- 在 `data/sources/` 保存来源和许可证说明

外部词库来源：

- Vocabulary: <https://github.com/konsheng/Sensitive-lexicon/tree/main/Vocabulary>
- License: <https://github.com/konsheng/Sensitive-lexicon/blob/main/LICENSE>

注意：扩展词库覆盖面更广，但误判也会增加。正式用于模型输入拦截前，建议先观察命中原因，把过于宽泛的词条或词库单独清洗。

## 测试方法

### 1. 校验词库格式

```bash
python3 scripts/validate.py
```

正常情况下会看到：

```text
验证通过。
```

如果输出 `WARN`，通常是重复词或空行；如果输出 `ERROR`，需要先修复。

### 2. 查看词库统计

```bash
python3 scripts/stats.py
```

会输出每个词库文件的词条数量和去重后数量。

### 3. 测试本地 API

先启动服务：

```bash
python3 scripts/web_server.py
```

再请求接口：

```bash
curl -s http://127.0.0.1:8765/api/check \
  -H 'Content-Type: application/json' \
  -d '{"text":"这里有招聘信息","maxReasons":5}'
```

预期返回里包含：

```json
{
  "ok": false
}
```

### 4. 测试前端页面

打开：

```text
http://127.0.0.1:8765
```

输入：

```text
这里有招聘信息
```

点击“检测”，页面应显示 `False`，并展示类似：

```text
输入内容涉及广告推广信息。
```

### 5. 检查 Python 语法

```bash
python3 -m py_compile scripts/check_text.py scripts/stats.py scripts/validate.py scripts/import_konsheng_lexicon.py scripts/web_server.py
```

没有输出就表示语法检查通过。

## 当前词库规模

可以随时运行：

```bash
python3 scripts/stats.py
```

查看最新数量。

## 注意事项

- 这是词库匹配，不是语义审核模型，不能覆盖所有规避写法。
- 词库越大，误判概率越高。
- 上游扩展词库中可能包含泛词，正式拦截前建议先做一轮业务清洗。
- 当前前端用于本地测试，不建议直接暴露到公网。
- 对高并发生产服务，建议在服务启动时加载词库，不要每次请求都重新读文件。

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。

外部导入词库的来源和许可证见 `data/sources/`。
