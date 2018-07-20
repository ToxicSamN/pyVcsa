
import json
from pyVcsa.exceptions import ValidationError
from pyVcsa.recovery.backup.job import Job


BACKUP_URL_BASE = 'recovery/backup/'

class ValidateJob(Job):

    def __init__(self, cim_session):
        super().__init__(cim_session.vcenter)
        self.base_url += BACKUP_URL_BASE

    def pre_backup_validation(self, parts, location, location_type='FTP', location_user='anonymous', location_password='',
                 backup_password=None, description='Validate Backup Job before taking backup'):
        self.location = location
        self.location_type = location_type
        self.location_user = location_user
        self.__location_secret = location_password or ''
        self.__backup_secret = backup_password or ''
        self.description = description

        if isinstance(parts, list) or isinstance(parts, tuple):
            self.parts = parts
        elif isinstance(parts, str):
            self.parts = [parts]
        else:
            # invalid type
            raise ValidationError(
                "Paramenter validation on 'parts' failed. Type {} not of valid type 'list' or 'string'".format(
                    type(parts)))
        if not self.parts.__contains__('common') and not self.parts.__contains__('seat'):
            raise PartsValidationError(
                "Parts parameter contains invalid arguments. Expected 'seat' or 'common'\nParameter 'parts': {}".format(
                    self.parts)
            )

        if backup_password:
            self.backup_protected = True

        self._create_request()
        self.session.post('{}validate'.format(self.base_url))
