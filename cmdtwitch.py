import obspython, threading, time, json, webbrowser, subprocess, copy
from urllib import request, parse
from http import server

clientID='0q28kbk2ovz7ovd16sggfqhp545u6p'

def apiCall(requestInfo):
    from urllib.error import HTTPError
    from sys import stderr
    try:
        #print(vars(requestInfo))
        response=request.urlopen(requestInfo).read()
        if(len(response)==0):
            return True
        response=json.loads(response)
        #print(response)
        return response
    except HTTPError as error:
        if(error.code==401):
            return get_token()
        stderr.write(vars(requestInfo)+'\n')
        stderr.write(error.read().decode()+'\n')
        raise error

def addRedeem(command):
    from os.path import basename
    url='https://api.twitch.tv/helix/channel_points/custom_rewards?'+parse.urlencode({
        'broadcaster_id':data['broadcaster_id']
    })
    headers=copy.deepcopy(data['auth_headers'])
    headers['Content-Type']='application/json'
    requestInfo=request.Request(
        url,
        data=json.dumps({
            'title':basename(command),
            'cost':100,
            'is_enabled':False
        }).encode(),
        headers=headers,
        method='POST'
    )
    response=apiCall(requestInfo)['data'][0]
    data['redeems'].append({
        'reward_id':response['id'],
        'cursor':''
    })
    script_save(obs_settings)
    webbrowser.open('https://dashboard.twitch.tv/viewer-rewards/channel-points/rewards')

def delRedeem(index):
    url='https://api.twitch.tv/helix/channel_points/custom_rewards?'+parse.urlencode({
        'broadcaster_id':data['broadcaster_id'],
        'id':data['redeems'][index]['reward_id']
    })
    del data['redeems'][index]
    script_save(obs_settings)
    requestInfo=request.Request(url,headers=data['auth_headers'],method='DELETE')
    apiCall(requestInfo)

def main():
    while True:
        for redeem in data['redeems']:
            try:
                url='https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions?'+parse.urlencode({
                    'broadcaster_id':data['broadcaster_id'],
                    'reward_id':redeem['reward_id'],
                    'after':redeem['cursor'],
                    'status':'UNFULFILLED',
                    'first':1
                })
                requestInfo=request.Request(url,headers=data['auth_headers'])
                response=apiCall(requestInfo)
                redeem['cursor']=response['pagination']['cursor']
                index=data['redeems'].index(redeem)
                command=data['commands'][index]['value']
                command=command.replace('$USER_INPUT',response['data'][0]['user_input'])
                print(command)
                from os.path import dirname
                subprocess.Popen(command,cwd=dirname(command))
            except KeyError:
                pass
            except:
                import traceback
                traceback.print_exc()
        time.sleep(1)

def get_token():
    global httpThread
    class OAuthRequestHandler(server.BaseHTTPRequestHandler):
        def log_request(*args, **kwargs):
            pass
        def do_GET(self):
            from urllib.parse import urlparse, parse_qs
            self.send_response(200)
            self.end_headers()
            self.wfile.write('<script>close();</script>'.encode())
            self.wfile.close()
            data['token']=parse_qs(urlparse(self.path).query)['access_token'][0]
            data['auth_headers']={
                'Authorization':'Bearer '+data['token'],
                'Client-Id': clientID
            }
            requestInfo=request.Request('https://api.twitch.tv/helix/users?',headers=data['auth_headers'])
            response=apiCall(requestInfo)['data'][0]
            data['broadcaster_id']=response['id']
            script_save(obs_settings)
            start()
            self.server.shutdown()
    httpServer=server.HTTPServer(('localhost',2000), OAuthRequestHandler)
    httpThread=threading.Thread(target=httpServer.serve_forever)
    httpThread.daemon=True
    httpThread.start()
    url='https://id.twitch.tv/oauth2/authorize?'+parse.urlencode(
        {
            'client_id':clientID,
            'redirect_uri':'https://sugoidogo.github.io/cmdtwitch3/auth.html',
            'response_type':'token',
            'scope':'channel:manage:redemptions channel:read:redemptions'
        }
    )
    webbrowser.open(url)

def start():
    global mainThread
    mainThread=threading.Thread(target=main)
    mainThread.daemon=True
    mainThread.start()

def script_defaults(settings):
    defaults=obspython.obs_data_create_from_json(json.dumps({
        'token':'',
        'broadcaster_id':'',
        'commands':[],
        'redeems':[]
    }))
    obspython.obs_data_apply(defaults,settings)
    obspython.obs_data_apply(settings,defaults)

def script_description():
    return "run commands for twitch redeems"

def script_load(settings):
    global data, obs_settings
    obs_settings=settings
    data=json.loads(obspython.obs_data_get_json(settings))
    if(data['broadcaster_id']==''):
        get_token()
    else:
        start()

def script_save(settings):
    save=obspython.obs_data_create_from_json(json.dumps(data))
    obspython.obs_data_apply(settings,save)

def on_commands_modified(props, property, settings):
    try:
        commands=json.loads(obspython.obs_data_get_json(settings))['commands']
        if(len(commands)==len(data['commands'])):
            script_save(obs_settings)
            return True
        if(len(commands)>len(data['commands'])):
            data['commands']=commands
            addRedeem(data['commands'][-1]['value'])
            return False
        if(len(commands)<len(data['commands'])):
            index=0
            while True:
                if(len(commands)==index or commands[index]!=data['commands'][index]):
                    data['commands']=commands
                    delRedeem(index)
                    return False
                index+=1
    except KeyError:
        pass

def script_properties():
    properties=obspython.obs_properties_create()
    commands=obspython.obs_properties_add_editable_list(properties,'commands','commands',obspython.OBS_EDITABLE_LIST_TYPE_FILES_AND_URLS,None,None)
    obspython.obs_property_set_modified_callback(commands,on_commands_modified)
    return properties

def script_unload():
    global data, obs_settings
    data=None
    obs_settings=None
    try:
        mainThread._stop()
        httpThread._stop()
    except:
        pass