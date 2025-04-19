# 企业微信API回调处理服务

## 项目介绍

本项目基于[企业微信官方Python SDK](https://github.com/sbzhu/weworkapi_python)进行二次开发，主要针对企业微信消息回调场景进行功能增强和现代化改造。原始项目由腾讯企业微信团队维护。

更多来自个人开发者的其它语言的库推荐：  
ruby ： https://github.com/mycolorway/wework  MyColorway(个人开发者)  
php : https://github.com/sbzhu/weworkapi_php  abelzhu@tencent.com(企业微信团队)  
golang : https://github.com/sbzhu/weworkapi_golang  ryanjelin@tencent.com(企业微信团队)   
golang : https://github.com/doubliekill/EnterpriseWechatSDK  1006401052yh@gmail.com(个人开发者) 


## 功能特点

- 支持企业微信URL验证（配置回调URL时使用）
- 支持接收并解密企业微信消息
- 支持处理文本消息和图片消息
- 消息处理异步执行，不阻塞主服务
- 完整的日志记录系统
- 支持HTTPS安全连接

## 系统要求

- Python 3.9+
- 企业微信企业号账户
- 具备公网IP或域名（用于企业微信回调,也可以通过内网穿透）

## 依赖库

- Flask - Web服务框架
- python-dotenv - 环境变量管理
- pycrypto - 加密库（用于企业微信消息解密）
- xmldom - XML解析

## 安装说明

1. 克隆本仓库到本地
   ```bash
   git clone
   ```


2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 复制配置文件示例并进行配置：
   ```bash
   cp .env.example .env
   ```
4. 编辑`.env`文件，填入您的企业微信配置信息

## 配置说明

在`.env`文件中配置以下参数：

- `CORP_ID` - 企业微信的企业ID
- `CORP_SECRET` - 企业微信的应用密钥
- `SUITE_ID` - 企业微信的应用ID
- `SUITE_TOKEN` - 用于验证消息来源
- `SUITE_ENCODING_AES_KEY` - 用于消息加解密
- `FLASK_PORT` - 服务监听端口
- `SSL_CERT_PATH` - SSL证书路径（可选）
- `SSL_KEY_PATH` - SSL密钥路径（可选）

## 使用方法

1. 启动服务：
   ```
   python workapi.py
   ```

2. 在企业微信管理后台配置回调URL：
   - URL格式：`http(s)://您的域名或IP/hook_path`
   - Token和EncodingAESKey需与`.env`文件中配置一致

3. 测试接收消息：
   - 向配置了回调的应用发送消息
   - 查看日志目录下的`qywx.log`文件确认接收情况


## 文件结构

```
├── callback
│   ├── ierror.py
│   └── WXBizMsgCrypt3.py
├── .env
├── .env.example
├── .gitignore
├── README.md
├── workapi.py
└── requirements.txt
```

## 注意事项

- 生产环境建议使用HTTPS，需配置SSL证书
- 请妥善保管企业微信的敏感配置信息
- 日志文件会记录所有接收到的消息内容

## 致谢

*本项目的开发特别感谢腾讯企业微信团队提供的基础SDK支持*  
*Licensed under [MIT License](./LICENSE)*
