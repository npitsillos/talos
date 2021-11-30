import logging

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
    created_at = fields.DateTimeField(required=True)
    deadline = fields.DateTimeField()
    url = fields.URLField()
    team_name = fields.CharField(required=False)
    team_members = fields.ListField(fields.CharField())

class Tutorial(MongoModel):
    name = fields.CharField(required=True)
    created_at = fields.DateTimeField(required=True)
    url = fields.CharField(required=True)
    difficulty = fields.CharField()
    category = fields.CharField()