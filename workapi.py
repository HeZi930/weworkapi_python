#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, request, abort
from xml.dom.minidom import parseString
import threading
import time
import os
import sys
import logging
from typing import Tuple, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保log目录存在
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'qywx.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加当前目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入企业微信相关模块
from callback.WXBizMsgCrypt3 import WXBizMsgCrypt

app = Flask(__name__)

# 从环境变量获取配置
CORP_ID = os.getenv('CORP_ID')
SUITE_TOKEN = os.getenv('SUITE_TOKEN')
SUITE_ENCODING_AES_KEY = os.getenv('SUITE_ENCODING_AES_KEY')

# 初始化企业微信API实例
qy_api = [
    WXBizMsgCrypt(SUITE_TOKEN, SUITE_ENCODING_AES_KEY, CORP_ID),
]

def process_message(name: str, content: str, channel: int, msg_type: int) -> None:
    """处理接收到的消息"""
    try:
        cmd = f"python3 command.py '{name}' '{content}' '{channel}' '{msg_type}'"
        threading.Thread(target=lambda: os.system(cmd)).start()
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def parse_xml_message(xml_content: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """解析XML消息内容"""
    try:
        doc = parseString(xml_content)
        collection = doc.documentElement
        
        name = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data
        msg_type = collection.getElementsByTagName("MsgType")[0].childNodes[0].data
        content = None
        pic_url = None
        
        if msg_type == "text":
            content = collection.getElementsByTagName("Content")[0].childNodes[0].data
        elif msg_type == "image":
            pic_url = collection.getElementsByTagName("PicUrl")[0].childNodes[0].data
            
        return name, content, pic_url, msg_type
    except Exception as e:
        logger.error(f"Error parsing XML: {e}")
        return None, None, None, None

@app.route('/hook_path', methods=['GET', 'POST'])
def webhook():
    """处理企业微信回调请求"""
    if request.method == 'GET':
        return verify_url(request)
    elif request.method == 'POST':
        return handle_message(request)
    return abort(405)

def verify_url(request) -> str:
    """验证URL有效性"""
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')
    
    ret, sEchoStr = qy_api[0].VerifyURL(msg_signature, timestamp, nonce, echo_str)
    if ret != 0:
        logger.error(f"URL verification failed with ret: {ret}")
        return "failed"
    return sEchoStr

def handle_message(request) -> str:
    """处理接收到的消息"""
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    data = request.data.decode('utf-8')
    
    ret, sMsg = qy_api[0].DecryptMsg(data, msg_signature, timestamp, nonce)
    if ret != 0:
        logger.error(f"Message decryption failed with ret: {ret}")
        return "failed"
    
    name, content, pic_url, msg_type = parse_xml_message(sMsg)
    if not name:
        return "failed"
    
    # 记录日志
    if msg_type == "text":
        logger.info(f"[ch0] {name}: {content}")
        process_message(name, content, 0, 0)
    elif msg_type == "image":
        logger.info(f"[ch0] {name}: 图片消息")
        process_message(name, pic_url, 0, 1)
    
    return "ok"

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 8066))
    ssl_context = None
    
    # 检查SSL证书和密钥文件是否存在
    cert_path = os.getenv('SSL_CERT_PATH')
    key_path = os.getenv('SSL_KEY_PATH')
    
    if cert_path and key_path and os.path.exists(cert_path) and os.path.exists(key_path):
        ssl_context = (cert_path, key_path)
        logger.info(f"Using SSL with certificate: {cert_path} and key: {key_path}")
    else:
        logger.warning("SSL certificate or key not found. Running in HTTP mode.")
        logger.warning("For production use, please set SSL_CERT_PATH and SSL_KEY_PATH in .env file.")
    
    app.run("0.0.0.0", port, ssl_context=ssl_context)