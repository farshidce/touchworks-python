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
    ACTION_GET_TASKLIST_BY_VIEW = 'GetTaskListByView'
    RESULT_GET_TASKLISTBY_VIEW = 'gettasklistbyviewinfo'
    ACTION_GET_DELEGATES = 'GetDelegates'
    RESULT_GET_DELEGATES = 'getdelegatesinfo'
    ACTION_GET_TASK_COMMENTS = 'GetTaskComments'
    RESULT_GET_TASK_COMMENTS = 'gettaskcommentsinfo'
    ACTION_SAVE_TASK = 'savetask'
    RESULT_SAVE_TASK = 'savetaskinfo'
    ACTION_SEARCH_TASK_VIEWS = 'SearchTaskViews'
    RESULT_SEARCH_TASK_VIEWS = 'searchtaskviewsinfo'
    ACTION_SAVE_TASK_STATUS = 'SaveTaskStatus'
    RESULT_SAVE_TASK_STATUS = 'savetaskstatusinfo'
    ACTION_GET_TASK = 'GetTask'
    RESULT_GET_TASK = 'gettaskinfo'
    ACTION_SAVE_TASK_COMMENT = 'SaveTaskComent'
    RESULT_SAVE_TASK_COMMENT = 'savetaskcommentinfo'
    ACTION_SAVE_MSG_FROM_PAT_PORTAL = 'SaveMsgFromPatPortal'
    RESULT_SAVE_MSG_FROM_PAT_PORTAL = 'savemsgfrompatportalinfo'
    ACTION_GET_TASK_LIST = 'GetTaskList'
    RESULT_GET_TASK_LIST = 'gettasklistinfo'
    ACTION_SET_PATIENT_LOCATION_AND_STATUS = 'SetPatientLocationAndStatus'
    RESULT_SET_PATIENT_LOCATION_AND_STATUS = 'setpatientlocationandstatusinfo'
    ACTION_GET_CLINICAL_SUMMARY = 'GetClinicalSummary'
    RESULT_GET_CLINICAL_SUMMARY = 'getclinicalsummaryinfo'
    ACTION_GET_PATIENT_ACTIVITY = 'GetPatientActivity'
    RESULT_GET_PATIENT_ACTIVITY = 'getpatientactivityinfo'
    ACTION_GET_PATIENT_PHARAMCIES = 'GetPatientPharmacies	'
    RESULT_GET_PATIENT_PHARAMCIES = 'getpatientpharmaciesinfo'
    ACTION_SET_PATIENT_MEDHX_FLAG = 'SetPatientMedHXFlag	'
    RESULT_SET_PATIENT_MEDHX_FLAG = 'setpatientmedhxflaginfo'
    ACTION_GET_CHANGED_PATIENTS = 'GetChangedPatients	'
    RESULT_GET_CHANGED_PATIENTS = 'getchangedpatientsinfo'
    ACTION_GET_PATIENT_LOCATIONS = 'GetPatientLocations	'
    RESULT_GET_PATIENT_LOCATIONS = 'getpatienlLocationsinfo'
    ACTION_GET_USER_ID = 'GetUserID	'
    RESULT_GET_USER_ID = 'getuseridinfo'
    ACTION_GET_PROVIDER = 'GetProvider'
    RESULT_GET_PROVIDER = 'getproviderinfo'
    ACTION_GET_PROVIDER_INFO = 'GetProviderInfo'
    RESULT_GET_PROVIDER_INFO = 'getproviderinfoinfo'
    ACTION_GET_PROVIDERS = 'GetProviders'
    RESULT_GET_PROVIDERS = 'getprovidersinfo'
    ACTION_GET_USER_PREFERENCES = 'GetUserPreferences'
    RESULT_GET_USER_PREFERENCES = 'getuserpreferencesinfo'


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

    def search_patients(self, search_criteria,
                        include_picture='N', organization_id=None):
        """
        invokes TouchWorksMagicConstants.ACTION_SEARCH_PATIENTS action
        :return: JSON response
        """
        include_picture = include_picture or ''
        organization_id = organization_id or ''
        magic = self._magic_json(action=TouchWorksMagicConstants.ACTION_SEARCH_PATIENTS,
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

    def get_encounter_list_for_patient(self, patient_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT,
            app_name=self._app_name,
            token=self._token.token,
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
                  "<item name='ahsEncounterID' value='@@ENCOUNTERID@@’/>" + \
                  "<item name='OrganizationID' value=''/>" + \
                  "<item name='accessionValue' value=''/>" + \
                  "<item name='appGroup' value='TouchWorks'/></docParams>"
        doc_xml = doc_xml.replace("@@ENCOUNTERID@@", str(encounter_id))
        print(doc_xml)
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SAVE_UNSTRUCTURED_DATA,
            patient_id=patient_id,
            user_id=ehr_username,
            parameter1=doc_xml,
            parameter2=document_content)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SAVE_UNSTRUCTURED_DATA)
        return result

    def set_patient_location_and_status(self, patient_id,
                                        encounter_status,
                                        patient_location):
        """
        invokes TouchWorksMagicConstants.ACTION_SET_PATIENT_LOCATION_AND_STATUS action
        :param encounter_status - EntryName from the Encounter_Status_DE dictionary.
            The desired entryname can be looked up with the GetDictionary action.
        :param patient_location - EntryName from the Site_Location_DE dictionary.
            The desired entryname can be looked up with the GetDictionary action.
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SET_PATIENT_LOCATION_AND_STATUS,
            patient_id=patient_id,
            parameter1=encounter_status,
            parameter2=patient_location)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SET_PATIENT_LOCATION_AND_STATUS)
        return result

    def get_clinical_summary(self, patient_id,
                             section,
                             encounter_id_identifer,
                             verbose=''):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_CLINICAL_SUMMARY action
        :param patient_id:
        :param section - if one of the following values is specified, Section indicates
            which section of clinical data to return. If no Section is specified,
            all sections with data are returned. You can specify multiple sections
            using a pipe-delimited list. For example, "Vitals|Results."
                List
                ChiefComplaint
                Vitals
                Activities
                Alerts
                Problems
                Results
                History
                Medications
                Allergies
                Immunizations
                Orders
        :param encounter_id_identifer - identifier for the encounter. Used in conjunction with
            the "ChiefComplaint" when called in Parameter1. EncounterID can be acquired
            with the Unity call GetEncounterList.
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_CLINICAL_SUMMARY,
            patient_id=patient_id,
            parameter1=section,
            parameter2=encounter_id_identifer,
            parameter3=verbose)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_CLINICAL_SUMMARY)
        return result

    def get_patient_activity(self, patient_id, since=''):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_PATIENT_ACTIVITY,
            patient_id=patient_id,
            parameter1=since)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_PATIENT_ACTIVITY)
        return result

    def set_patient_medhx_flag(self, patient_id,
                               medhx_status):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :param patient_id
        :param medhx_status - 	Field in EEHR expects U, G, or D. SP defaults to Null and
            errors out if included.
                U=Unknown
                G=Granted
                D=Declined
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SET_PATIENT_MEDHX_FLAG,
            patient_id=patient_id,
            parameter1=medhx_status
        )
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SET_PATIENT_MEDHX_FLAG)
        return result

    def get_changes_patients(self, patient_id,
                             since,
                             clinical_data_only='Y',
                             verbose='Y',
                             quick_scan='Y',
                             which_field='',
                             what_value=''):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_CHANGED_PATIENTS,
            patient_id=patient_id,
            parameter1=since,
            parameter2=clinical_data_only,
            parameter3=verbose,
            parameter4=quick_scan,
            parameter5=which_field,
            parameter6=what_value
        )
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_CHANGED_PATIENTS)
        return result

    def get_patients_locations(self, patient_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        doc_xml = "<docParams><item name='User' value='@@USER@@'/></docParams>"
        doc_xml = doc_xml.replace("@@USER@@", str(patient_id))
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_PATIENT_LOCATIONS,
            parameter1=doc_xml)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_PATIENT_LOCATIONS)
        return result

    def get_patient_pharmacies(self, patient_id,
                               patients_favorite_only='N'):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_PATIENT_PHARAMCIES,
            patient_id=patient_id,
            parameter1=patients_favorite_only)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_PATIENT_PHARAMCIES)
        return result

    def get_user_id(self):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_USER_ID)

        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_USER_ID)
        return result

    def get_provider(self, provider_id, provider_username=''):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_PROVIDER action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_PROVIDER,
            parameter1=provider_id,
            parameter2=provider_username)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_PROVIDER)
        return result

    def get_provider_info(self, sought_user):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_PROVIDER_INFO,
            app_name=self._app_name,
            token=self._token.token,
            parameter1=sought_user)

        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_PROVIDER_INFO)
        return result

    def get_providers(self, security_filter,
                      name_filter='%',
                      only_providers_flag='Y',
                      internal_external='I',
                      ordering_authority='',
                      real_provider='N'):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :param security_filter - This is the EntryCode of the Security_Code_DE dictionary
            for the providers being sought. A list of valid security codes can be obtained from
            GetDictionary on the Security_Code_DE dictionary.
        :param name_filter
        :param only_providers_flag
        :param internal_external
        :param ordering_authority
        :param real_provider
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_PROVIDERS,
            parameter1=security_filter,
            parameter2=name_filter,
            parameter3=only_providers_flag,
            parameter4=internal_external,
            parameter5=ordering_authority,
            parameter6=real_provider)

        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_PROVIDERS)
        return result

    def get_task_list(self, since='', task_types='', task_status=''):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_TASK_LIST action
        :param since - If given a datetime, retrieves only tasks created (or last modified)
            after that date and time. Defaults to 1/1/1900.
        :param task_status - Optional list of pipe-delimited task status names.
            For example, "Active|In Progress|Complete".
        :param task_types - Optional list of pipe-delimited task type names.
            For example, "Sign Note|Verify Result|MedRenewal"
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_TASK_LIST,
            parameter1=since,
            parameter2=task_types,
            parameter3=task_status)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_ENCOUNTER_LIST_FOR_PATIENT)
        return result

    def save_message_from_pat_portal(self, patient_id,
                                     p_vendor_name,
                                     p_message_id,
                                     p_practice_id,
                                     message,
                                     sent_date,
                                     transaction_type
                                     ):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :param
        :param message
        :param sent_date
        :param transaction_type -   type	To register a patient with the portal,
            this should be 'Register Patient Request.'
                Valid types are stored in iHealth_TransCode_DE.
                Approve Online Consultation
                Custom Form Submitted
                Decline Online Consultation
                Deny Patient Registration
                Form Requested
                Health Remiders
                Register Patient
                Register Patient Request
                RenewRx
                Seek Appointment
                Seek Online Consultation
                Send Clinical Document
                Send General Message
                Send Notification Message
                Unregister Patient
        :return: JSON response
        """
        portal_info_xml = '<msg>' + \
                          '<ppvendor value="@@VENDOR@@" />' + \
                          '<ppmsgid value="@@MESSAGEID@@" />' + \
                          '<pppractice value="@@PRACTICE@@" />' + \
                          '</msg>'
        portal_info_xml = portal_info_xml.replace(
            '@@VENDOR@@', p_vendor_name).replace(
            '@@MESSAGEID@@', p_message_id).replace(
            '@@PRACTICE@@', p_practice_id)

        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SAVE_MSG_FROM_PAT_PORTAL,
            patient_id=patient_id,
            parameter1=portal_info_xml,
            parameter2=self._ehr_username,
            parameter3=message,
            parameter4=sent_date,
            parameter5=transaction_type)

        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SAVE_MSG_FROM_PAT_PORTAL)
        return result

    def save_task_comment(self, task_id, task_comment):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SAVE_TASK_COMMENT,
            parameter1=task_id,
            parameter6=task_comment)

        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SAVE_TASK_COMMENT)
        return result

    def get_task(self, patient_id, task_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_TASK,
            patient_id=patient_id,
            parameter1=task_id)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_TASK)
        return result

    def save_task_status(self, task_id,
                         task_action,
                         comment,
                         delegate_id=''):
        """
        invokes TouchWorksMagicConstants.ACTION_SAVE_TASK_STATUS action
        :param task_action - Task action, such as Approve, Complete, or Deny.
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SAVE_TASK_STATUS,
            parameter1=task_id,
            parameter2=task_action,
            parameter3=delegate_id,
            parameter4=comment)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SAVE_TASK_STATUS)
        return result

    def search_task_views(self, user, search_string):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SEARCH_TASK_VIEWS,
            parameter1=user,
            parameter2=search_string)

        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_SEARCH_TASK_VIEWS)
        return result

    def save_task(self, patient_id,
                  task_type,
                  target_user,
                  work_object_id,
                  comments,
                  subject):
        """
        invokes TouchWorksMagicConstants.ACTION_SAVE_TASK action
        :param patient_id
        :param task_type - EntryMnemonic value from IDX_TASK_ACTION_DE. Dictionary
            values can be looked up using the GetDictionary action.
        :param target_user - TargetUser	Pass in the username of the individual who
            will be assigned the task. Typical delegates can be found by calling GetDelegates.
                It is also possible to assign a task to a team by passing in 'Team'+the ID
                of the corresponding team from the Team_DE dictionary.
                The team can be looked up using the GetDictionary action.
                If the LoginUser is the same as the TargetUser, the task will be marked as
                delegated (and therefore no longer available in GetTask for that LoginUser).
        :param work_object_id - The ID of the item to link to the task,
                such as the medication or note ID. If not needed, 0 can be passed instead.
        :param comments - A comment to set for the task.
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_SAVE_TASK,
            patient_id=patient_id,
            parameter1=task_type,
            parameter2=target_user,
            parameter3=work_object_id,
            parameter4=comments,
            parameter5=subject)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_ENCOUNTER_LIST_FOR_PATIENT)
        return result

    def get_task_comments(self, patient_id, task_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_TASK_COMMENTS,
            patient_id=patient_id,
            parameter1=task_id)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_TASK_COMMENTS)
        return result

    def get_delegates(self, patient_id):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_DELEGATES,
            app_name=self._app_name,
            token=self._token.token,
            patient_id=patient_id)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_DELEGATES)
        return result

    def get_task_list_by_view(self, patient_id, task_view_id, org_id=''):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_ENCOUNTER_LIST_FOR_PATIENT action
        :return: JSON response
        """
        magic = self._magic_json(
            action=TouchWorksMagicConstants.ACTION_GET_TASKLIST_BY_VIEW,
            patient_id=patient_id,
            parameter1=task_view_id,
            parameter2=org_id)
        response = self._http_request(TouchWorksEndPoints.MAGIC_JSON, data=magic)
        result = self._get_results_or_raise_if_magic_invalid(
            magic,
            response,
            TouchWorksMagicConstants.RESULT_GET_TASKLISTBY_VIEW)
        return result

    def get_schedule(self, ehr_username, start_date,
                     changed_since, include_pix, other_user='All',
                     end_date='',
                     appointment_types=None, status_filter='All'):
        """
        invokes TouchWorksMagicConstants.ACTION_GET_SCHEDULE action
        :return: JSON response
        """
        if not start_date:
            raise ValueError('start_date can not be null')
        if end_date:
            start_date = '%s|%s' % (start_date, end_date)
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
