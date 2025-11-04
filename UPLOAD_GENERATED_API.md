# 授权书生成系统 - API接口文档

> **模块：** `app/routes/upload_generated.py`  
> **功能：** 授权书数据管理和文档生成  
> **更新时间：** 2025-01-21

---

## 📑 目录

- [概述](#概述)
- [页面路由](#页面路由)
- [API接口](#api接口)
  - [数据查询](#数据查询)
  - [数据操作](#数据操作)
  - [Word文档生成](#word文档生成)
  - [PDF文档生成](#pdf文档生成)
  - [Excel导入](#excel导入)
- [数据模型](#数据模型)
- [权限说明](#权限说明)

---

## 概述

本模块提供授权书数据的完整生命周期管理：

- **数据导入**：从Excel批量导入授权书数据（支持日期格式自动转换）
- **数据管理**：查询、筛选、编辑、删除授权书记录（支持CRUD完整操作）
- **文档生成**：根据模板生成Word/PDF格式的授权书文档（支持单个和批量生成）
- **智能下载**：批量下载文档（ZIP打包，**自动生成缺失文件**，无需手动预生成）

### 技术栈

- **后端框架**：Flask
- **数据库ORM**：SQLAlchemy
- **Excel处理**：openpyxl
- **Word处理**：python-docx
- **PDF转换**：docx2pdf (需要Microsoft Word)

---

## 页面路由

### 1. 功能菜单页面

**路由：** `GET /upload-generated/menu`  
**权限：** `@generate_admin_required`  
**功能：** 展示功能菜单，提供数据导入和列表查看的入口  
**模板：** `app/templates/uploadGeneratedFiles/menu.html`

**访问方式：**
- 直接访问URL：`/upload-generated/menu`
- 从导航栏点击"功能菜单"

---

### 2. 数据导入页面

**路由：** `GET /upload-generated/import`  
**权限：** `@generate_admin_required`  
**功能：** 提供Excel文件上传和数据预览功能，支持批量导入授权书数据  
**模板：** `app/templates/uploadGeneratedFiles/upload.html`

**访问方式：**
- 直接访问URL：`/upload-generated/import`
- 从导航栏点击"数据导入"
- 从menu.html点击"Excel数据导入"卡片

---

### 3. 数据列表页面

**路由：** `GET /upload-generated/list`  
**权限：** `@generated_required`  
**功能：** 展示所有已导入的授权书数据，支持筛选、分页、编辑、删除、生成文档等操作  
**模板：** `app/templates/uploadGeneratedFiles/list.html`

**访问方式：**
- 直接访问URL：`/upload-generated/list`
- 从导航栏点击"数据列表"
- 从menu.html点击"数据列表查看"卡片

---

## API接口

### 数据查询

#### 1. 获取数据列表

**路由：** `GET /upload-generated/api/list`  
**权限：** `@generated_required`  
**功能：** 获取授权书数据列表，支持分页、筛选和模糊搜索

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 | 默认值 |
|--------|------|------|------|--------|
| page | int | 否 | 页码 | 1 |
| page_size | int | 否 | 每页条数 | 10 |
| template_used | string | 否 | 使用模板（模糊搜索） | - |
| store_type | string | 否 | 店铺类型（模糊搜索） | - |
| authorized_entity | string | 否 | 授权主体（模糊搜索） | - |
| platform | string | 否 | 授权平台（模糊搜索） | - |
| brand | string | 否 | 授权品牌（模糊搜索） | - |
| store_name | string | 否 | 店铺名称（模糊搜索） | - |
| auth_number | string | 否 | 授权字号（模糊搜索） | - |
| stamping_entity | string | 否 | 授权方主体（模糊搜索） | - |

**返回数据：**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "template_used": "模板A",
      "store_type": "旗舰店",
      "authorized_entity": "公司A",
      "platform": "天猫",
      "brand": "品牌A",
      "trademark_no": "12345678",
      "store_name": "测试旗舰店",
      "period": "2024-01-01至2024-12-31",
      "auth_number": "AUTH-001",
      "stamping_entity": "公司B",
      "stamping_date": "2024-01-01",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `loadData()` 函数

---

#### 2. 获取筛选选项

**路由：** `GET /upload-generated/api/filters`  
**权限：** `@generated_required`  
**功能：** 获取所有字段的唯一值列表，用于填充筛选下拉框

**返回数据：**

```json
{
  "success": true,
  "filters": {
    "templates": ["模板A", "模板B"],
    "store_types": ["旗舰店", "专卖店"],
    "entities": ["公司A", "公司B"],
    "platforms": ["天猫", "京东"],
    "brands": ["品牌A", "品牌B"],
    "stamping_entities": ["公司A", "公司B"]
  }
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `loadFilters()` 函数（页面初始化时调用）

---

#### 3. 获取单条记录

**路由：** `GET /upload-generated/api/record/<id>`  
**权限：** `@generated_required`  
**功能：** 根据记录ID获取完整的记录信息，用于编辑功能的数据回填

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | int | 记录ID |

**返回数据：**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "template_used": "模板A",
    "store_type": "旗舰店",
    "authorized_entity": "公司A",
    "platform": "天猫",
    "brand": "品牌A",
    "trademark_no": "12345678",
    "store_name": "测试旗舰店",
    "period": "2024-01-01至2024-12-31",
    "auth_number": "AUTH-001",
    "stamping_entity": "公司B",
    "stamping_date": "2024-01-01"
  }
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `openEditModal(id)` 函数（点击编辑按钮时）

---

### 数据操作

#### 4. 更新记录

**路由：** `PUT /upload-generated/api/record/<id>`  
**权限：** `@generate_admin_required`  
**功能：** 根据记录ID更新记录的所有字段

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | int | 记录ID |

**请求体（JSON）：**

```json
{
  "template_used": "模板A",
  "store_type": "旗舰店",
  "authorized_entity": "公司A",
  "platform": "天猫",
  "brand": "品牌A",
  "trademark_no": "12345678",
  "store_name": "测试旗舰店",
  "period": "2024-01-01至2024-12-31",
  "auth_number": "AUTH-001",
  "stamping_entity": "公司B",
  "stamping_date": "2024-01-01"
}
```

**返回数据：**

```json
{
  "success": true,
  "message": "记录更新成功",
  "data": { /* 更新后的完整记录 */ }
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `saveEdit(e)` 函数（编辑模态框提交时）

---

#### 5. 删除记录

**路由：** `DELETE /upload-generated/api/record/<id>`  
**权限：** `@generate_admin_required`  
**功能：** 根据记录ID删除记录（不可恢复）

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | int | 记录ID |

**返回数据：**

```json
{
  "success": true,
  "message": "记录删除成功"
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `deleteRecord(id)` 函数（点击删除按钮并确认后）

---

### Word文档生成

#### 6. 生成单个Word文档

**路由：** `POST /upload-generated/api/generate/<id>`  
**权限：** `@generate_admin_required`  
**功能：** 根据记录ID生成对应的Word授权书文档

**技术说明：**
- 使用模板填充数据
- 文件名格式：`店铺类型_店铺名称.docx`
- 重复生成会覆盖旧文件

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | int | 记录ID |

**返回数据：**

```json
{
  "success": true,
  "message": "文档生成成功",
  "file_path": "static/generated_docs/天猫店_测试旗舰店.docx",
  "filename": "天猫店_测试旗舰店.docx"
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `generateWordDocument(id)` 函数（点击"Word"按钮时）

---

#### 7. 批量生成Word文档

**路由：** `POST /upload-generated/api/generate-batch`  
**权限：** `@generate_admin_required`  
**功能：** 根据多个记录ID批量生成Word授权书文档

**请求体（JSON）：**

```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**返回数据：**

```json
{
  "success": true,
  "message": "成功生成 5 个文档，失败 0 个",
  "results": {
    "success": 5,
    "failed": 0,
    "files": [
      "天猫店_测试旗舰店.docx",
      "京东店_测试专卖店.docx"
    ],
    "errors": []
  }
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `batchGenerateDocuments()` 函数（选中记录后点击"批量生成文档"按钮）

---

#### 8. 下载Word文档

**路由：** `GET /upload-generated/download/<filename>`  
**权限：** `@generated_required`  
**功能：** 根据文件名下载已生成的Word文档

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| filename | string | 文件名 |

**返回：** Word文件流（`application/vnd.openxmlformats-officedocument.wordprocessingml.document`）

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `generateWordDocument(id)` 函数（生成成功后自动触发下载）

---

### PDF文档生成

#### 9. 生成PDF文档

**路由：** `POST /upload-generated/api/generate-pdf/<id>`  
**权限：** `@generate_admin_required`  
**功能：** 根据记录ID生成对应的PDF授权书文档

**技术说明：**
- 先生成临时Word文档，再转换为PDF
- 转换完成后自动删除临时Word文件
- 文件名格式：`店铺类型_店铺名称.pdf`
- Windows环境需要Microsoft Word支持

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | int | 记录ID |

**返回数据：**

```json
{
  "success": true,
  "message": "PDF生成成功",
  "file_path": "static/generated_docs/天猫店_测试旗舰店.pdf",
  "filename": "天猫店_测试旗舰店.pdf"
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `generatePDFDocument(id)` 函数（点击"PDF"按钮时）
  - `previewPDF(id)` 函数（点击"预览"按钮且PDF不存在时）

---

#### 10. 检查PDF是否存在

**路由：** `GET /upload-generated/api/check-pdf/<id>`  
**权限：** `@generated_required`  
**功能：** 根据记录ID检查对应的PDF文件是否已生成

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | int | 记录ID |

**返回数据：**

```json
{
  "success": true,
  "exists": true,
  "filename": "天猫店_测试旗舰店.pdf"
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `previewPDF(id)` 函数（点击"预览"按钮时先检查）

---

#### 11. 预览PDF文档

**路由：** `GET /upload-generated/preview-pdf/<filename>`  
**权限：** `@generated_required`  
**功能：** 在浏览器中预览PDF文档（不触发下载）

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| filename | string | PDF文件名 |

**返回：** PDF文件流（`application/pdf`, `as_attachment=False`）

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `previewPDF(id)` 函数（检查或生成PDF后在新窗口打开）

---

#### 12. 下载PDF文档

**路由：** `GET /upload-generated/download-pdf/<filename>`  
**权限：** `@generated_required`  
**功能：** 下载PDF文档（触发浏览器下载）

**URL参数：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| filename | string | PDF文件名 |

**返回：** PDF文件流（`application/pdf`, `as_attachment=True`）

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `generatePDFDocument(id)` 函数（生成成功后自动触发下载）

---

#### 13. 批量生成PDF文档

**路由：** `POST /upload-generated/api/generate-pdf-batch`  
**权限：** `@generate_admin_required`  
**功能：** 根据多个记录ID批量生成PDF授权书文档

**技术说明：**
- 遍历每个记录，先生成Word再转换为PDF
- 提供成功/失败统计
- 转换完成后自动删除临时Word文件
- Windows环境需要Microsoft Word支持

**请求体（JSON）：**

```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**返回数据：**

```json
{
  "success": true,
  "message": "成功生成 5 个PDF，失败 0 个",
  "results": {
    "success": 5,
    "failed": 0,
    "files": [
      "天猫店_测试旗舰店.pdf",
      "京东店_测试专卖店.pdf"
    ],
    "errors": []
  }
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `batchGeneratePDFDocuments()` 函数（选中记录后点击"批量生成PDF"按钮）

---

#### 14. 批量下载文档（ZIP打包，自动生成缺失文件）

**路由：** `POST /upload-generated/api/download-batch`  
**权限：** `@generated_required`  
**功能：** 将多个文档打包为ZIP文件下载，**自动生成缺失的文件**

**技术说明：**
- 支持批量下载Word或PDF文档
- **智能检测**：自动检测文件是否存在
- **自动生成**：文件不存在时自动先生成，再打包
- 使用内存ZIP打包，无需创建临时文件
- 提供详细统计：新生成数量、已存在数量、失败数量
- ZIP文件名格式：`授权书_{type}_{timestamp}.zip`
- 内部文档文件名：`店铺类型_店铺名称.{docx|pdf}`

**请求体（JSON）：**

```json
{
  "ids": [1, 2, 3, 4, 5],
  "type": "word"  // 或 "pdf"
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ids | Array\<Integer\> | 是 | 要下载的记录ID数组 |
| type | string | 否 | 文件类型（`word` 或 `pdf`），默认为 `word` |

**返回：** ZIP文件流（`application/zip`）

**响应头（统计信息）：**

| 响应头名称 | 类型 | 说明 |
|-----------|------|------|
| X-Generated-Count | int | 新生成的文件数量 |
| X-Existed-Count | int | 已存在的文件数量 |
| X-Failed-Count | int | 生成失败的文件数量 |
| X-Total-Count | int | 成功打包的文件总数 |

**成功示例：**
- 文件流下载，同时返回统计响应头
- 前端可读取响应头显示详细统计信息

**错误返回：**

```json
{
  "success": false,
  "message": "所有文件生成失败，无法下载。失败原因：..."
}
```

**使用场景：**

1. **场景1：直接下载**
   - 选择10条记录
   - 点击"批量下载Word"
   - 系统检测到其中5个文件已存在，5个文件未生成
   - **自动生成** 5个缺失文件
   - 打包10个文件为ZIP下载
   - 提示："Word文档批量下载成功！（新生成 5 个，已存在 5 个）"

2. **场景2：全部需要生成**
   - 选择新导入的20条记录（尚未生成任何文件）
   - 点击"批量下载PDF"
   - **自动生成** 20个PDF文件
   - 打包20个文件为ZIP下载
   - 弹窗显示详细统计

3. **场景3：部分失败**
   - 选择15条记录
   - 其中2条数据缺少必填字段
   - 成功生成13个，失败2个
   - 打包13个成功的文件下载
   - 提示："Word文档批量下载成功！（新生成 10 个，已存在 3 个，失败 2 个）"

**调用位置：**
- `app/templates/uploadGeneratedFiles/list.html`
  - `batchDownloadDocuments(type)` 函数（选中记录后点击"批量下载Word"或"批量下载PDF"按钮）

---

### Excel导入

#### 15. 预览Excel数据

**路由：** `POST /upload-generated/preview`  
**权限：** `@generate_admin_required`  
**功能：** 解析上传的Excel文件并返回数据预览

**技术说明：**
- 使用openpyxl解析Excel
- 校验表头格式
- 自动对齐数据长度
- 跳过完全空行
- **日期格式自动转换**：
  - Excel的datetime对象 → `YYYY年M月D日`
  - Excel的日期序列号（如45737） → `YYYY年M月D日`
  - 适用于"用印时间"和"授权期间"等日期字段

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | Excel文件（multipart/form-data） |

**返回数据：**

```json
{
  "success": true,
  "rows": [
    {
      "使用模板": "模板A",
      "店铺类型": "旗舰店",
      "授权主体": "公司A",
      "授权平台": "天猫",
      "授权品牌": "品牌A",
      "品牌商标号": "12345678",
      "店铺名称": "测试旗舰店",
      "授权期间": "2024-01-01至2024-12-31",
      "授权字号": "AUTH-001",
      "授权方（盖章）主体": "公司B",
      "用印时间": "2024-01-01"
    }
  ],
  "count": 1
}
```

**错误返回（表头不匹配）：**

```json
{
  "success": false,
  "message": "表头不匹配",
  "expected": ["使用模板", "店铺类型", ...],
  "found": ["模板", "类型", ...]
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/upload.html`
  - `uploadAndPreview()` 函数（选择Excel文件后）

---

#### 16. 确认导入Excel数据

**路由：** `POST /upload-generated/confirm`  
**权限：** `@generate_admin_required`  
**功能：** 将预览确认后的Excel数据批量导入到数据库

**技术说明：**
- 支持事务处理
- 导入失败时自动回滚
- 批量插入提高效率

**请求体（JSON）：**

```json
{
  "rows": [
    {
      "使用模板": "模板A",
      "店铺类型": "旗舰店",
      "授权主体": "公司A",
      "授权平台": "天猫",
      "授权品牌": "品牌A",
      "品牌商标号": "12345678",
      "店铺名称": "测试旗舰店",
      "授权期间": "2024-01-01至2024-12-31",
      "授权字号": "AUTH-001",
      "授权方（盖章）主体": "公司B",
      "用印时间": "2024-01-01"
    }
  ]
}
```

**返回数据：**

```json
{
  "success": true,
  "inserted": 1
}
```

**调用位置：**
- `app/templates/uploadGeneratedFiles/upload.html`
  - `confirmImport()` 函数（预览后点击"确认导入"按钮）

---

## 数据模型

### Generated（授权书记录）

**表名：** `generated`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID |
| template_used | String | 使用模板 |
| store_type | String | 店铺类型 |
| authorized_entity | String | 授权主体 |
| platform | String | 授权平台 |
| brand | String | 授权品牌 |
| trademark_no | String | 品牌商标号 |
| store_name | String | 店铺名称 |
| period | String | 授权期间 |
| auth_number | String | 授权字号 |
| stamping_entity | String | 授权方（盖章）主体 |
| stamping_date | String | 用印时间 |
| created_at | DateTime | 创建时间 |

---

## 权限说明

### 1. @generate_admin_required（生成管理员权限）

**适用范围：**
- 数据导入页面
- 功能菜单页面
- 所有数据修改操作（新增、更新、删除）
- 所有文档生成操作（Word、PDF）

**权限要求：** 需要生成管理员角色

---

### 2. @generated_required（查看权限）

**适用范围：**
- 数据列表页面
- 数据查询操作
- 文件下载和预览操作

**权限要求：** 需要基本查看权限（包含生成管理员权限）

---

## 配置说明

### 相关配置项（config.py）

```python
# 模板文件存储目录
UPLOAD_FOLDER_TEMPLATE = 'app/static/templates'

# 生成文档输出目录
UPLOAD_FOLDER_SHOUQUAN = 'app/static/generated_docs'
```

### Excel表头要求

导入的Excel文件必须包含以下表头（顺序可调整）：

1. 使用模板
2. 店铺类型
3. 授权主体
4. 授权平台
5. 授权品牌
6. 品牌商标号
7. 店铺名称
8. 授权期间
9. 授权字号
10. 授权方（盖章）主体
11. 用印时间

---

## 错误处理

所有API接口遵循统一的错误返回格式：

```json
{
  "success": false,
  "message": "错误描述信息"
}
```

常见HTTP状态码：

- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器内部错误

---

## 相关文档

- [Word文档生成说明](WORD_GENERATOR_README.md)
- [PDF文档生成说明](PDF_GENERATOR_README.md)
- [配置路径说明](CONFIG_PATHS_SETUP.md)

---

**更新记录：**
- 2025-01-21：创建初始版本，包含所有接口文档

