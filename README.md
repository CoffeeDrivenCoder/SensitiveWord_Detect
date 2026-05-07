# SensitiveWord_Detect

一个本地敏感词检测小工具。启动后会打开一个简单网页，在文本框里输入或粘贴内容，点击“检测”即可看到 `True` / `False` 和命中原因。

## 环境要求

只需要 Python，不需要安装第三方依赖。

建议使用 Python 3.8 或更高版本。

确认 Python 可用：

```bash
python3 --version
```

## 启动前端

进入项目目录：

```bash
cd SensitiveWord_Detect
```

启动服务：

```bash
python3 scripts/web_server.py
```

看到类似输出说明启动成功：

```text
检测前端已启动: http://127.0.0.1:8765
已加载词条: 18377
```

然后打开浏览器访问：

```text
http://127.0.0.1:8765
```

## 怎么使用

1. 在左侧文本框输入或粘贴完整内容。
2. 点击“检测”。
3. 右侧会显示结果。

结果说明：

- `True`：没有命中敏感词
- `False`：命中敏感词
- 命中时会显示原因，例如：`输入内容涉及广告推广信息。`

多行文本会作为一整段内容检测，不会按行拆开。

## 换端口启动

如果 `8765` 端口被占用，可以换一个端口：

```bash
python3 scripts/web_server.py --port 8899
```

然后访问：

```text
http://127.0.0.1:8899
```

## 添加敏感词

敏感词文件放在：

```text
data/sensitive_words/
```

新增一个 `.txt` 文件即可，例如：

```text
data/sensitive_words/自定义词库.txt
```

推荐每行一个词：

```text
示例词A
示例词B
示例词C
```

保存后重启服务生效。

## 常用测试命令

校验词库：

```bash
python3 scripts/validate.py
```

统计词库：

```bash
python3 scripts/stats.py
```

测试接口：

```bash
curl -s http://127.0.0.1:8765/api/check \
  -H 'Content-Type: application/json' \
  -d '{"text":"这里有招聘信息","maxReasons":5}'
```

检查 Python 语法：

```bash
python3 -m py_compile scripts/check_text.py scripts/stats.py scripts/validate.py scripts/import_konsheng_lexicon.py scripts/web_server.py
```

## 项目结构

```text
data/sensitive_words/   敏感词词库
data/stopwords/         停止词
scripts/web_server.py   本地前端服务
scripts/check_text.py   检测逻辑
web/                    前端页面
```

## 注意

这个工具用于本地测试和模型输入预检，不建议直接暴露到公网。
