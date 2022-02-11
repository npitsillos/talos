import logging
import datetime

from pymodm import MongoModel, fields

logger = logging.getLogger(__name__)


class CogDetails(MongoModel):
    name = fields.CharField(required=True)
    local_path = fields.CharField(required=True)
    enabled = fields.BooleanField(default=True)
    loaded = fields.BooleanField(default=False)


class BotConfig(MongoModel):
    ADMIN_ROLE = fields.CharField()
    EXTENSIONS = fields.EmbeddedDocumentListField(CogDetails, default=[])


class Comp(MongoModel):
    name = fields.CharField(required=True)
    platform = fields.CharField(required=True)
    description = fields.CharField()
    created_at = fields.DateTimeField(required=True)
    deadline = fields.DateTimeField()
    merger_deadline = fields.DateTimeField()
    url = fields.URLField()
    team_name = fields.CharField(required=False)
    team_members = fields.ListField(fields.CharField())
    max_team_size = fields.IntegerField()
    max_daily_subs = fields.IntegerField()
    subs_today = fields.IntegerField(default=0)
    finished_on = fields.DateTimeField()

    def status(self):

        members = ",".join(self.team_members)
        deadline = self.deadline if self.deadline > datetime.datetime.now() else "Passed"
        merger_deadline = self.merger_deadline if self.merger_deadline > datetime.datetime.now() else "Passed"
        status = (
            f":triangular_flag_on_post:**\t{self.name}**\n***{self.description}.***\n**Merger Deadline:**\t{merger_deadline}"
            + f"\n**Deadline:**\t{deadline}\n**Team Name:**\t{self.team_name}\n:busts_in_silhouette:\t{members}\n"
            + f"**Team Size:**\t{self.max_team_size}\n:link:\t{self.url}"
        )

        return status


class TutorialModel(MongoModel):
    name = fields.CharField(required=True)
    created_at = fields.DateTimeField(required=True)
    url = fields.CharField(required=True)
    difficulty = fields.CharField()
    category = fields.CharField()


class UserAuth(MongoModel):
    user = fields.CharField(required=True)
    auth_info = fields.DictField(required=True)