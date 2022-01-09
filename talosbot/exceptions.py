class InvalidCategoryException(Exception):
    pass


class CompetitionAlreadyExistsException(Exception):
    pass


class CompetitionAlreadyArchivedException(Exception):
    pass


class TutorialAlreadyExistsException(Exception):
    pass


class TeamAlreadyHasNameException(Exception):
    def __init__(self, team_name, *args, **kwargs):
        self.team_name = team_name


class MaxSubmissionsReachedException(Exception):
    pass
