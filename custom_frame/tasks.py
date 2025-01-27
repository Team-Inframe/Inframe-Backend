from .models import CustomFrame
from config.celery import app
import logging
from django_redis import get_redis_connection

logger = logging.getLogger("inframe")
redis_conn = get_redis_connection("default")

@app.task
def update_hot_custom_frame():    
    logger.info(f"핫한 커스텀 프레임 스케쥴링")
    hot_custom_frames = redis_conn.zrevrange("custom_frame_bookmarks", 0, 3, withscores=True)
    
    for index,(custom_frame_id,score) in enumerate(hot_custom_frames):
        custom_frame_id = custom_frame_id.decode("utf-8")
        
        try:
            custom_frame = CustomFrame.objects.get(custom_frame_id=custom_frame_id)
        except CustomFrame.DoesNotExist:
            continue
        
        bookmarks_snapshot = redis_conn.zscore("custom_frame_bookmarks", custom_frame_id)
        if bookmarks_snapshot is None:
            bookmarks_snapshot = 0
            
        custom_frame_data = {
            "custom_frame_id": custom_frame.custom_frame_id,
            "custom_frame_title": custom_frame.custom_frame_title,
            "custom_frame_url": custom_frame.custom_frame_url,
            "bookmarks": custom_frame.bookmarks,
            "bookmarks_snapshot": int(bookmarks_snapshot),
            
        }
        for key, value in custom_frame_data.items():
            redis_conn.hset(f"hot_custom_frame:{index+1}", key, value)    