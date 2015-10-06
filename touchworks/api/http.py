from touchworks.logger import Logger
import json
import uuid
import requests
import time

logger = Logger.get_logger(__name__)


class TouchWorksException(Exception):
    pass


class TouchWorksErrorMessages(object):
    GET_TOKEN_FAILED_ERROR = 'unable to acquire the token from web service'
    MAGIC_JSON_FAILED = 'magic json api failed'


class SecurityToken(object):
    def __init__(self, token, acquired_time=None):
        if not token:
            raise Exception('token can not be empty')
        if not acquired_time:
            self.acquired_time = time.time()
        else:
            self.acquired_time = acquired_time
        self.token = token


class TouchWorksEndPoints(object):
    GET_TOKEN = 'json/GetToken'
    MAGIC_JSON = 'json/MagicJson'


class TouchWorksMagicConstants(object):
    ACTION_SEARCH_PATIENTS = 'SearchPatients'
    RESULT_SEARCH_PATIENTS = 'searchpatientsinfo'
    ACTION_GET_DOCUMENTS = 'GetDocuments'
    RESULT_GET_DOCUMENTS = 'getdocumentsinfo'
    ACTION_GET_SCHEDULE = 'GetSchedule'
    RESULT_GET_SCHEDULE = 'getscheduleinfo'
    ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT = 'GetEncounterListForPatient'
    RESULT_GET_ENCOUNTER_LIST_FOR_PATIENT = 'getencounterlistforpatientinfo'
    ACTION_GET_PATIENT_INFO = 'GetPatient'
    RESULT_GET_PATIENT_INFO = 'getpatientinfo'
    ACTION_GET_ENCOUNTER = 'GetEncounter'
    RESULT_GET_ENCOUNTER = 'getencounterinfo'
    ACTION_SAVE_UNSTRUCTURED_DATA = 'SaveUnstructuredDocument'
    RESULT_SAVE_UNSTRUCTURED_DATA = 'saveunstructureddocument'
    ACTION_GET_DOCUMENT_TYPE = 'GetDocumentType'
    RESULT_GET_DOCUMENT_TYPE = 'getdocumenttypeinfo'
    ACTION_GET_DICTIONARY = 'GetDictionary'
    RESULT_GET_DICTIONARY = 'getdictionaryinfo'
    ACTION_SAVE_NOTE = 'SaveNote'
    RESULT_SAVE_NOTE = 'savenoteinfo'


class TouchWorks(object):
    TOKEN_DEFAULT_TIMEOUT_IN_SECS = 20 * 60

    def __init__(self, base_url, username,
                 password, app_name, cache_token=True,
                 token_timeout=TOKEN_DEFAULT_TIMEOUT_IN_SECS,
                 app_username=None):
        """
        creates an instance of TouchWorks, connects to the TouchWorks Web Service
        and caches username, password, app_name
        :param base_url: required
        :param username: required
        :param password: required
        :param app_name: required
        :param cache_token: optional
        :param token_timeout: optional
        :param app_username: optional
        :return:
        """
        if not base_url:
            raise ValueError('base_url can not be null')
        if not username:
            raise ValueError('username can not be null')
        if not password:
            raise ValueError('password can not be null')
        if not app_name:
            raise ValueError('app_name can not be null')
        self._base_url = base_url
        self._app_name = app_name
        self._username = username
        # FIXME: store username, password only if user decided to cache token
        self._password = password
        self._token_timeout = token_timeout
        self._ehr_username = app_username
        self._cache_token = cache_token
        self._token = self.get_token(self._app_name, self._username, self._password)

    def get_token(self, appname, username, password):
        """
            get the security token by connecting to TouchWorks API
        """
        ext_exception = TouchWorksException(
            TouchWorksErrorMessages.GET_TOKEN_FAILED_ERROR)
        data = {'Username': username,
                'Password': password}
        resp = self._http_request(TouchWorksEndPoints.GET_TOKEN, data)
        try:
            logger.debug('token : %s' % resp)
            if not resp.text:
                raise ext_exception
            try:
                uuid.UUID(resp.text, version=4)
                return SecurityToken(resp.text)
            except ValueError:
                logger.error('response was not valid uuid string. %s' % resp.text)
                raise ext_exception

        except Exception as ex:
            logger.exception(ex)
            raise ext_exception

    def _token_valid(self):
        """
        checks if the token cached is valid or has expired by comparing
        the time token was created with current time
        :return: True if token has not expired yet and False is token is empty or
                it has expired
        """
        if not self._cache_token:
            return False
        now = time.time()
        if now - self._token.acquired_time > self._token_timeout:
            logger.debug('token needs to be reset')
            return False
        return True

    def _http_request(self, api, data, headers=None):
        """
        internal method for handling request and response
        and raising an exception is http return status code is not success

        :rtype : response object from requests.post()
        """
        if not headers:
            headers = {'Content-Type': 'application/json'}
        if not self._token_valid:
            self._token = self.get_token(self._app_name, self._username, self._password)
        response = requests.post(self._base_url + '/' + api, data=json.dumps(data),
                                 headers=headers)
        # raise an exception if the status was not 200
        logger.debug(json.dumps(data))
        logger.debug(response.text)
        response.raise_for_status()
        return response

    def save_note(self, note_text, patient_id,
                  document_type,
                  document_status='Unsigned', wrapped_in_rtf='N'):
        """
        invokes TouchWorksMagicConstants.ACTION_SAVE_NOTE action
        :return: JSON response
        """
        allowed_document_status = ['Unsigned', 'Final']
        if document_status not in ['Unsigned', 'Final']:
            raise ValueError('document_status was invalid. allowed values are %s' %
                             allowed_document_status)
        magic = self._magic_json(action=TouchWorksMagicConstants.ACTION_SAVE_NOTE,
                                 patient_id=patient_id,
                                 parameter1=note_text,
                                 parameter2=document_type,
                                 parameter3=document_status,
                                 parameter4=wrapped_in_rtf)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SAVE_NOTE)
        return result

    def search_patients(self, ehr_username, search_criteria,
                        include_picture='N', organization_id=None):
        """
        invokes TouchWorksMagicConstants.ACTION_SEARCH_PATIENTS action
        :return: JSON response
        """
        include_picture = include_picture or ''
        organization_id = organization_id or ''
        magic = self._magic_json(action=TouchWorksMagicConstants.ACTION_SEARCH_PATIENTS,
                                 user_id=ehr_username,
                                 app_name=self._app_name,
                                 token=self._token.token,
                                 parameter1=search_criteria,
                                 parameter2=include_picture,
                                 parameter3=organization_id)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SEARCH_PATIENTS)
        return result

    def get_document_type(self, ehr_username, doc_type):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_DOCUMENT_TYPE action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_DOCUMENT_TYPE,
            app_name=self._app_name,
            user_id=ehr_username,
            token=self._token.token,
            parameter1=doc_type
        )
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_DOCUMENT_TYPE)
        return result

    def get_patient(self, ehr_username, patient_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_PATIENT_INFO action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_PATIENT_INFO,
            app_name=self._app_name,
            user_id=ehr_username,
            token=self._token.token,
            patient_id=patient_id
        )
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_PATIENT_INFO)
        return result

    def get_encounter(self, ehr_username, patient_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_ENCOUNTER,
            app_name=self._app_name,
            user_id=ehr_username,
            token=self._token.token,
            patient_id=patient_id
        )
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_ENCOUNTER)
        return result

    def get_dictionary(self, dictionary_name):
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_DICTIONARY,
            parameter1=dictionary_name,
            app_name=self._app_name,
            token=self._token.token)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_DICTIONARY)
        return result

    def find_document_type_by_name(self, entity_name, active='Y',
                                   match_case=True):
        """
        search document types by name and active(Y/N) status
        :param entity_name: entity name
        :return:
        """
        all_types = self.get_dictionary('Document_Type_DE')
        if match_case:
            filtered = filter(
                lambda x: x['Active'] == active and x['EntryName'].find(entity_name) >= 0,
                all_types)
        else:
            token = entity_name.lower()
            filtered = filter(
                lambda x: x['Active'] == active and x['EntryName'].lower().find(token) >= 0,
                all_types)
        return filtered

    def get_encounter_list_for_patient(self, ehr_username, patient_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT,
            app_name=self._app_name,
            token=self._token.token,
            user_id=ehr_username,
            patient_id=patient_id)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_ENCOUNTER_LIST_FOR_PATIENT)
        return result

    def save_unstructured_document(self, ehr_username,
                                   patient_id,
                                   encounter_id,
                                   document_content):
        """
        invokes TouchWorksMagicConstants.ACTION_SAVE_UNSTRUCTURED_DATA action
        :return: JSON response
        """
        doc_xml = "<docParams><item name='documentCommand' value='I'/>" + \
                  "<item name='documentType'  value='Chart'/>" + \
                  "<item name='authorCode' value='ResLet'/>" + \
                  "<item name='ahsEncounterID' value=‘@@ENCOUNTERID@@’/>" + \
                  "<item name='OrganizationID' value=''/>" + \
                  "<item name='accessionValue' value=''/>" + \
                  "<item name='appGroup' value='TouchWorks'/></docParams>"
        doc_xml = doc_xml.replace("@@ENCOUNTERID@@", str(encounter_id))
        print(doc_xml)
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SAVE_UNSTRUCTURED_DATA,
            app_name=self._app_name,
            patient_id=patient_id,
            token=self._token.token,
            user_id=ehr_username,
            parameter1=doc_xml,
            parameter2=document_content)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SAVE_UNSTRUCTURED_DATA)
        return result

    def get_schedule(self, ehr_username, start_date,
                     changed_since, include_pix, other_user='All',
                     appointment_types=None, status_filter='All'):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_SCHEDULE action
        :return: JSON response
        """
        if not start_date:
            raise ValueError('start_date can not be null')
        if not changed_since:
            changed_since = ''
        magic = self._magic_json(action=TouchWorksMagicConstants.ACTION_GET_SCHEDULE,
                                 app_name=self._app_name,
                                 user_id=ehr_username, token=self._token.token,
                                 parameter1=start_date,
                                 parameter2=changed_since,
                                 parameter3=include_pix,
                                 parameter4=other_user,
                                 parameter5=appointment_types,
                                 parameter6=status_filter)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_SCHEDULE)
        return result

    def get_documents(self, ehr_username, patient_id, start_date=None,
                      end_date=None, document_id=None, doc_type=None,
                      newest_document='N'):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_DOCUMENTS action
        :return: JSON response
        """

        if not start_date:
            start_date = ''
        if not end_date:
            end_date = ''
        if not doc_type:
            doc_type = ''
        magic = self._magic_json(action=TouchWorksMagicConstants.ACTION_GET_DOCUMENTS,
                                 user_id=ehr_username, token=self._token.token,
                                 patient_id=patient_id,
                                 app_name=self._app_name,
                                 parameter1=start_date,
                                 parameter2=end_date,
                                 parameter3=document_id,
                                 parameter4=doc_type,
                                 parameter5=newest_document)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_DOCUMENTS)
        return result

    def _magic_json(self, action='', user_id='', app_name='', patient_id='',
                    token='', parameter1='', parameter2='',
                    parameter3='', parameter4='', parameter5='',
                    parameter6='', data=''):
        """
        utility method to create a magic json object needed to invoke TouchWorks APIs
        :return: magic json
        """
        if not token:
            token = self._token.token
        if not app_name:
            app_name = self._app_name
        if not user_id:
            if self._ehr_username:
                user_id = self._ehr_username

        return {
            'Action': action,
            'AppUserID': user_id,
            'Appname': app_name,
            'PatientID': patient_id,
            'Token': token,
            'Parameter1': parameter1,
            'Parameter2': parameter2,
            'Parameter3': parameter3,
            'Parameter4': parameter4,
            'Parameter5': parameter5,
            'Parameter6': parameter6,
            'Data': data
        }

    def _get_results_or_raise_if_magic_invalid(self, magic, response, result_key):
        try:
            j_response = response.json()
            if j_response:
                if result_key in j_response[0]:
                    return j_response[0][result_key]
                elif 'Error' in j_response[0]:
                    if magic and 'Action' in magic:
                        raise TouchWorksException(
                            magic['Action'] + ' API failed' + ' : ' +
                            j_response[0]['Error'])
                    else:
                        raise TouchWorksException(
                            TouchWorksErrorMessages.MAGIC_JSON_FAILED + ' : ' +
                            j_response[0]['Error'])
            raise TouchWorksException(TouchWorksErrorMessages.MAGIC_JSON_FAILED)
        except Exception as ex:
            logger.exception(ex)
            raise TouchWorksException(TouchWorksErrorMessages.MAGIC_JSON_FAILED)
