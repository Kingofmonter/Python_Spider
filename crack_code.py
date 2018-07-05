import time,random
import PIL.Image as image
import requests,json,re,urllib
from PIL import Image
from io import BytesIO
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver


class Crack():
    def __init__(self,username,password):

        self.url="https://passport.bilibili.com/login"                                                              #网址
        self.brower=webdriver.Chrome(r"C:\Users\Administrator\Downloads\chromedriver_win32\chromedriver.exe")   #浏览器驱动所在位置
        self.wait=WebDriverWait(self.brower,100)
        self.username=username
        self.password=password
        self.BOREDR=6

    def open(self):
        """
        打开浏览器，输入查询内容
        :return:
        """

        self.brower.get(self.url)
        self.brower.maximize_window()
        time.sleep(3)

        username=self.brower.find_element_by_id('login-username')                                                      #用户名id
        password=self.brower.find_element_by_id('login-passwd')                                                         #密码id

        username.send_keys(self.username)
        password.send_keys(self.password)

        ele=self.brower.find_element_by_xpath('//*[@class="gt_slider_knob gt_show"]')

        AC(self.brower).move_to_element(ele).perform()



    def ge_screenshot(self):
        '''
        获取网页截图
        :return:
        '''

        screenshot=self.brower.get_screenshot_as_png()
        screenshot=Image.open(BytesIO(screenshot))

        return screenshot


    def get_images(self,bg_filename='bg,jpg',fullbg_filename='fullbg.jpg'):
        '''
        获取图片验证码
        :param bg_filename:
        :param fullbg_filename:
        :return:
        '''

        bg=[]
        fullbg=[]

        while bg==[] and fullbg==[]:
            bf=BeautifulSoup(self.brower.page_source,'lxml')
            bg=bf.find_all('div',class_='gt_cut_bg_slice')
            fullbg=bf.find_all('div',class_='gt_cut_fullbg_slice')

        bg_url=re.findall('url\(\"(.*)\"\);',bg[0].get('style'))[0].replace('webp','jpg')
        fullbg_url=re.findall('url\(\"(.*)\"\);',fullbg[0].get('style'))[0].replace('webp','jpg')

        bg_location_list=[]
        fullbg_location_list=[]

        for each_bg in bg:
            location ={}
            location['x']=int(re.findall('background-position: (.*)px (.*)px;',each_bg.get('style'))[0][0])
            location['y']=int(re.findall('background-position: (.*)px (.*)px;',each_bg.get('style'))[0][1])
            bg_location_list.append(location)

        for each_fullbg in fullbg:
            location ={}
            location['x']=int(re.findall('background-position: (.*)px (.*)px;',each_fullbg.get('style'))[0][0])
            location['y']=int(re.findall('background-position: (.*)px (.*)px;',each_fullbg.get('style'))[0][1])
            fullbg_location_list.append(location)

        urlretrieve(url=bg_url,filename=bg_filename)
        print('缺口图片下载完成')
        urlretrieve(url=fullbg_url,filename=fullbg_filename)
        print('背景图片下载完成')

        return bg_location_list,fullbg_location_list


    def get_merge_image(self,filename,location_list):
        '''
        根据位置对图片进行合并还原
        :param filename: 图片
        :param location_list: 图片位置
        :return:
        '''

        im=image.open(filename)
        new_im=image.new('RGB',(260,116))
        im_list_upper=[]
        im_list_down=[]

        for location in location_list:
            if location['y']==-58:
                im_list_upper.append(im.crop((abs(location['x']),58,abs(location['x'])+10,166)))
            if location['y']==0:
                im_list_down.append(im.crop((abs(location['x']),0,abs(location['x'])+10,58)))

        new_im=image.new('RGB',(260,116))

        x_offset=0
        for im in im_list_upper:
            new_im.paste(im,(x_offset,0))
            x_offset+=im.size[0]
        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        new_im.save(filename)
        return new_im


    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    def get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        left = 43
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left


    def get_track(self,distance):
        '''
        根据偏移量获取移动轨迹
        :param distance:
        :return:
        '''
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        move=0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        # else:
        #     current += move
        #
        #     track.append(round(-move))
        #
        #
        # if current > distance:
        #
        #     current -= move
        #
        #     track.append(round(move))
        #

        return track

    # def fake_drag(self, knob, offset):
    #
    #     offsets, tracks = easing.get_tracks(offset, 12, 'ease_out_expo')
    #     print(offsets)
    #     AC(self.browser).click_and_hold(knob).perform()
    #     for x in tracks:
    #         AC(self.browser).move_by_offset(x, 0).perform()
    #     AC(self.browser).pause(0.5).release().perform()
    #
    #     return


    def get_slider(self):
        '''
        获取滑块
        :return:
        '''
        while True:
            try:
                slider=self.brower.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                break
            except:
                time.sleep(0.5)
        return slider


    def move_to_gap(self,slider,track):
        '''
        拖动滑块
        :param slider:
        :param track:
        :return:
        '''
        #保持鼠标点击动作
        AC(self.brower).click_and_hold(slider).perform()

        while track:
            x=random.choice(track)
            #移动
            AC(self.brower).move_by_offset(xoffset=x,yoffset=0).perform()
            #删除track中的坐标元素
            track.remove(x)

        time.sleep(0.5)
        #释放鼠标
        AC(self.brower).release().perform()

    def crack(self):

        self.open()

        #保存图片名称
        bg_filename='bg.jpg'
        fullbg_filename='fullbg.jpg'

        #获取图片
        bg_location_list,fullbg_location_list=self.get_images(bg_filename,fullbg_filename)

        #合并还原图片
        bg_img=self.get_merge_image(bg_filename,bg_location_list)
        fullbg_img=self.get_merge_image(fullbg_filename,fullbg_location_list)

        #获取缺口位置
        gap=self.get_gap(fullbg_img,bg_img)
        print('缺口位置',gap)

        track=self.get_track(gap-self.BOREDR)
        print('滑动滑块')
        print(track)

        #点击缺口
        slider=self.get_slider()
        #拖动滑块
        self.move_to_gap(slider,track)


if __name__=='__main__':
    print("start")
    crack=Crack('15158765640','jin630061126')                                                                          #输入用户名密码
    crack.crack()
