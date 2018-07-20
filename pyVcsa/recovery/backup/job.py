
import json
from pyVcsa.exceptions import ValidationError
from pyVcsa.recovery.backup.exceptions import JobError, PartsValidationError
from pyVcsa.rest import ApplianceAPI


JOB_URL_BASE = 'recovery/backup/job/'


class Job(ApplianceAPI):

    class JobData:

        def __init__(self):
            self.id = None
            self.message = None
            self.start_time = None
            self.end_time = None
            self.progress = None
            self.state = None

        def __str__(self):
            return "id: {}\nstart_time: {}\nend_time: {}\nmessage: {}\nprogress: {}\nstate: {}".format(self.id,
                                                                                                self.start_time,
                                                                                                self.end_time,
                                                                                                self.message,
                                                                                                self.progress,
                                                                                                self.state)

    def __init__(self, cim_session):
        self.session = cim_session
        self.vcs = cim_session.vcenter
        self.job = Job.JobData()
        self.location = None
        self.location_type = None
        self.location_user = None
        self.__location_secret = None
        self.__backup_secret = None
        self.backup_protected = False
        self.description = None
        self.parts = [] # valid options common, seat
        super().__init__(cim_session.vcenter)
        self.base_url += JOB_URL_BASE

    def create(self, parts, location, location_type='FTP', location_user='anonymous', location_password='',
               backup_password=None, description='VCSA Backup Job'):

        self.location = location
        self.location_type = location_type
        self.location_user = location_user
        self. __location_secret = location_password or ''
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

        self.session.post(self.base_url, json=self._create_request())
        self._set_obj_job()
        self._monitor_job()

    def _set_obj_job(self):
        if self.session.response_data and isinstance(self.session.response_data, dict):
            self.job.id = self.session.response_data['value'].get('id', None)
            self.job.start_time = self.session.response_data['value'].get('start_time', None)
            self.job.end_time = self.session.response_data['value'].get('end_time', None)
            self.job.message = self.session.response_data['value'].get('messages', [])
            self.job.progress = self.session.response_data['value'].get('progress', None)
            self.job.state = self.session.response_data['value'].get('state', None)

    def _monitor_job(self):
        print("Job Running")
        while self.job.id and not self.job.state == 'SUCCEEDED' and not self.job.state == 'FAILED':
            # job is still running

            self.get()

        if self.job.state == 'FAILED':
            raise JobError('Job {} FAILED\n{}'.format(self.job.id, self.job))
        print("Job Complete")

    def _create_request(self):
        self.request_data = self._format_json()
        return self.request_data

    def cancel(self):
        cancel_url = '{}{}/cancel'.format(self.base_url, self.job.id)
        self.session.post(cancel_url)
        self._set_obj_job()
        return self.job

    def get(self, job_id=None):
        if not job_id:
            job_id = self.job.id
        get_url = '{}{}'.format(self.base_url, job_id)
        self.session.get(get_url)
        self._set_obj_job()


    def list(self):
        list_url = '{}'.format(self.base_url)
        self.session.get(list_url)
        return self.session.response.content.decode('utf8')

    def _format_json(self):
        json_dict = {
            'piece': {
                'backup_password': self.__backup_secret,
                'location': self.location,
                'location_user': self.location_user,
                'location_password': self.__location_secret,
                'location_type': self.location_type,
                'comment': self.description,
                'parts': self.parts
            }
        }
        return json_dict
