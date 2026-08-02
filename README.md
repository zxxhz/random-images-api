# 随机图片 API（random-image-api）

基于 FastAPI 的随机图片 API 服务。将图片按分类存放于 `images/` 文件夹的子文件夹中，即可通过接口随机获取或指定获取图片。

## 功能特性

- **随机获取（全分类）**：从所有图片中随机返回一张，支持链接跳转
- **随机获取（按分类）**：按子文件夹名（分类）随机返回一张
- **指定获取**：通过 `子文件夹名/文件名` 精确获取指定图片
- 支持常见图片格式：`.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`
- 内置路径穿越防护

## 目录结构

```
random-douni-api/
├── main.py              # FastAPI 应用
├── images/              # 图片根目录
│   ├── cat/             # 分类（子文件夹）
│   │   ├── a.jpg
│   │   └── b.png
│   └── dog/             # 分类（子文件夹）
│       └── c.gif
├── pyproject.toml
└── README.md
```

> 图片需放置在 `images/` 下的各子文件夹中，子文件夹名即为分类名。

## 安装与运行

本项目使用 `uv` 管理依赖，Python 版本要求 3.12。

```bash
# 安装依赖
uv sync

# 启动开发服务（默认监听 127.0.0.1:8000）
fastapi dev main.py
# 或
uvicorn main:app --reload
```

启动后访问 `http://127.0.0.1:8000/docs` 可查看交互式 API 文档。

## 接口说明

### 1. 随机图片（全分类）

```
GET /random
```

从 `images/` 下所有子文件夹的图片中随机选取一张，302 跳转到该图片的实际地址。

**响应**：`302 Redirect` → `/image/{子文件夹}/{文件名}`

**示例**：
```bash
curl -i http://127.0.0.1:8000/random
```

若无任何图片，返回 `404`。

### 2. 随机图片（按分类）

```
GET /random/{category}
```

从指定分类（子文件夹）中随机选取一张图片，302 跳转到该图片的实际地址。

| 参数 | 位置 | 说明 |
|------|------|------|
| `category` | path | 分类名，即 `images/` 下的子文件夹名 |

**响应**：`302 Redirect` → `/image/{category}/{文件名}`

**示例**：
```bash
curl -i http://127.0.0.1:8000/random/cat
```

若分类不存在或该分类下无图片，返回 `404`。

### 3. 指定图片

```
GET /image/{subfolder}/{filename}
```

根据子文件夹名与文件名直接返回指定图片，响应体为图片二进制流，`Content-Type` 自动按扩展名设置。

| 参数 | 位置 | 说明 |
|------|------|------|
| `subfolder` | path | 子文件夹名 |
| `filename` | path | 文件名（含扩展名） |

**响应**：`200 OK`，body 为图片文件

**示例**：
```bash
curl -o a.jpg http://127.0.0.1:8000/image/cat/a.jpg
```

若图片不存在，返回 `404`。

## 使用示例

在 HTML 中用作随机图床：
```html
<img src="http://127.0.0.1:8000/random" alt="随机图片" />
<img src="http://127.0.0.1:8000/random/cat" alt="随机猫咪图片" />
```

直接引用指定图片：
```html
<img src="http://127.0.0.1:8000/image/cat/a.jpg" alt="指定图片" />
```

## 安全说明

- `/image` 接口对路径参数进行校验，拒绝包含 `..` 的请求，防止目录穿越攻击
- 仅返回 `images/` 目录下存在的文件
