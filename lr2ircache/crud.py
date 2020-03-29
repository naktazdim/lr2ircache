from logging import getLogger
from datetime import datetime, timedelta

import pause
from sqlalchemy.orm import Session
import lr2irscraper

from . import models


lr2ir_last_accessed = datetime.fromtimestamp(0)
LR2IR_ACCESS_INTERVAL = timedelta(seconds=5)  # ひとまずハードコード


def wait():
    global lr2ir_last_accessed
    logger = getLogger(__name__)

    until = lr2ir_last_accessed + LR2IR_ACCESS_INTERVAL
    if until > datetime.now():
        logger.info("wait until {}...".format(until.isoformat()))
        pause.until(until)
    lr2ir_last_accessed = datetime.now()


def get_item(db: Session, bmsmd5: str):
    logger = getLogger(__name__)

    db_item = db.query(models.Item).filter(models.Item.bmsmd5 == bmsmd5).one_or_none()

    if db_item is None:  # データベース内になかったらLR2IRから情報を読んでキャッシュ
        logger.info("item not found in the database: {}".format(bmsmd5))
        logger.info("fetch item info from LR2IR ...")
        wait()
        bms_info = lr2irscraper.get_bms_info(bmsmd5)  # LR2IRから情報を読む
        if bms_info is None:
            logger.info("unregistered in LR2IR".format(bmsmd5))
            return None  # もしLR2IRにもない譜面だったらNoneを返して修了
        logger.info("succeeded".format(bmsmd5))
        # 無事LR2IRからデータが取れたら、データベースにキャッシュしておく
        db_item = models.Item(bmsmd5=bmsmd5, **bms_info.to_dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

    return db_item
