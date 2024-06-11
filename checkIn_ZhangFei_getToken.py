'''
new Env('暂时不能用-掌上飞车扫码登陆')
cron: 1 1 1 1 1
                       _oo0oo_
                      o8888888o
                      88" . "88
                      (| -_- |)
                      0\  =  /0
                    ___/`---'\___
                  .' \\|     |// '.
                 / \\|||  :  |||// \
                / _||||| -:- |||||- \
               |   | \\\  - /// |   |
               | \_|  ''\---/''  |_/ |
               \  .-\__  '-'  ___/-. /
             ___'. .'  /--.--\  `. .'___
          ."" '<  `.___\_<|>_/___.' >' "".
         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
         \  \ `_.   \_ __\ /__ _/   .-` /  /
     =====`-.____`.___ \_____/___.-`___.-'=====
                       `=---='


     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

           佛祖保佑     永不宕机     永无BUG

Author: BNDou
Date: 2024-04-11 22:20:35
LastEditTime: 2024-06-12 00:15:29
FilePath: \Auto_Check_In\checkIn_ZhangFei_getToken.py
Description: 
'''

import io
import re
import time

import qrcode
import requests
from PIL import Image
from pyzbar.pyzbar import decode


def get_auth_token(t):
    """官方算法：根据supertoken计算auth_token"""
    e, r = 0, len(t)
    for n in range(r):
        e = 33 * e + ord(t[n])
    return e % 4294967296


def get_ptqrtoken(t):
    """官方算法：根据qrsig计算ptqrtoken"""
    e, r = 0, len(t)
    for n in range(r):
        e += (e << 5) + ord(t[n])
    return 2147483647 & e


if __name__ == "__main__":
    # 1、获取需要扫码的图片并切获取qrsig
    url = "https://xui.ptlogin2.qq.com/ssl/ptqrshow?daid=381&appid=716027609&pt_3rd_aid=1105330667"
    res_qr = requests.get(url)
    qrsig = res_qr.cookies.get('qrsig')
    # print("\nqrsig =", qrsig)

    # 打印二维码
    barcode_url = ''
    barcodes = decode(Image.open(io.BytesIO(res_qr.content)))
    for barcode in barcodes:
        barcode_url = barcode.data.decode("utf-8")

    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=2)
    qr.add_data(barcode_url)
    qr.make(fit=True)
    # invert=True白底黑块
    qr.print_ascii(invert=True)

    # 2、获取ptqrtoken
    ptqrtoken = get_ptqrtoken(qrsig)
    # print("ptqrtoken =", ptqrtoken)

    # 3、监控用户是否扫成功
    while (True):
        params = {
            "ptqrtoken": ptqrtoken,
            "u1": "http://connect.qq.com",
            "from_ui": "1",
            "daid": "381",
            "aid": "716027609",
            "pt_3rd_aid": "1105330667",
            "pt_openlogin_data": "refer_cgi%3Dm_authorize%26response_type%3Dtoken%26client_id%3D1105330667%26redirect_uri%3Dauth%253A%252F%252Ftauth.qq.com%252F%26",
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"https://xui.ptlogin2.qq.com/ssl/ptqrlogin?{query_string}"
        res_login = requests.get(
            url=url,
            headers={
                'Cookie':
                '; '.join([
                    f'{key}={value}'
                    for key, value in res_qr.cookies.get_dict().items()
                ])
            })
        print(res_login.text)
        if "登录成功" in res_login.text:
            # 4、提取 openid appid access_token
            openid = re.search(r"openid=(\w+)", res_login.text).group(1)
            appid = re.search(r"appid=(\w+)", res_login.text).group(1)
            access_token = re.search(r"access_token=(\w+)",
                                     res_login.text).group(1)
            print(
                f"\nopenid = {openid}\nappid = {appid}\naccess_token = {access_token}"
            )
            break
        # 两秒循环检测
        time.sleep(2)
