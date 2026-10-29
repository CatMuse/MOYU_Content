# 本地内容包制作

在 MOYU「内容 → 添加内容 → 本地加载」中选择 JSON。加载后自动选中内容。模板见 [examples](examples/)。

## 内容包格式（schemaVersion 1）

```json
{
  "schemaVersion": 1,
  "id": "my-course",
  "name": "我的句子课程",
  "version": "1.0.0",
  "minimumAppVersion": "0.1.0",
  "kind": "sentences",
  "author": "你的名字",
  "source": "原创",
  "license": "仅供个人使用",
  "summary": "练习日常表达",
  "decks": [
    {
      "id": "my-course-lesson-01",
      "name": "第一课 · 打招呼",
      "section": "第一单元",
      "shortName": "打招呼",
      "learningGoal": "介绍自己并回应问候。",
      "grammarFocus": "I am / I'm",
      "grammarNote": "I'm 是 I am 的缩写。",
      "words": [
        {"id": "greeting-001", "word": "Nice to meet you.", "meaning": "很高兴认识你。"}
      ]
    }
  ]
}
```

- `kind` 为 `vocabulary`（单词词库）或 `sentences`（句子课程）。词库必须只有一个 deck；课程可以有多个 deck。
- 包与 deck 的 `id` 只能使用英文字母、数字、短横线及下划线，最多 120 个字符；不使用 `custom`、`test`、`empty`、`word-atlas-ielts`。
- 包 ID 在内容库中唯一；不同包的 deck ID 不得重复；同一 deck 内的练习 ID 不得重复。建议全部使用自己的前缀。
- 每条练习必填 `id`、`word`、`meaning`，可选 `phonetic`、`partOfSpeech`、`definition`、`example`，均为字符串。
- deck 的 `section`、`shortName`、`learningGoal`、`grammarFocus`、`grammarNote` 为可选字段。
- `version`、`minimumAppVersion` 使用 `数字.数字.数字`；可选 `order`（整数）控制已安装内容的显示顺序。
- 单包不超过 32 MB；最多 1,000 个 deck，每个 deck 最多 50,000 条练习。
- 仅支持数据，不执行脚本或加载插件代码。

## 更新与进度

修正文字时保留原有 ID；新增练习使用新 ID。更新增加版本号，同版本不同内容会被拒绝，不能用旧版覆盖新版。更新不能改变包的类型。

句子课程更新会对照旧的已完成练习 ID 计算新版中连续完成的位置。中间新增的练习会成为新的起点，避免直接跳过未学内容；复杂重排可能需要重新练习部分旧条目。已有词库学习记录和收藏继续使用 deck/word ID。

移除下载不会清除学习记录。重新加载同一包可以恢复进度。应用更新内容时会收起练习窗口，避免正在输入的内容被替换。

