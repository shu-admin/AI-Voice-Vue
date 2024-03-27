#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#   合成小语种需要传输小语种文本、使用小语种发音人vcn、tte=unicode以及修改文本编码方式
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import configparser
import os
from flask import Flask, flash, redirect, request, jsonify, url_for,send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys

import base64
import hashlib
import hmac
import json
import os
import time
from functools import partial
import requests
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os

# print(sys.argv[0])#当前脚本的位置
app = Flask(__name__)
# 配置 CORS，允许来自指定源的请求
CORS(app, resources={r"/process": {"origins": "http://localhost:5173"},r"/text2speech": {"origins": "http://localhost:5173"}})
lfasr_host = 'http://raasr.xfyun.cn/api'

# ... 其他代码 ...
# 创建配置解析器对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('./config/apiKeyConfig.ini')

# 获取API参数
secret_key = config.get('API', 'secret_key')
appid  = config.get('API', 'appid')

# 打印训练数据集路径
# print(secret_key,appid)

UPLOAD_FOLDER = './data/test/'
ALLOWED_EXTENSIONS = {'wav','mp3','mp4'}

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识
  

# 请求的接口名
api_prepare = '/prepare'
api_upload = '/upload'
api_merge = '/merge'
api_get_progress = '/getProgress'
api_get_result = '/getResult'
# 文件分片大小10M
file_piece_sice = 10485760

# ——————————————————转写可配置参数————————————————
# 参数可在官网界面（https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html）查看，根据需求可自行在gene_params方法里添加修改
# 转写类型
lfasr_type = 0
# 是否开启分词
has_participle = 'false'
has_seperate = 'true'
# 多候选词个数
max_alternatives = 0
# 子用户标识
suid = ''

class SliceIdGenerator:
    """slice id生成器"""

    def __init__(self):
        self.__ch = 'aaaaaaaaa`'

    def getNextSliceId(self):
        ch = self.__ch
        j = len(ch) - 1
        while j >= 0:
            cj = ch[j]
            if cj != 'z':
                ch = ch[:j] + chr(ord(cj) + 1) + ch[j + 1:]
                break
            else:
                ch = ch[:j] + 'a' + ch[j + 1:]
                j = j - 1
        self.__ch = ch
        return self.__ch


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path

    # 根据不同的apiname生成不同的参数,本示例中未使用全部参数您可在官网(https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html)查看后选择适合业务场景的进行更换
    def gene_params(self, apiname, taskid=None, slice_id=None):
        appid = self.appid
        secret_key = self.secret_key
        upload_file_path = self.upload_file_path
        ts = str(int(time.time()))
        m2 = hashlib.md5()
        m2.update((appid + ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)
        param_dict = {}

        if apiname == api_prepare:
            # slice_num是指分片数量，如果您使用的音频都是较短音频也可以不分片，直接将slice_num指定为1即可
            slice_num = int(file_len / file_piece_sice) + (0 if (file_len % file_piece_sice == 0) else 1)
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['file_len'] = str(file_len)
            param_dict['file_name'] = file_name
            param_dict['slice_num'] = str(slice_num)
        elif apiname == api_upload:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
            param_dict['slice_id'] = slice_id
        elif apiname == api_merge:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
            param_dict['file_name'] = file_name
        elif apiname == api_get_progress or apiname == api_get_result:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
        return param_dict

    # 请求和结果解析，结果中各个字段的含义可参考：https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html
    def gene_request(self, apiname, data, files=None, headers=None):
        response = requests.post(lfasr_host + apiname, data=data, files=files, headers=headers)
        result = json.loads(response.text)
        if result["ok"] == 0:
            print("{} success:".format(apiname) + str(result))
            return result
        else:
            print("{} error:".format(apiname) + str(result))
            exit(0)
            return result

    # 预处理
    def prepare_request(self):
        return self.gene_request(apiname=api_prepare,
                                 data=self.gene_params(api_prepare))

    # 上传
    def upload_request(self, taskid, upload_file_path):
        file_object = open(upload_file_path, 'rb')
        try:
            index = 1
            sig = SliceIdGenerator()
            while True:
                content = file_object.read(file_piece_sice)
                if not content or len(content) == 0:
                    break
                files = {
                    "filename": self.gene_params(api_upload).get("slice_id"),
                    "content": content
                }
                response = self.gene_request(api_upload,
                                             data=self.gene_params(api_upload, taskid=taskid,
                                                                   slice_id=sig.getNextSliceId()),
                                             files=files)
                if response.get('ok') != 0:
                    # 上传分片失败
                    print('upload slice fail, response: ' + str(response))
                    return False
                print('upload slice ' + str(index) + ' success')
                index += 1
        finally:
            'file index:' + str(file_object.tell())
            file_object.close()
        return True

    # 合并
    def merge_request(self, taskid):
        return self.gene_request(api_merge, data=self.gene_params(api_merge, taskid=taskid))

    # 获取进度
    def get_progress_request(self, taskid):
        return self.gene_request(api_get_progress, data=self.gene_params(api_get_progress, taskid=taskid))

    # 获取结果
    def get_result_request(self, taskid):
        return self.gene_request(api_get_result, data=self.gene_params(api_get_result, taskid=taskid))

    def all_api_request(self):
        # 1. 预处理
        pre_result = self.prepare_request()
        taskid = pre_result["data"]
        # 2 . 分片上传
        self.upload_request(taskid=taskid, upload_file_path=self.upload_file_path)
        # 3 . 文件合并
        self.merge_request(taskid=taskid)
        # 4 . 获取任务进度
        while True:
            # 每隔20秒获取一次任务进度
            progress = self.get_progress_request(taskid)
            progress_dic = progress
            if progress_dic['err_no'] != 0 and progress_dic['err_no'] != 26605:
                print('task error: ' + progress_dic['failed'])
                return
            else:
                data = progress_dic['data']
                task_status = json.loads(data)
                if task_status['status'] == 9:
                    print('task ' + taskid + ' finished')
                    break
                print('The task ' + taskid + ' is in processing, task status: ' + str(data))

            # 每次获取进度间隔20S
            time.sleep(20)
        # 5 . 获取结果
        return self.get_result_request(taskid=taskid)

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text,BusinessArgs):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = BusinessArgs
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

def on_message(ws, message):
    try:
        message = json.loads(message)
        print(message)
        code = message["code"]
        sid = message["sid"]
        status = message.get("data", {}).get("status")
        
        # 初始化audio_bytes为空字节对象
        audio_bytes = b''
        
        if 'audio' in message.get("data", {}):
            audio = message["data"]["audio"]
            audio_bytes = base64.b64decode(audio)  # 解码音频数据
        else:
            print("audio 字段为空或未定义")
        
        if status == 2:
            print("WebSocket连接关闭")
            ws.close()
            
        if code != 0:
            errMsg = message["message"]
            print(f"sid:{sid} 调用错误:{errMsg}, 错误码:{code}")
        else:
            # 确保只有在audio_bytes非空时才尝试写入文件
            if audio_bytes:
                with open('./demo.mp3', 'ab') as f:
                    f.write(audio_bytes)
            else:
                print("没有音频数据可写入")

    except Exception as e:
        print("接收消息时发生解析异常:", e)





# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws,a,b):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws, wsParam):  # 添加wsParam作为参数
    def run(wsParam):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        print("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists('./demo.mp3'):
            os.remove('./demo.mp3')

    thread.start_new_thread(run, (wsParam,))  # 传递wsParam给线程函数

#判断上传文件的后缀名是否符合要求
def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/text2speech', methods=['POST','GET'])
def text2speech():
    if request.method == 'POST':
        print(request.data)
        # 首先，将字节串解码成字符串
        request.data = request.data.decode('utf-8')

        # 然后，使用json.loads()将字符串解析为Python字典
        request.data = json.loads(request.data)
        print(request.data['text'])
        # 测试时候在此处正确填写相关信息即可运行
        wsParam = Ws_Param(APPID='b19de6ba', APISecret='ZDQ5YWViMTk1ODczNzI4ZTQzMGU5NWY5',
                        APIKey='0bf4a4c2e5e0ea0bf8806065511ba428',
                        Text=request.data['text'],
                        BusinessArgs={"aue": request.data['aue'], "auf": "audio/L16;rate=16000","vcn": request.data['vcn'], "sfl":1,"speed": request.data['speed'],"volume": request.data['volume'], "pitch": request.data['pitch'], "tte": "utf8"})
                        # BusinessArgs={"aue": request.data['aue'], "vcn": request.data['vcn'],"speed": request.data['speed'],"sfl":1, "volume": request.data['volume'], "pitch": request.data['pitch'], "tte": "unicode"})
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)

        # 使用 partial 包装 on_open 函数，确保 wsParam 被传递
        ws.on_open = partial(on_open, wsParam=wsParam)


        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        audioUrl = '../demo.mp3'
        # return send_file('../demo.mp3', mimetype='audio/mp3')
        return audioUrl

@app.route('/get_audio')
def get_audio():
    # 假设你的MP3文件存储在服务器上的这个位置
    file_path = '../demo.mp3'
    # send_file会自动读取并发送文件内容
    return send_file(file_path, mimetype='audio/mp3')

@app.route('/process', methods=['POST','GET'])
def process():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        
        if file and allowedFile(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            print(file)
            uploadFileName = UPLOAD_FOLDER + filename
            api = RequestApi(appid="b19de6ba", secret_key="a27ac448ce83674012406ce4a369bf7b", upload_file_path=uploadFileName)
            # api.all_api_request()
            return api.all_api_request()
    # file.save(f"./data/test/{secure_filename(file.filename)}")
    # data = request.json  # 获取请求中的JSON数据，包含待处理的文件信息

    # # 在这里执行处理的代码
    # text = '******'


    # response = {
    #     'processResult': text
    # }

    # return jsonify(response)
    return "hello,world"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

