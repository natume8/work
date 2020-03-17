import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import random as rand
from operator import itemgetter
import copy

# giftBox用の座標をいじるクラスです
class Dot():
    def __init__(self, a, b):
        self.x = a
        self.y = b

    def rot(self, cx, cy, theta):
        self.x -= cx
        self.y -= cy
        self.xp = self.x * np.cos(theta) - self.y * np.sin(theta)
        self.yp = self.x * np.sin(theta) + self.y * np.cos(theta)
        self.x = self.xp + cx
        self.y = self.yp + cy

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def copy(self):
        result = Dot(self.x, self.y)
        return result

    def reflect(self, d1, d2):
        hoge = self.copy()

        hoge.move(-d1.x, -d1.y)
        d3 = d2.copy()
        d3.move(-d1.x, -d1.y)

        if d3.y == 0:
            theta = 0
        elif d3.x != 0:
            theta = np.arctan2(d3.y, d3.x)
        else:
            theta = np.pi / 2

        x = hoge.x * np.cos(2 * theta) + hoge.y * np.sin(2 * theta)
        y = hoge.x * np.sin(2 * theta) - hoge.y * np.cos(2 * theta)
        result = Dot(x, y)
        result.move(d1.x, d1.y)
        return result


class StripeSegment():#ただの多角形
    def __init__(self):
        self.dots = []

    def append(self, a):  # aはdot
        self.dots.append(a)

    def reflect(self, d1, d2):  # aはseg,d1,d2はdot
        # d1,d2を結ぶ線を中心にaを鏡映に写す。
        result = StripeSegment()
        for hoge in self.get():
            _dot = hoge.reflect(d1, d2)
            result.append(_dot)
        return result

    def sort(self):
        thetas = []
        decoi = copy.deepcopy(self.dots)
        avg=Dot(0,0)

        for hoge in decoi:
            avg.x += hoge.x
            avg.y += hoge.y
        avg.x /= len(decoi)
        avg.y /= len(decoi)

        for hoge in decoi:
            hoge.x -= avg.x
            hoge.y -= avg.y

        for hoge in decoi:
            thetas.append(np.arctan2(hoge.y,hoge.x))

        #print("dots:")
        #for hoge in self.dots:
        #    print(hoge.x,hoge.y)

        self.dots = [list(x) for x in zip(*sorted(zip(self.dots, thetas), key=itemgetter(1)))][0]
        # for hoge in self.dots:
        #     print(hoge.x,hoge.y)
            #print(np.arctan2(hoge.y,hoge.x))

    def haveVertical(self,verticalX,th):
        count = 0
        for dot in self.dots:
            if dot.y < th:
                break
            if dot.x == verticalX:
                count+=1
        if count >= 2: 
            return True
        else: 
            return False

    def getVertical(self,verticalX,th):
        result = []
        for dot in self.dots:
            if dot.y < th:
                break
            if dot.x == verticalX:
                result.append(dot.y)
        return result

    def haveHorizon(self,horizonY,th):
        count = 0
        for dot in self.dots:
            if dot.x < th:
                break
            if dot.y == horizonY:
                count+=1
        if count >= 2: 
            return True
        else: 
            return False
    def getHorizon(self,horizonY,th):
        result = []
        for dot in self.dots:
            if dot.x < th:
                break
            if dot.y == horizonY:
                result.append(dot.x)
        return result

    def get(self):
        return self.dots
    def len(self):
        return len(self.dots)
    def reverse(self):
        self.dots.reverse()
    def clear(self):
        self.dots.clear()


class Stripe():
    def __init__(self):
        self.segments = []
        self.segments.clear()
        self.r = 0
        self.g = 0
        self.b = 0

    def append(self, a):  # aはstripesegment
        self.segments.append(a)

    def setcolor(self, _r, _g, _b):
        self.r = _r
        self.g = _g
        self.b = _b

    def get(self):
        return self.segments

class GiftBox():
    # 入力された3つの数は大きさでソートしなおします
    def __init__(self, a, b, c):
        self.dots_to_render = []
        [self.num1, self.num2, self.num3] = reversed(sorted([a, b, c]))
        # print("三辺の長さ:")
        # print(self.num1,self.num2,self.num3)

        self.alpha = self.beta = self.gamma = self.num3 / 2

    # 描画っぽい形式に直します。今はmatplotで確認しています
    def render(self, theta):
        decoi = Dot(0, 0)
        self.dots_to_render = [decoi]
        decoi = Dot(0, self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2, self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(0, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + self.num3, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + self.num3, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2 + self.num3, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2 + self.num3, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + self.num3, -self.num1 - self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2 + self.num3, -self.num1 - self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + 2 * self.num3, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + 2 * self.num3, -self.num1)
        self.dots_to_render.append(decoi)

        # thetaを元にu,vを算出する
        # 条件式：
        # print("ゆとり")
        # print(self.alpha)
        self.P = 2 * self.num1 - 2 * self.num2 * np.tan(theta) + (1 - np.tan(theta)) * self.num3 + self.beta
        self.Q = self.P - self.num3 * np.tan(theta)
        self.l2 = self.Q / 2
        self.w = (self.l2 + self.num3) * np.sin(theta)
        self.h = self.P * np.cos(theta)
        # print("uv座標")
        # print(self.w,self.h)

        for hoge in self.dots_to_render:
            hoge.rot(0, 0, theta)
            hoge.move(self.w, self.h)

        """plt.figure(figsize=(5, 5))
        g = plt.subplot()
        g.set_ylim([-20, 300])
        g.set_xlim([-20, 300])
        for hoge in dots_to_render:
            g.plot(hoge.x, hoge.y, marker='o')
        plt.show()
        plt.savefig("hoge.png")"""

    # 渡されたtheteが許容できるか返す
    def isValidThete(self, theta):
        self.P = 2 * self.num1 - 2 * self.num2 * np.tan(theta) + (1 - np.tan(theta)) * self.num3 + self.beta
        self.Q = self.P - self.num3 * np.tan(theta)
        self.l2 = self.Q / 2
        if not (np.tan(theta) < self.num1 / self.num2): return False
        if not (np.tan(theta) > (self.num1 + self.num3 + self.beta) / (2 * self.num2 + self.num3)): return False
        if not (self.P - (self.num3 + self.l2 + self.P) * np.sin(theta) * np.sin(theta) > 0): return False
        return True

    # 最小用紙サイズを返す
    def getValidPaperSize(self, theta):
        self.P = 2 * self.num1 - 2 * self.num2 * np.tan(theta) + (1 - np.tan(theta)) * self.num3 + self.beta
        self.Q = self.P - self.num3 * np.tan(theta)
        self.l2 = self.Q / 2
        self.H = (2 * self.num2 + 2 * self.num3) * np.sin(theta) + self.P * np.cos(theta) + self.gamma * np.sin(theta)
        self.W = max(
            (self.num1 + self.num3 + self.l2) * np.sin(theta) + (2 * self.num2 + 2 * self.num3) * np.cos(
                theta) + self.alpha,
            (2 * self.num1 - self.num2 * np.tan(theta) + 2 * self.num3 + self.l2 + self.beta) * np.sin(theta) + (
                        self.num2 + self.num3) * np.cos(theta) + self.alpha
        )
        # print("最小用紙サイズ")
        # print(self.W,self.H)
        return (self.W, self.H)

    def getOptimalTheta(self):
        values = []
        for i in range(900):
            angle = i / 10 / 180 * np.pi
            if self.isValidThete(angle):
                # print(i/10)
                # print(self.getValidPaperSize(i/10 /180*np.pi))
                minimum_ps = self.getValidPaperSize(angle)
                values.append([minimum_ps[0] * minimum_ps[1], i, minimum_ps])

        #print(min(values)[2])
        return min(values)[1] / 10

    def drawStripe(self, s, u, offset, theta2, theta1):
        decoi = Dot(0, 0)
        self.dots_to_render = [decoi]
        decoi = Dot(0, self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2, self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(0, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + self.num3, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + self.num3, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2 + self.num3, -self.num1)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2 + self.num3, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + self.num3, -self.num1 - self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(self.num2 + self.num3, -self.num1 - self.num3)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + 2 * self.num3, 0)
        self.dots_to_render.append(decoi)
        decoi = Dot(2 * self.num2 + 2 * self.num3, -self.num1)
        self.dots_to_render.append(decoi)

        self.P = 2 * self.num1 - 2 * self.num2 * np.tan(theta1) + (1 - np.tan(theta1)) * self.num3 + self.beta
        self.Q = self.P - self.num3 * np.tan(theta1)
        self.l2 = self.Q / 2
        self.w = (self.l2 + self.num3) * np.sin(theta1)
        self.h = self.P * np.cos(theta1)

        plt.figure(figsize=(5, 5))
        g = plt.subplot()
        g.set_ylim([-150, 350])
        g.set_xlim([-150, 350])

        self.result = [] ########### selfつけました

        dist = offset
        isBottomLine = False
        isUpSide = False
        isLeftSide = False
        judge = [self.num1**2 + self.num2**2,self.num1**2 + self.num2**2]
        #while dist < (self.num1*np.cos(theta2)+self.num2*np.cos(theta2)):#描画範囲内
        while judge[1] <= judge[0] :
            judge[0] = judge[1]
            judge[1] = (self.num2 - dist*np.sin(theta2))**2 + (self.num1 - dist*np.cos(theta2))**2
            if(isBottomLine == False):
                _stripe = Stripe()
                _seg = StripeSegment()

            if(dist == 0):
                _dot = Dot(0,0)
                _seg.append(_dot)
                dist += s
                isBottomLine = True
                continue

            if (np.tan(theta2)*dist*np.sin(theta2)+dist*np.cos(theta2))/np.tan(theta2) < self.num2:
                isUpSide = True
                #上辺に接している
                _dot = Dot((np.tan(theta2)*dist*np.sin(theta2)+dist*np.cos(theta2))/np.tan(theta2),0)
                _seg.append(_dot)
            else:
                #右辺に接している
                if np.tan(theta2)*self.num2-np.tan(theta2)*dist*np.sin(theta2)-dist*np.cos(theta2) < -self.num1:#下に溢れたら
                    _dot = Dot(self.num2,-self.num1)
                    _seg.append(_dot)
                    break
                else:
                    _dot = Dot(self.num2,np.tan(theta2)*self.num2-np.tan(theta2)*dist*np.sin(theta2)-dist*np.cos(theta2))
                    _seg.append(_dot)
                if(isUpSide == True & isBottomLine == True):#点が増えるパターン
                    _dot = Dot(self.num2,0)
                    _seg.append(_dot)
                isUpSide = False

            if (-np.tan(theta2)*dist*np.sin(theta2)-dist*np.cos(theta2)) > -self.num1:
                isLeftSide = True
                #左辺に接している
                _dot = Dot(0,-np.tan(theta2)*dist*np.sin(theta2)-dist*np.cos(theta2))
                _seg.append(_dot)
            else:
                #下辺に接している
                if (-self.num1+np.tan(theta2)*dist*np.sin(theta2)+dist*np.cos(theta2))/np.tan(theta2) > self.num2:
                    _dot = Dot(self.num2,-self.num1)
                    _seg.append(_dot)
                    break
                else:
                    _dot = Dot((-self.num1+np.tan(theta2)*dist*np.sin(theta2)+dist*np.cos(theta2))/np.tan(theta2),-self.num1)
                    _seg.append(_dot)
                if(isLeftSide == True & isBottomLine == True):#点が増えるパターン
                    _dot = Dot(0,-self.num1)
                    _seg.append(_dot)
                isLeftSide = False

            if(isBottomLine == True):
                #メイン面についてのみ作る
                _stripe.append(_seg)
                _stripe.setcolor(rand.randint(0,255),rand.randint(0,255),rand.randint(0,255))
                self.result.append(_stripe)

            if(isBottomLine == False): dist += s
            else: dist += u
            isBottomLine = not isBottomLine

        #メイン面を元に他の面を作る
        provisResult = []
        for aaa in self.result:
            for hoge in aaa.get():
                _seg1 = hoge.reflect(Dot(-self.num3/2,0),Dot(-self.num3/2,-self.num1))#左に鏡映
                provisResult.append(_seg1)
                _seg2 = hoge.reflect(Dot(0,-(self.num1*2+self.num3)/2),Dot(self.num2,-(self.num1*2+self.num3)/2))#右下に鏡映
                provisResult.append(_seg2)
                _seg3 = hoge.reflect(Dot((self.num2*2+self.num3)/2,0),Dot((self.num2*2+self.num3)/2,-self.num1))#右に鏡映
                provisResult.append(_seg3)
            for hoge in provisResult:
                aaa.append(hoge)
            provisResult.clear()
        
        #側面について追加
        for aaa in self.result:
            for hoge in aaa.get():
                #meinの左
                if hoge.haveVertical(0,-self.num1):
                    _seg1 = StripeSegment()
                    _dot = Dot(0,hoge.getVertical(0,-self.num1)[0])
                    _seg1.append(_dot)
                    _dot = Dot(0,hoge.getVertical(0,-self.num1)[1])
                    _seg1.append(_dot)
                    _dot = Dot(0,hoge.getVertical(0,-self.num1)[0])
                    _dot.move(-self.num3,0)
                    _seg1.append(_dot)
                    _dot = Dot(0,hoge.getVertical(0,-self.num1)[1])
                    _dot.move(-self.num3,0)
                    _seg1.append(_dot)
                    provisResult.append(_seg1)
                    
                #メインの左上(上に作ってから鏡映)
                if hoge.haveHorizon(0,-self.num2):
                    _seg2 = StripeSegment()
                    _dot = Dot(hoge.getHorizon(0,-self.num2)[0],0)
                    _seg2.append(_dot)
                    _dot = Dot(hoge.getHorizon(0,-self.num2)[1],0)
                    _seg2.append(_dot)
                    _dot = Dot(hoge.getHorizon(0,-self.num2)[0],0)
                    _dot.move(0,self.num3)
                    _seg2.append(_dot)
                    _dot = Dot(hoge.getHorizon(0,-self.num2)[1],0)
                    _dot.move(0,self.num3)
                    _seg2.append(_dot)
                    provisResult.append(_seg2.reflect(Dot(-self.num3/2,0),Dot(-self.num3/2,self.num2)))

                #メインの右
                if hoge.haveVertical(self.num2,-self.num1):
                    _seg3 = StripeSegment()
                    _dot = Dot(self.num2,hoge.getVertical(self.num2,-self.num1)[0])
                    _seg3.append(_dot)
                    _dot = Dot(self.num2,hoge.getVertical(self.num2,-self.num1)[1])
                    _seg3.append(_dot)
                    _dot = Dot(self.num2,hoge.getVertical(self.num2,-self.num1)[0])
                    _dot.move(self.num3,0)
                    _seg3.append(_dot)
                    _dot = Dot(self.num2,hoge.getVertical(self.num2,-self.num1)[1])
                    _dot.move(self.num3,0)
                    _seg3.append(_dot)
                    provisResult.append(_seg3)

                #メインの下
                if hoge.haveHorizon(-self.num1,-self.num2):
                    _seg4 = StripeSegment()
                    _dot = Dot(hoge.getHorizon(-self.num1,-self.num2)[0],-self.num1)
                    _seg4.append(_dot)
                    _dot = Dot(hoge.getHorizon(-self.num1,-self.num2)[1],-self.num1)
                    _seg4.append(_dot)
                    _dot = Dot(hoge.getHorizon(-self.num1,-self.num2)[0],-self.num1)
                    _dot.move(0,-self.num3)
                    _seg4.append(_dot)
                    _dot = Dot(hoge.getHorizon(-self.num1,-self.num2)[1],-self.num1)
                    _dot.move(0,-self.num3)
                    _seg4.append(_dot)
                    provisResult.append(_seg4)

            for hoge in provisResult:
                aaa.append(hoge)
            provisResult.clear()

        for hoge in self.dots_to_render:
            hoge.rot(0, 0, theta1)
            hoge.move(self.w, self.h)
            g.plot(hoge.x, hoge.y, marker='*')

        for aaa in self.result:
            print("STRIPE:have color")
            #print(aaa.r,aaa.g,aaa.b)
            for hogehoge in aaa.get():
                hogehoge.sort()
                print("STRIPESEGMENT:have",hogehoge.len(), "dots")
                for hoge in hogehoge.get():
                    hoge.move(self.num2 + self.num3, 0)
                    hoge.rot(0, 0, theta1)
                    hoge.move(self.w, self.h)
                    g.plot(hoge.x, hoge.y, marker='o', color=[aaa.r / 255, aaa.g / 255, aaa.b / 255])                    

        #plt.show()
        #plt.savefig("hoge.png")


if __name__ == '__main__':
    #print(np.arctan2(np.pi/2))
    # 引数の3数は大きさです。順番は内部でソートします
    #test = GiftBox(100, 60, 30)
    #test = GiftBox(20,25,30)
    test = GiftBox(100,120,150)
    # test.getValidPaperSize(np.pi/4)

    # print(test.getOptimalTheta())

    # print("許容角度")
    # for i in range(900):
    #     if test.isValidThete(i/10 /180*np.pi): print(i/10)
    #     print(np.arctan(i/10 /180*np.pi))

    # 線の幅、線の間、オフセット、箱に対するストライプの角度、箱の角度の順です
    # test.drawStripe(5,4,5, np.pi / 4, np.pi / 4)
    #test.drawStripe(5,4,5, np.pi / 2, np.pi / 4)
    test.drawStripe(10,10,0,np.pi/4,np.pi/4)

    # dots = StripeSegment()
    # dot = Dot(0,0)
    # dots.append(dot)
    # dot = Dot(10,10)
    # dots.append(dot)
    # dot = Dot(5,0)
    # dots.append(dot)
    # dot = Dot(0,5)
    # dots.append(dot)
    # dot = Dot(3,7)
    # dots.append(dot)
    # dots.sort()
    
