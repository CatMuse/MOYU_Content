# MOYU Content

MOYU 官方内容目录与下载资源。客户端从此仓库加载经过 Ed25519 签名的目录，核对下载包的 SHA-256、大小和版本后安装；已下载内容可离线使用。

## 当前内容

| 内容 | 版本 | 数量 | 分发方式 |
| --- | --- | --- | --- |
| 把话说完整 | 1.0.1 | 160 课 / 7,823 条练习 | `packs/` 中的 JSON |
| 词光雅思 | 1.0.0 | 7,298 个词条与插图 / 22,905 段录音 | [Release 附件](https://github.com/CatMuse/MOYU_Content/releases/tag/content-v1.0.0)，约 585 MB |

其他历史词库和第三方课程暂未纳入公开目录，待确认公开分发许可后再发布。已有本地下载不会被删除。

## 自己制作内容

复制 [单词模板](examples/my-words.moyupack.json) 或 [句子课程模板](examples/my-course.moyupack.json)，按 [格式说明](FORMAT.md) 编辑，在客户端「内容 → 添加内容 → 本地加载」中导入。更新时增加版本号，保持已有包、课及练习的 ID 稳定。移除下载不会清除学习记录。

客户端只连接此官方仓库，不提供切换到其他仓库的设置；本地导入独立可用。内容包仅包含数据，不执行代码。

## 许可与来源

每个内容包保留自己的作者、来源及许可；仓库公开可见不代表其中所有内容采用相同许可。

- 「把话说完整」为 MOYU 原创课程，Copyright (c) CatMuse，保留所有权利，提供给 MOYU 用户个人学习使用。
- 词光雅思源自 [designfuchen/word-atlas](https://github.com/designfuchen/word-atlas)，固定上游提交 `99c007673d38f02c418d8e4cd2e9ec90b5d40be5`。内容按 **CC BY 4.0** 分发，详见 [原始内容许可](licenses/word-atlas-CONTENT_LICENSE.md) 与 [署名和改动说明](licenses/word-atlas-ATTRIBUTION.txt)。MOYU 仅提取必要词条及媒体，增加安装清单并重新打包，未包含上游网站程序代码。上游内容由 AI 生成，未逐条人工审校。
- `examples/` 为制作格式示例，可复制修改以创建个人内容包。

## 目录与完整性

- `catalog.json`：客户端读取的签名信封，包含 Base64 编码的原始目录和签名。
- `catalog.payload.json`：便于代码审查的明文目录，与信封中的字节完全一致。
- `catalog-public-key.pem`：仅用于验证的公开密钥；私钥不在此仓库。
- `packs/`：不可变版本的普通内容包。词光大型 ZIP 作为 Release 附件，避免进入 Git 历史。

内容更新先发布新版本文件，再更新并签名目录。已发布版本不可替换成不同字节。客户端会先验证目录签名，再验证包的哈希、格式和身份，验证或安装失败不会替换原有内容。
