#破解b站滑块验证码

###所需下载库
1.bs4
2.requests

###使用前提
1.需有chrome<br>
2.下载chrome浏览器驱动


###使用方法
1.在        ```
line20 self.brower=webdriver.Chrome(r"xxxxxx")   #本地浏览器驱动所在位置  
```
设置下载好的浏览器驱动<br>
2.在```
line299   crack=Crack('用户名','密码')   
```输入用户名密码<br>
3.启动脚本


###注意事项
*本脚本算法未优化，故登陆成功率不高