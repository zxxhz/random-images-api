import random
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, RedirectResponse

app = FastAPI()

# 图片根目录（本项目 main.py 同级 images 文件夹）
IMAGES_DIR = Path(__file__).parent / "images"
# 支持的图片扩展名
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def list_images(category: str | None = None) -> list[Path]:
    """列出指定分类（子文件夹）下的所有图片；未指定分类则列出所有子文件夹下的图片。

    该函数涉及文件系统遍历（rglob / is_file），属于阻塞 I/O，
    需在异步端点中通过 run_in_threadpool 调用，避免阻塞事件循环。
    """
    if category:
        category_dir = IMAGES_DIR / category
        if not category_dir.is_dir():
            return []
        search_dir = category_dir
    else:
        search_dir = IMAGES_DIR

    return [
        p
        for p in search_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


@app.get("/random")
async def random_image():
    """随机获取一张图片（全分类），302 跳转到具体图片地址。"""
    images = await run_in_threadpool(list_images)
    if not images:
        raise HTTPException(status_code=404, detail="未找到任何图片")
    chosen = random.choice(images)
    rel_path = chosen.relative_to(IMAGES_DIR).as_posix()
    return RedirectResponse(url=f"/image/{rel_path}", status_code=302)


@app.get("/random/{category}")
async def random_image_by_category(category: str):
    """按分类（子文件夹名）随机获取一张图片，302 跳转到具体图片地址。"""
    images = await run_in_threadpool(list_images, category)
    if not images:
        raise HTTPException(
            status_code=404, detail=f"分类 '{category}' 不存在或无图片"
        )
    chosen = random.choice(images)
    rel_path = chosen.relative_to(IMAGES_DIR).as_posix()
    return RedirectResponse(url=f"/image/{rel_path}", status_code=302)


@app.get("/image/{subfolder}/{filename}")
async def get_image(subfolder: str, filename: str):
    """根据 子文件夹名/文件名 直接返回指定图片。"""
    # 安全校验：防止路径穿越
    if ".." in subfolder or ".." in filename or "/" in subfolder:
        raise HTTPException(status_code=404, detail="图片不存在")

    file_path = IMAGES_DIR / subfolder / filename
    # is_file() 涉及文件系统 I/O，丢到线程池避免阻塞事件循环
    if not await run_in_threadpool(file_path.is_file):
        raise HTTPException(status_code=404, detail="图片不存在")

    # FileResponse 内部使用 anyio 在线程池中流式读取文件，不会阻塞事件循环
    return FileResponse(file_path)
