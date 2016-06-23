from oauth2gateway import OAuth2Gateway
import os

class Wrike(OAuth2Gateway):
  def __init__(self, data_filepath=None, auth_info=None, wait_for_redirect=False, tokens_updater=None):
    OAuth2Gateway.__init__(self, data_filepath=data_filepath, auth_info=auth_info, tokens_updater=tokens_updater)
    self._host_url = 'https://www.wrike.com/api/v3'
    self._oauth2_url = 'https://www.wrike.com/oauth2/token'
    self._oauth2_authorization_url = 'https://www.wrike.com/oauth2/authorize'
    self._oauth2_client_id = os.environ['WRIKE_CLIENT_ID']
    self._oauth2_client_secret = os.environ['WRIKE_CLIENT_SECRET']
    self._wait_for_redirect = wait_for_redirect == True
    self._api = {
      'get_task': {
        'path': '/tasks/{id}',
        'method': 'GET',
        'translate': [
          {
            'type': 'ApiV2Task',
            'params': ['id']
          }
        ],
        'valid_status': [200, 400]
      },
      'get_task_v2':{
        'path': '/tasks/{id}',
        'method': 'GET',
        'valid_status': [200]
      },
      'id': {
        'path': '/ids',
        'method': 'GET',
        'valid_status': [200]
      },
      'create_comment_in_task_v3': {
        'path': '/tasks/{idv3}/comments',
        'method': 'POST',
        'valid_status': [200]
      },
      'modify_task': {
        'path': '/tasks/{id}',
        'method': 'PUT',
        'translate': [
          {
            'type': 'ApiV2Task',
            'params': ['id']
          }
        ],
        'valid_status': [200]
      },
      'list_folders': {
        'path': '/folders',
        'method': 'GET',
        'valid_status': [200]
      },
      'get_folder': {
        'path': '/folders/{id}',
        'method': 'GET',
        'valid_status': [200]
      },
      'create_task': {
        'path': '/folders/{folderId}/tasks',
        'method': 'POST',
        'valid_status': [200]
      },
      'get_contacts': {
        'path': '/contacts',
        'method': 'GET',
        'valid_status': [200]
      },
      'change_task': {
        'path': '/tasks/{taskId}',
        'method': 'PUT',
        'valid_status': [200]
      }
    }

  def call(self, api, **args):
    if self._api[api].get('translate') is not None:
      for translate in self._api[api]['translate']:
        for param in translate['params']:
          ids = super(Wrike, self).call('id', params={
            'ids': '[{0}]'.format(args[param]),
            'type': translate['type']
          })[0]

          if ids.get('data') is not None and len(ids['data']) > 0:
            args[param] = ids['data'][0]['id']
          else:
            args[param] = None

    return super(Wrike, self).call(api, **args)

  def get_current_contact(self):
    response = self.call('get_contacts', params={'me': True})[0]
    return response['data'][0]

  def get_task(self, task_id):
    response = self.call('get_task', id=task_id)[0]
    if response.get('data') is not None and len(response['data']) > 0:
      return response['data'][0]
    else:
      return None

  def get_task_v2(self, task_v2_id):
    response = self.call('get_task_v2', id=task_v2_id)[0]
    if response.get('data') is not None and len(response['data']) > 0:
      return response['data'][0]
    else:
      return None

  def complete_task(self, task_id):
    response = self.call('modify_task', id=task_id, params={
      'status': 'Completed'
    })[0]
    if response.get('data') is not None and len(response['data']) > 0:
      return response['data'][0]
    else:
      return None

  def list_folders(self):
    response = self.call('list_folders')[0]
    return response.get('data')

  def get_folder(self, folder_id):
    response = self.call('get_folder', id=folder_id)[0]
    if response.get('data') is not None and len(response['data']) > 0:
      return response['data'][0]
    else:
      return None

  def create_task(self, folder_id, title, params={}):
    params.update({'title': title})
    response = self.call('create_task', folderId=folder_id, params=params)[0]
    if response.get('data') is not None and len(response['data']) > 0:
      return response['data'][0]
    else:
      return None

  def create_task_comment(self, task_id_v3, comment):
    response = self.call('create_comment_in_task_v3', idv3=task_id_v3, params={
      'text': comment
    })[0]
    return response['data'][0]

  def change_task(self, task_id_v3, params={}):
    response = self.call('change_task', taskId=task_id_v3, params=params)[0]
    return response['data'][0]
