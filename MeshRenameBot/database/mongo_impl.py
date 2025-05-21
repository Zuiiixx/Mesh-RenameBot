import os
import json
from typing import Union
from pymongo import MongoClient


class MongoDB(MongoClient):
    MODE_SAME_AS_SENT = 0
    MODE_AS_DOCUMENT = 1
    MODE_AS_GMEDIA = 2
    MODE_RENAME_WITHOUT_COMMAND = 3
    MODE_RENAME_WITH_COMMAND = 4

    def __init__(self, dburl=None):
        if dburl is None:
            dburl = os.environ.get("DATABASE_URL")
            if dburl is None:
                from MeshRenameBot.core.get_config import get_var  # Lazy import to avoid circular errors
                dburl = get_var("DATABASE_URL")
        super().__init__(dburl)
        self._db = self.get_database()

    def get_user_var(self, var: str, user_id: int) -> Union[None, str]:
        user = self._db.mesh_rename.find_one({"user_id": str(user_id)})
        if user:
            jdata = json.loads(user.get("json_data", "{}"))
            return jdata.get(var)
        return None

    def set_user_var(self, var: str, value: Union[int, str], user_id: int) -> None:
        users = self._db.mesh_rename
        user_id = str(user_id)

        user = users.find_one({"user_id": user_id})
        if user:
            jdata = json.loads(user.get("json_data", "{}"))
            jdata[var] = value
            users.update_one({"_id": user["_id"]}, {"$set": {"json_data": json.dumps(jdata)}})
        else:
            users.insert_one({
                "user_id": user_id,
                "json_data": json.dumps({var: value}),
                "file_choice": self.MODE_SAME_AS_SENT,
                "thumbnail": None
            })

    def get_thumbnail(self, user_id: int) -> Union[str, bool]:
        user = self._db.mesh_rename.find_one({"user_id": str(user_id)})
        if user and user.get("thumbnail"):
            user_dir = os.path.join(os.getcwd(), 'userdata', str(user_id))
            os.makedirs(user_dir, exist_ok=True)

            path = os.path.join(user_dir, "thumbnail.jpg")
            with open(path, "wb") as f:
                f.write(user["thumbnail"])
            return path
        return False

    def set_thumbnail(self, thumbnail: Union[str, bytes], user_id: int) -> bool:
        if isinstance(thumbnail, str):
            with open(thumbnail, "rb") as f:
                thumbnail = f.read()

        user_id = str(user_id)
        self._db.mesh_rename.update_one(
            {"user_id": user_id},
            {"$set": {"thumbnail": thumbnail}},
            upsert=True
        )
        return True

    def set_mode(self, mode: int, user_id: int) -> None:
        self._db.mesh_rename.update_one(
            {"user_id": str(user_id)},
            {"$set": {"file_choice": mode}},
            upsert=True
        )

    def get_mode(self, user_id: int) -> int:
        user = self._db.mesh_rename.find_one({"user_id": str(user_id)})
        return user.get("file_choice", self.MODE_SAME_AS_SENT) if user else self.MODE_SAME_AS_SENT