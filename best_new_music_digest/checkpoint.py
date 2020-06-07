"""
Checkpointing.
"""

from pymongo import MongoClient

from best_new_music_digest import settings


class Checkpointer:
    """
    Saves and loads checkpoints.
    """

    def __init__(self):
        self.checkpoints = MongoClient(settings.MONGODB_URI)["best-new-music-digest"].checkpoints

    def get_checkpoint(self, name):
        """
        Returns the checkpoint for a given name (empty if doesn't already exist).
        """

        checkpoint = self.checkpoints.find_one({"name": name})
        return checkpoint["link"] if checkpoint else ""

    def save_checkpoint(self, name, link):
        """
        Saves the checkpoint.
        """

        self.checkpoints.find_one_and_update(
            {"name": name},
            {"$set": {"link": link}},
            upsert=True,
        )
