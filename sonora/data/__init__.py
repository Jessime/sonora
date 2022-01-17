import importlib.resources

from loguru import logger


def get_img(name):
    from pathlib import Path

    try:
        with importlib.resources.path("sonora.data", name) as img_path:
            img = str(img_path)
            return img
    except ModuleNotFoundError:
        with importlib.resources.path("data", name) as img_path:
            img = Path("data") / name
            logger.info("I DON'T KNOW IF I GET IN HERE OR NOT")
    if "sonora/sonora" in img:
        img = img.replace("sonora/", "", 1)
        logger.info(f"this is so stupid")
    logger.info(img)
    return img
