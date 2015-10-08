from touchworks.api.http import TouchWorks, TouchWorksException
import json
import unittest
import uuid
from touchworks.logger import Logger
import pprint
from nose.tools import raises
import random

logger = Logger.get_logger(__name__)


class TestAPIs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(open('tests/config.json').read())
        cls.url = cls.config['server']
        cls.svc_username = cls.config['serviceusername']
        cls.svc_password = cls.config['servicepassword']
        cls.app_name = cls.config['appname']

    def setUp(self):
        pass

    def test_get_dictionary(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password=self.svc_password,
                              app_username=self.config['ehr_username'],
                              app_name=self.app_name,
                              cache_token=True)
        self.api.get_dictionary('Document_Type_DE')
        rtf_doc_types = self.api.find_document_type_by_name('Consult', match_case=False)
        for a_type in rtf_doc_types:
            logger.debug(pprint.pformat(a_type))

    def test_save_note(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password=self.svc_password,
                              app_name=self.app_name,
                              app_username=self.config['ehr_username'],
                              cache_token=True)
        patients = self.api.search_patients('J*', 'N')
        self.api.save_note('hello there', document_type='Consult',
                           patient_id=patients[0]['ID'],
                           document_status='Final',
                           wrapped_in_rtf='Y')

    def test_get_encounters(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password=self.svc_password,
                              app_username=self.config['ehr_username'],
                              app_name=self.app_name,
                              cache_token=True)
        patients = self.api.search_patients('J*', 'N')
        if patients and len(patients) >= 5:
            for patient in patients[0:5]:
                encounters = self.api.get_encounter_list_for_patient(patient_id=patient['ID'])
                for encounter in encounters:
                    logger.debug(pprint.pformat(encounter))
                    self.api.save_unstructured_document(
                        ehr_username=self.config['ehr_username'],
                        patient_id=patient['ID'],
                        encounter_id=encounter['Encounterid'],
                        document_content='random note : %s' % str(uuid.uuid4())[0:5])
                    # if 'ReferringProviderID' in encounter:

                    logger.debug(pprint.pformat(patient))

    def test_search_patients(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password=self.svc_password,
                              app_username=self.config['ehr_username'],
                              app_name=self.app_name,
                              cache_token=True)
        patients = self.api.search_patients('J*', 'N')
        if patients and len(patients) >= 5:
            for patient in patients[0:5]:
                self.api.get_patient(ehr_username=self.config['ehr_username'],
                                     patient_id=patient['ID'])
                logger.debug(pprint.pformat(patient))

    def test_get_document_types(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password=self.svc_password,
                              app_username=self.config['ehr_username'],
                              app_name=self.app_name,
                              cache_token=True)
        types = ['Chart', 'Consult', 'SpecReport', 'ChartCopy']
        for type in types:
            result = self.api.get_document_type(ehr_username=self.config['ehr_username'],
                                                doc_type='')
            logger.debug('\n%s' % pprint.pformat(result))

    def test_get_schedule(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password=self.svc_password,
                              app_name=self.app_name,
                              cache_token=True)
        schedules = self.api.get_schedule(ehr_username=self.config['ehr_username'],
                                          start_date='9/1/2015',
                                          end_date='10/4/2015',
                                          changed_since='',
                                          include_pix='',
                                          other_user='',
                                          appointment_types='',
                                          status_filter='')
        with open('/tmp/schedules.json', 'w+') as f:
            f.write(json.dumps(schedules))
        logger.debug('retrieved %s schedules ' % len(schedules))
        if schedules and len(schedules) >= 5:
            for schedule in schedules[0:5]:
                logger.debug(pprint.pformat(schedule))
                logger.debug(schedule['patientID'])
                self.api.get_patient(ehr_username=self.config['ehr_username'],
                                     patient_id=schedule['patientID'])

    @raises(TouchWorksException)
    def test_invalid_password(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password='wrong password',
                              app_name=self.app_name,
                              cache_token=True)

    def test_patients(self):
        self.api = TouchWorks(base_url=self.url,
                              username=self.svc_username,
                              password=self.svc_password,
                              app_name=self.app_name,
                              app_username=self.config['ehr_username'],
                              cache_token=True)
        patients = self.api.search_patients('F*')
        for patient in random.sample(patients, 3):
            encounters = self.api.get_encounter_list_for_patient(patient['ID'])
            # get patient clinical summary
            for encounter in encounters:
                logger.info('encounter : %s' % pprint.pformat(encounter))
                clinical_summary = self.api.get_clinical_summary(
                    patient_id=patient['ID'],
                    encounter_id_identifer=encounter['Encounterid'],
                    section='')
                logger.info('clinical summary : \n%s' % pprint.pformat(clinical_summary))
            # patient activity
            activities = self.api.get_patient_activity(patient['ID'])
            for activity in activities:
                logger.info('\n%s' % pprint.pformat(activity))
