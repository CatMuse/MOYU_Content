#!/usr/bin/env python3
"""Publish a local scene pack into this checkout and sign the catalog. Never uploads keys."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--pack', required=True, type=Path)
p.add_argument('--prepare-only', action='store_true', help='Copy pack and review documents without changing the signed catalog')
p.add_argument('--review-dir', required=True, type=Path)
p.add_argument('--signing-key', type=Path, default=root.parent / 'MOYU_Extras/local/content-signing.pem')
a = p.parse_args()
openssl = os.environ.get('MOYU_OPENSSL', '/opt/homebrew/opt/openssl@3/bin/openssl')
raw = a.pack.read_bytes()
pack = json.loads(raw)
assert pack['sceneCourse'] is True and pack['kind'] == 'vocabulary'
assert len(raw) <= 32_000_000
import re
assert re.fullmatch(r'[a-z0-9][a-z0-9-]*', pack['id'])
assert re.fullmatch(r'\d+\.\d+\.\d+', pack['version'])
decks = pack['decks']
assert len({d['id'] for d in decks}) == len(decks)
assert all(10 <= len(d['words']) <= 20 and d['section'] for d in decks)
review = json.loads((a.review_dir / f"course-catalog-{pack['version']}.json").read_bytes())
assert (review['id'], review['version'], review['pictures'], review['occurrences']) == (pack['id'], pack['version'], len(decks), sum(len(d['words']) for d in decks))
if not a.prepare_only:
    if not a.signing_key.is_file():
        p.error('Original signing key is missing; use --prepare-only to stage files without changing the catalog')
    public = subprocess.check_output([openssl, 'pkey', '-in', str(a.signing_key), '-pubout'])
    assert public == (root / 'catalog-public-key.pem').read_bytes(), 'Signing key differs from trusted public key'
envelope = json.loads((root / 'catalog.json').read_bytes())
old_payload = (root / 'catalog.payload.json').read_bytes()
assert base64.b64decode(envelope['payload'], validate=True) == old_payload
catalog = json.loads(old_payload)
filename = f"{pack['id']}-{pack['version']}.moyupack.json"
target = root / 'packs' / filename
assert not target.exists() or target.read_bytes() == raw, 'Published versions are immutable'
entry = {k: pack[k] for k in ['id', 'name', 'version', 'minimumAppVersion', 'kind', 'author', 'source', 'license', 'summary']}
entry.update(url=f'packs/{filename}', sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), lessonCount=len(decks), itemCount=sum(len(d['words']) for d in decks))
previous = next((e for e in catalog['packages'] if e['id'] == pack['id']), None)
if previous:
    assert tuple(map(int, pack['version'].split('.'))) >= tuple(map(int, previous['version'].split('.'))), 'Version rollback'
    if previous['version'] == pack['version']:
        assert previous == entry, 'Published version metadata is immutable'
    catalog['packages'] = [entry if e['id'] == pack['id'] else e for e in catalog['packages']]
else:
    catalog['packages'].append(entry)
payload = (json.dumps(catalog, ensure_ascii=False, indent=2) + '\n').encode()
with tempfile.TemporaryDirectory(prefix='moyu-content-sign-') as directory:
    temp = Path(directory)
    old = temp / 'old.json'; old.write_bytes(old_payload)
    sig = temp / 'signature'; sig.write_bytes(base64.b64decode(envelope['signature'], validate=True))
    subprocess.run([openssl, 'pkeyutl', '-verify', '-pubin', '-inkey', str(root / 'catalog-public-key.pem'), '-rawin', '-in', str(old), '-sigfile', str(sig)], check=True, capture_output=True)
    if not a.prepare_only:
        new = temp / 'new.json'; new.write_bytes(payload)
        signature = subprocess.check_output([openssl, 'pkeyutl', '-sign', '-rawin', '-inkey', str(a.signing_key), '-in', str(new)])
        sig.write_bytes(signature)
        subprocess.run([openssl, 'pkeyutl', '-verify', '-pubin', '-inkey', str(root / 'catalog-public-key.pem'), '-rawin', '-in', str(new), '-sigfile', str(sig)], check=True, capture_output=True)
# All checks and optional signing complete before updating the checkout.
target.write_bytes(raw)
if not a.prepare_only:
    (root / 'catalog.payload.json').write_bytes(payload)
    (root / 'catalog.json').write_text(json.dumps(dict(payload=base64.b64encode(payload).decode(), signature=base64.b64encode(signature).decode())) + '\n')
docs = root / 'courses' / pack['id']; docs.mkdir(parents=True, exist_ok=True)
(docs / 'course-catalog.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
(docs / 'words-review.tsv').write_bytes((a.review_dir / f"words-review-{pack['version']}.tsv").read_bytes())
scenes = list(dict.fromkeys(d['section'] for d in decks))
installation = ('当前已上传可导入包，尚未加入客户端在线目录。请下载上方文件，在客户端「内容 → 管理内容 → 导入本地内容」导入。原签名私钥恢复后，再将本包加入在线目录。' if a.prepare_only else '在客户端「内容 → 管理内容」下载或检查更新；也可通过「导入本地内容」选择上方文件。')
rows = '\n'.join(f"| {s} | {sum(d['section'] == s for d in decks)} | {sum(len(d['words']) for d in decks if d['section'] == s)} |" for s in scenes)
(docs / 'README.md').write_text(f'''# {pack['name']} v{pack['version']}

面向初中／高中学习者，采用美式英语。{len(scenes)} 个场景、{len(decks)} 张 16:9 场景图、{entry['itemCount']} 次词汇练习、{review['uniqueWords']} 个去重词。每图 10～20 词，底图不含教学标签和箭头，由支持场景课程的 MOYU 客户端绘制英文。

| 场景 | 图片 | 词汇出现次数 |
| --- | ---: | ---: |
{rows}

[下载导入包](../../packs/{filename}) · [图片目录](course-catalog.json) · [词表与坐标](words-review.tsv)

{installation}包 ID 为 `{pack['id']}`，更新保持旧图片与词条 ID，沿用已有学习记录，无需先删除旧包。

## 来源与使用范围

作者：{pack['author']}。插画由内置 image_gen 为 MOYU 生成，包含一次试衣图软尺数字移除编辑；未使用第三方成品插画、录音或例句。词表、坐标与场景例句为 MOYU 编排。原图、提示词、编辑记录、设计和构建脚本保留在制作项目 `MOYU_CrossPlatform/examples/city-life-scenes/`；此分发目录仅保存最新版本的使用说明、图片目录与校对表，不重复上传历史样板和高清制作稿。

许可沿用包内声明：{pack['license']} 仓库公开可见不授予额外再分发或其他用途的授权。

## 检查范围

已完成格式、素材哈希、24 图静态标签几何、可重复构建及旧版数据兼容性检查。逐图视觉和真实发音由维护者人工验收，未宣称已完成全部逐图运行验收。

文件：{entry['bytes']:,} 字节；SHA-256：`{entry['sha256']}`。
''')
print(f"Prepared {pack['id']} v{pack['version']}: {len(decks)} pictures, {entry['itemCount']} occurrences, {len(raw)} bytes; catalog " + ("unchanged (prepare only)." if a.prepare_only else "signed.") + " No private key copied.")
