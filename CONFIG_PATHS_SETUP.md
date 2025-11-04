# 配置路径说明

## 📁 配置项

在 `config.py` 中定义了以下与 Word 文档生成相关的路径配置：

```python
class Config:
    # Word 模板文件存放目录
    UPLOAD_FOLDER_TEMPLATE = os.path.join(basedir, 'app/static/templates')
    
    # 生成的授权书文档存放目录
    UPLOAD_FOLDER_SHOUQUAN = os.path.join(basedir, 'app/static/generated_docs')
```

## 🔧 使用方式

### 1. 在 word_generator.py 中的应用

`WordGenerator` 类会自动从配置中读取路径：

```python
from app.utils.word_generator import generate_word_document

# 自动使用配置中的路径
success, result = generate_word_document(record)

# 也可以手动指定路径（会覆盖配置）
success, result = generate_word_document(record, output_dir='/custom/path')
```

### 2. 路径解析优先级

1. **显式传入的路径** - 最高优先级
2. **配置文件中的路径** - 通过 `current_app.config` 获取
3. **默认路径** - 如果配置不存在或不在应用上下文中

### 3. 自动目录创建

系统会自动创建配置中指定的目录：

```python
# 在 word_generator.py 中
os.makedirs(os.path.dirname(output_path), exist_ok=True)
```

## 📂 目录结构

```
auth_system/
├── config.py                          # 配置文件
├── app/
│   ├── static/
│   │   ├── templates/                 # ← UPLOAD_FOLDER_TEMPLATE
│   │   │   ├── 标准授权模板.docx
│   │   │   ├── 高级授权模板.docx
│   │   │   └── ...
│   │   └── generated_docs/            # ← UPLOAD_FOLDER_SHOUQUAN
│   │       ├── 授权字号_店铺名称_时间戳.docx
│   │       └── ...
│   ├── utils/
│   │   └── word_generator.py          # 使用配置路径
│   └── routes/
│       └── upload_generated.py        # 使用配置路径
```

## 🎯 配置的优点

### ✅ 集中管理
- 所有路径配置统一在 `config.py` 中
- 便于维护和修改
- 避免硬编码

### ✅ 环境适配
- 开发环境和生产环境可以使用不同的路径
- 通过环境变量灵活配置

### ✅ 安全性
- 配置路径使用 `os.path.join()` 自动适配操作系统
- 支持绝对路径和相对路径

## 🔄 修改配置路径

如果需要修改路径，只需在 `config.py` 中修改：

```python
class Config:
    # 修改模板目录
    UPLOAD_FOLDER_TEMPLATE = '/path/to/custom/templates'
    
    # 修改输出目录
    UPLOAD_FOLDER_SHOUQUAN = '/path/to/custom/output'
```

## 🌍 环境变量支持

可以通过环境变量覆盖配置：

```python
# config.py
class Config:
    UPLOAD_FOLDER_TEMPLATE = os.environ.get('TEMPLATE_DIR') or \
                            os.path.join(basedir, 'app/static/templates')
    
    UPLOAD_FOLDER_SHOUQUAN = os.environ.get('OUTPUT_DIR') or \
                            os.path.join(basedir, 'app/static/generated_docs')
```

然后在 `.env` 文件中设置：

```bash
TEMPLATE_DIR=/custom/templates
OUTPUT_DIR=/custom/output
```

## 📝 代码示例

### 使用配置路径

```python
from flask import current_app
from app.utils.word_generator import WordGenerator
from app.models.generated import Generated

# 在 Flask 应用上下文中
record = Generated.query.get(1)

# 方式 1: 使用便捷函数（自动使用配置）
from app.utils.word_generator import generate_word_document
success, result = generate_word_document(record)

# 方式 2: 使用类（自动使用配置）
generator = WordGenerator()
success, result = generator.generate_from_model(record)

# 方式 3: 手动获取配置
template_dir = current_app.config['UPLOAD_FOLDER_TEMPLATE']
output_dir = current_app.config['UPLOAD_FOLDER_SHOUQUAN']
generator = WordGenerator(template_dir=template_dir)
success, result = generator.generate_from_model(record, output_dir=output_dir)
```

### 批量生成

```python
from app.utils.word_generator import batch_generate_word_documents
from app.models.generated import Generated

# 查询多条记录
records = Generated.query.limit(10).all()

# 批量生成（自动使用配置路径）
results = batch_generate_word_documents(records)

print(f"成功: {results['success']}")
print(f"失败: {results['failed']}")
```

## ⚙️ 初始化设置

创建必要的目录：

```python
# 运行一次即可
import os
from config import Config

config = Config()

# 创建模板目录
os.makedirs(config.UPLOAD_FOLDER_TEMPLATE, exist_ok=True)
print(f"✅ 已创建模板目录: {config.UPLOAD_FOLDER_TEMPLATE}")

# 创建输出目录
os.makedirs(config.UPLOAD_FOLDER_SHOUQUAN, exist_ok=True)
print(f"✅ 已创建输出目录: {config.UPLOAD_FOLDER_SHOUQUAN}")
```

或者在应用初始化时自动创建：

```python
# app/__init__.py
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 创建必要的目录
    os.makedirs(app.config['UPLOAD_FOLDER_TEMPLATE'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_SHOUQUAN'], exist_ok=True)
    
    # ... 其他初始化代码
    
    return app
```

## 🔍 路径验证

验证配置路径是否正确：

```python
from flask import current_app

def verify_paths():
    """验证配置路径"""
    template_dir = current_app.config.get('UPLOAD_FOLDER_TEMPLATE')
    output_dir = current_app.config.get('UPLOAD_FOLDER_SHOUQUAN')
    
    print(f"模板目录: {template_dir}")
    print(f"  存在: {os.path.exists(template_dir)}")
    print(f"  可写: {os.access(template_dir, os.W_OK)}")
    
    print(f"\n输出目录: {output_dir}")
    print(f"  存在: {os.path.exists(output_dir)}")
    print(f"  可写: {os.access(output_dir, os.W_OK)}")
```

## 📌 注意事项

1. **路径权限**：确保应用对配置路径有读写权限
2. **路径存在性**：系统会自动创建不存在的输出目录
3. **相对路径**：相对路径基于项目根目录（`basedir`）
4. **Windows 路径**：使用 `os.path.join()` 自动处理路径分隔符

---

**最后更新时间：** 2025-03-16
**配置版本：** 2.0

