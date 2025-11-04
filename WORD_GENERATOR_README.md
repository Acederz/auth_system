# Word 文档自动生成功能说明

## 📋 功能概述

该功能可以根据数据库中的 `Generated` 模型数据，自动填充 Word 模板文档并生成授权书。

## 🗂️ 目录结构

```
auth_system/
├── app/
│   ├── static/
│   │   ├── templates/          # Word 模板文件存放目录（需手动创建）
│   │   │   ├── 模板A.docx
│   │   │   ├── 模板B.docx
│   │   │   └── ...
│   │   └── generated_docs/     # 生成的文档存放目录（自动创建）
│   │       ├── 授权字号_店铺名称_时间戳.docx
│   │       └── ...
│   ├── utils/
│   │   └── word_generator.py   # Word 文档生成工具
│   ├── routes/
│   │   └── upload_generated.py # 路由和 API
│   └── models/
│       └── generated.py        # 数据模型
└── requirements.txt            # python-docx 已包含
```

## 🔧 安装依赖

系统已包含所需依赖 `python-docx`，如果需要重新安装：

```bash
pip install python-docx
```

## 📄 Word 模板文件准备

### 1. 创建模板目录

```bash
mkdir -p app/static/templates
mkdir -p app/static/generated_docs
```

### 2. 模板文件命名

模板文件名必须与 `Generated` 模型中的 `template_used` 字段值完全一致。

例如：
- 如果 `template_used` = "标准授权模板"
- 则模板文件应命名为：`标准授权模板.docx`

### 3. 模板中的占位符

在 Word 模板中使用 `《》` 包裹的占位符，系统会自动替换为对应的数据值：

| 占位符 | 对应字段 | 说明 |
|--------|----------|------|
| `《使用模板》` | template_used | 使用的模板名称 |
| `《店铺类型》` | store_type | 店铺类型 |
| `《授权主体》` | authorized_entity | 授权主体 |
| `《授权平台》` | platform | 授权平台 |
| `《授权品牌》` | brand | 授权品牌 |
| `《品牌商标号》` | trademark_no | 品牌商标号 |
| `《店铺名称》` | store_name | 店铺名称 |
| `《授权期间》` | period | 授权期间 |
| `《授权字号》` | auth_number | 授权字号 |
| `《授权方主体》` | stamping_entity | 授权方（盖章）主体 |
| `《用印时间》` | stamping_date | 用印时间 |

### 4. 模板示例

```
                    授权书

兹授权《授权主体》在《授权平台》平台开设《店铺类型》店铺。

店铺名称：《店铺名称》
授权品牌：《授权品牌》
品牌商标号：《品牌商标号》
授权期间：《授权期间》
授权字号：《授权字号》

授权方（盖章）：《授权方主体》
用印时间：《用印时间》
```

## 🚀 使用方法

### 方式一：通过页面操作

1. 访问 `/upload-generated/list` 查看数据列表
2. 点击每行的 **"生成"** 按钮，生成单个文档
3. 或勾选多个数据，点击 **"批量生成文档"** 按钮
4. 生成成功后会自动下载文档

### 方式二：通过 API 调用

#### 生成单个文档

```python
POST /upload-generated/api/generate/<id>

返回：
{
    "success": true,
    "message": "文档生成成功",
    "file_path": "static/generated_docs/授权字号_店铺名称_时间戳.docx",
    "filename": "授权字号_店铺名称_时间戳.docx"
}
```

#### 批量生成文档

```python
POST /upload-generated/api/generate-batch
Content-Type: application/json

{
    "ids": [1, 2, 3, 4, 5]
}

返回：
{
    "success": true,
    "message": "成功生成 5 个文档，失败 0 个",
    "results": {
        "success": 5,
        "failed": 0,
        "files": ["文件路径1.docx", "文件路径2.docx", ...],
        "errors": []
    }
}
```

#### 下载生成的文档

```
GET /upload-generated/download/<filename>
```

### 方式三：在 Python 代码中使用

```python
from app.models.generated import Generated
from app.utils.word_generator import generate_word_document, batch_generate_word_documents

# 生成单个文档
record = Generated.query.get(1)
success, result = generate_word_document(record)

if success:
    print(f"文档生成成功：{result}")
else:
    print(f"生成失败：{result}")

# 批量生成
records = Generated.query.limit(10).all()
results = batch_generate_word_documents(records)
print(f"成功：{results['success']}，失败：{results['failed']}")
```

## 📝 生成文件命名规则

生成的文件名格式：`授权字号_店铺名称_时间戳.docx`

例如：`SH20240115001_旗舰店_20250316143052.docx`

- 如果授权字号或店铺名称为空，会跳过该部分
- 时间戳格式：`YYYYMMDDHHmmss`
- 文件名中的非法字符会被自动替换为下划线

## ⚠️ 注意事项

1. **模板文件位置**：必须放在 `app/static/templates/` 目录下
2. **模板文件格式**：支持 `.docx` 格式（不支持旧版 `.doc`）
3. **占位符格式**：必须使用中文书名号 `《》` 包裹
4. **字段匹配**：占位符名称必须与表格中定义的完全一致
5. **文件权限**：确保程序对 `app/static/generated_docs/` 目录有写权限
6. **模板不存在**：如果找不到对应的模板文件，会返回错误信息

## 🔍 常见问题

### Q1: 提示"未找到模板文件"？

**A:** 检查以下几点：
1. 模板文件是否放在 `app/static/templates/` 目录
2. 文件名是否与 `template_used` 字段值完全一致（包括大小写）
3. 文件扩展名是否为 `.docx`

### Q2: 生成的文档中占位符没有被替换？

**A:** 检查以下几点：
1. 占位符是否使用中文书名号 `《》`
2. 占位符名称是否与表格中的完全一致
3. Word 模板中的占位符是否被拆分成多个 run（可以尝试重新输入占位符）

### Q3: 生成文档时提示权限错误？

**A:** 确保以下目录有写权限：
```bash
chmod 755 app/static/generated_docs/
```

### Q4: 如何自定义字段映射？

**A:** 编辑 `app/utils/word_generator.py` 中的 `field_mapping` 字典：

```python
self.field_mapping = {
    'model_field_name': '《Word中的占位符》',
    # 添加或修改映射关系
}
```

## 🛠️ 高级功能

### 自定义输出目录

```python
from app.utils.word_generator import WordGenerator

generator = WordGenerator(template_dir='自定义模板目录')
success, result = generator.generate_from_model(
    record, 
    output_dir='自定义输出目录'
)
```

### 保留格式替换

系统会自动保留 Word 文档中的原有格式（字体、颜色、对齐方式等），只替换文本内容。

### 支持表格和页眉页脚

系统支持替换以下位置的占位符：
- 正文段落
- 表格单元格
- 页眉
- 页脚

## 📞 技术支持

如有问题，请联系系统管理员或查看源代码注释。

---

**最后更新时间：** 2025-03-16
**版本：** 1.0.0

