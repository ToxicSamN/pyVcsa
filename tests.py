

from pyVcsa.rest import CimSession
from pyVcsa.recovery.backup.job import Job

if __name__ == '__main__':
    vcenter = ''
    cim = CimSession(vcenter=vcenter,
                     username='',
                     password='',
                     ssl_verify=False,
                     ignore_weak_ssl=True)
    cim.get_session()
    bk_job = Job(cim_session=cim)
    bk_job.create(parts=['common'],
                  location='',
                  location_type='FTP',
                  location_user='',
                  location_password=""
                  )

    print('break')
