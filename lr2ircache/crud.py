from logging import getLogger
from datetime import datetime, timedelta
import bz2

import pause
from sqlalchemy.orm import Session
import lr2irscraper

from . import models
from .database import SessionLocal

LR2IR_ACCESS_INTERVAL = timedelta(seconds=5)  # ひとまずハードコード
LR2IR_RANKING_CACHE_EXPIRATION_INTERVAL = timedelta(days=1)  # ひとまずハードコード


def wait():
    logger = getLogger(__name__)

    session = SessionLocal()
    db_last_accessed = session.query(models.LR2IRLastAccessed).one()  # type: models.LR2IRLastAccessed
    until = db_last_accessed.last_accessed + LR2IR_ACCESS_INTERVAL
    db_last_accessed.last_accessed = max(until, datetime.now())
    session.commit()

    if until > datetime.now():
        logger.info("wait until {}...".format(until.isoformat()))
        pause.until(until)


def get_item(db: Session, bmsmd5: str, no_cache=False):
    logger = getLogger(__name__)

    db_item = db.query(models.Item).filter(models.Item.bmsmd5 == bmsmd5).one_or_none()
    if no_cache and db_item:  # no_cache の場合はデータがあったら削除
        db.delete(db_item)
        db.commit()
        db_item = None

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


def get_ranking(db: Session, bmsmd5: str, no_cache=False):
    logger = getLogger(__name__)

    db_ranking = db.query(models.Ranking).filter(models.Ranking.bmsmd5 == bmsmd5).one_or_none()
    if no_cache and db_ranking:  # no_cache の場合はデータがあったら削除
        db.delete(db_ranking)
        db.commit()
        db_ranking = None

    if db_ranking is None:  # ランキングがキャッシュされていなければ
        logger.info("ranking not found in the database: {}".format(bmsmd5))
    else:  # ランキングがキャッシュされていれば
        expire_date = db_ranking.last_accessed + LR2IR_RANKING_CACHE_EXPIRATION_INTERVAL
        if expire_date < datetime.now():  # ランキングのキャッシュが古ければ
            logger.info("ranking cache expired: {}".format(bmsmd5))
        else:  # 新鮮なキャッシュがあればそれをそのまま返して終了
            return db_ranking

    # 新鮮なキャッシュがなければLR2IRからデータを取得してキャッシュ
    logger.info("fetch ranking from LR2IR ...")
    wait()
    ranking_df = lr2irscraper.get_ranking(bmsmd5).to_dataframe()  # LR2IRから情報を読む
    if len(ranking_df) == 0:
        logger.info("unregistered in LR2IR".format(bmsmd5))
        return None  # もしLR2IRにもない譜面だったらNoneを返して修了
    logger.info("succeeded".format(bmsmd5))
    # 無事LR2IRからデータが取れたら、データベースにキャッシュしておく
    ranking_compressed = bz2.compress(ranking_df.to_json(orient="records").encode())
    if db_ranking is None:
        db_ranking = models.Ranking(bmsmd5=bmsmd5, ranking=ranking_compressed, last_accessed=datetime.now())
        db.add(db_ranking)
    else:
        db_ranking.ranking = ranking_compressed
        db_ranking.last_accessed = datetime.now()
    db.commit()
    db.refresh(db_ranking)

    return db_ranking
