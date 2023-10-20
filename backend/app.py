import configparser

# 创建配置解析器对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('./config/apiKeyConfig.ini')

# 获取API参数
secret_key = config.get('API', 'secret_key')
appid  = config.get('API', 'appid')

# 打印训练数据集路径
# print(secret_key,appid)

from flask import Flask, request, jsonify

app = Flask(__name__)

# ... 其他代码 ...

@app.route('/process', methods=['POST','GET'])
def process():
    data = request.json  # 获取请求中的JSON数据，包含待处理的文件信息

    # 在这里执行处理的代码
    text = '******'


    response = {
        'processResult': text
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

