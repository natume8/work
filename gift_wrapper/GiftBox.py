import numpy as np
import random as rand
from operator import itemgetter
import copy


# giftBox用の座標をいじるクラスです
class Dot:
    def __init__(self, a, b):
        self.x = a
        self.y = b

    def rot(self, cx, cy, theta):
        self.x -= cx
        self.y -= cy
        xp = self.x * np.cos(theta) - self.y * np.sin(theta)
        yp = self.x * np.sin(theta) + self.y * np.cos(theta)
        self.x = xp + cx
        self.y = yp + cy

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def copy(self):
        result = Dot(self.x, self.y)
        return result

    def reflect(self, d1, d2):
        dots_copy = self.copy()

        dots_copy.move(-d1.x, -d1.y)
        d3 = d2.copy()
        d3.move(-d1.x, -d1.y)

        if d3.y == 0:
            theta = 0
        elif d3.x != 0:
            theta = np.arctan2(d3.y, d3.x)
        else:
            theta = np.pi / 2

        x = dots_copy.x * np.cos(2 * theta) + dots_copy.y * np.sin(2 * theta)
        y = dots_copy.x * np.sin(2 * theta) - dots_copy.y * np.cos(2 * theta)
        result = Dot(x, y)
        result.move(d1.x, d1.y)
        return result

    def getl(self):
        return [self.x, self.y]


class StripeSegment:  # ただの多角形
    def __init__(self):
        self.dots = []

    def append(self, a):  # aはdot
        self.dots.append(a)

    def reflect(self, d1, d2):  # aはseg,d1,d2はdot
        # d1,d2を結ぶ線を中心にaを鏡映に写す。
        result = StripeSegment()
        for stripe_dots in self.get():
            _dot = stripe_dots.reflect(d1, d2)
            result.append(_dot)
        return result

    def sort(self):
        thetas = []
        decoi = copy.deepcopy(self.dots)
        avg = Dot(0, 0)

        for e_dot in decoi:
            avg.x += e_dot.x
            avg.y += e_dot.y
        avg.x /= len(decoi)
        avg.y /= len(decoi)

        for e_dot in decoi:
            e_dot.x -= avg.x
            e_dot.y -= avg.y

        for e_dot in decoi:
            thetas.append(np.arctan2(e_dot.y, e_dot.x))

        self.dots = [list(x) for x in zip(
            *sorted(zip(self.dots, thetas), key=itemgetter(1)))][0]

    def have_vertical(self, vertical_x, th):
        count = 0
        for dot in self.dots:
            if dot.y < th:
                break
            if dot.x == vertical_x:
                count += 1
        if count >= 2:
            return True
        else:
            return False

    def get_vertical(self, vertical_x, th):
        result = []
        for dot in self.dots:
            if dot.y < th:
                break
            if dot.x == vertical_x:
                result.append(dot.y)
        return result

    def have_horizon(self, horizon_h, th):
        count = 0
        for dot in self.dots:
            if dot.x < th:
                break
            if dot.y == horizon_h:
                count += 1
        if count >= 2:
            return True
        else:
            return False

    def get_horizon(self, horizon_y, th):
        result = []
        for dot in self.dots:
            if dot.x < th:
                break
            if dot.y == horizon_y:
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


class Stripe:
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


class GiftBox:
    # 入力された3つの数は大きさでソートしなおします
    def __init__(self, a, b, c):
        self.dots_to_render = []
        [self.num1, self.num2, self.num3] = reversed(sorted([a, b, c]))
        # print("三辺の長さ:")
        # print(self.num1,self.num2,self.num3)

        self.alpha = self.beta = self.gamma = self.num3 / 2
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

    def render(self, theta):
        # thetaを元にu,vを算出する
        # 条件式：
        # print("ゆとり")
        # print(self.alpha)
        P = 2 * self.num1 - 2 * self.num2 * \
            np.tan(theta) + (1 - np.tan(theta)) * self.num3 + self.beta
        Q = P - self.num3 * np.tan(theta)
        l2 = Q / 2
        w = (l2 + self.num3) * np.sin(theta)
        h = P * np.cos(theta)
        print("uv座標: ", w, h)
        print("uv座標")
        print(w, h)

        for e_dot in self.dots_to_render:

            e_dot.rot(0, 0, theta)
            e_dot.move(w, h)

    # 渡されたthetaが許容できるか返す
    def is_valid_theta(self, theta):
        p = 2 * self.num1 - 2 * self.num2 * \
            np.tan(theta) + (1 - np.tan(theta)) * self.num3 + self.beta
        q = p - self.num3 * np.tan(theta)
        l2 = q / 2
        s = (self.num3 + l2 + p) * np.sin(theta) * np.sin(theta)
        m = ((self.num2 + self.num3) * np.sin(theta)
             - (self.num1 - self.num2 * np.tan(theta) + self.num3 + self.beta) * np.cos(theta)) \
            * (self.num3 + l2 + p) * np.sin(theta) \
            / (self.num1 - p)
        if not np.tan(theta) < self.num1 / self.num2:
            return False
        elif not np.tan(theta) > (self.num1 + self.num3 + self.beta) / (2 * self.num2 + self.num3):
            return False
        elif not p - s > 0:
            return False
        elif (m - self.num3) < (self.num2 / 4):
            return False
        return True

    # 最小用紙サイズを返す
    def get_valid_paper_size(self, theta):
        p = 2 * self.num1 - 2 * self.num2 * \
            np.tan(theta) + (1 - np.tan(theta)) * self.num3 + self.beta
        q = p - self.num3 * np.tan(theta)
        l2 = q / 2
        paper_height = (2 * self.num2 + 2 * self.num3) * np.sin(theta) + \
            p * np.cos(theta) + self.gamma * np.sin(theta)
        paper_width = max(
            (self.num1 + self.num3 + l2) * np.sin(theta) +
            (2 * self.num2 + 2 * self.num3) * np.cos(theta) + self.alpha,
            (2 * self.num1 - self.num2 * np.tan(theta) +
             2 * self.num3 + l2 + self.beta) * np.sin(theta)
            + (self.num2 + self.num3) * np.cos(theta) + self.alpha
        )
        # print("最小用紙サイズ")
        # print(paper_width,paper_height)
        return paper_width, paper_height

    def get_optimal_theta(self):
        values = []
        for i in range(900):
            angle = i / 10 / 180 * np.pi
            if self.is_valid_theta(angle):
                # print(i/10)
                # print(self.get_valid_paper_size(i/10 /180*np.pi))
                minimum_ps = self.get_valid_paper_size(angle)
                values.append([minimum_ps[0] * minimum_ps[1], i, minimum_ps])

        # print(min(values)[2])
        if not values:
            return None
        return min(values)[1] / 10

    def draw_stripe(self, line_w, interval_w, offset, theta2, theta1):
        # define boundary condition
        p = 2 * self.num1 - 2 * self.num2 * \
            np.tan(theta1) + (1 - np.tan(theta1)) * self.num3 + self.beta
        q = p - self.num3 * np.tan(theta1)
        l2 = q / 2
        w = (l2 + self.num3) * np.sin(theta1)
        h = p * np.cos(theta1)

        # return
        self.all_stripe = []

        # start calculate stripe points
        dist = offset
        is_bottom_line = False
        is_upside = False
        is_left_side = False
        judge = [self.num1 ** 2 + self.num2 **
                 2, self.num1 ** 2 + self.num2 ** 2]
        # while dist < (self.num1 * np.cos(theta2) + self.num2 * np.cos(theta2)):     # 描画範囲内
        while judge[1] <= judge[0]:
            judge[0] = judge[1]
            judge[1] = (self.num2 - dist * np.sin(theta2)) ** 2 + \
                (self.num1 - dist * np.cos(theta2)) ** 2
            if is_bottom_line is False:
                _stripe = Stripe()
                _seg = StripeSegment()

            if dist == 0:
                _dot = Dot(0, 0)
                _seg.append(_dot)
                dist += line_w
                is_bottom_line = True
                continue

            if (np.tan(theta2) * dist * np.sin(theta2) + dist * np.cos(theta2)) / np.tan(theta2) < self.num2:
                # 上辺に接している
                is_upside = True
                _dot = Dot((np.tan(theta2) * dist * np.sin(theta2) +
                            dist * np.cos(theta2)) / np.tan(theta2), 0)
                _seg.append(_dot)
            else:
                # 右辺に接している
                if np.tan(theta2) * self.num2 - np.tan(theta2) * dist * np.sin(theta2) \
                        - dist * np.cos(theta2) < -self.num1:  # 下に溢れたら
                    _dot = Dot(self.num2, -self.num1)
                    _seg.append(_dot)
                    break
                else:
                    _dot = Dot(self.num2,
                               np.tan(theta2) * self.num2 - np.tan(theta2) * dist * np.sin(theta2) - dist * np.cos(
                                   theta2))
                    _seg.append(_dot)
                if is_upside is True & is_bottom_line is True:  # 点が増えるパターン
                    _dot = Dot(self.num2, 0)
                    _seg.append(_dot)
                is_upside = False

            if (-np.tan(theta2) * dist * np.sin(theta2) - dist * np.cos(theta2)) > -self.num1:
                # 左辺に接している
                is_left_side = True
                _dot = Dot(0, -np.tan(theta2) * dist *
                           np.sin(theta2) - dist * np.cos(theta2))
                _seg.append(_dot)
            else:
                # 下辺に接している
                if (-self.num1 + np.tan(theta2) * dist * np.sin(theta2) + dist * np.cos(theta2)) / np.tan(
                        theta2) > self.num2:
                    _dot = Dot(self.num2, -self.num1)
                    _seg.append(_dot)
                    break
                else:
                    _dot = Dot(
                        (-self.num1 + np.tan(theta2) * dist * np.sin(theta2) +
                         dist * np.cos(theta2)) / np.tan(theta2),
                        -self.num1)
                    _seg.append(_dot)
                if is_left_side == True & is_bottom_line == True:  # 点が増えるパターン
                    _dot = Dot(0, -self.num1)
                    _seg.append(_dot)
                is_left_side = False

            if is_bottom_line is True:
                # メイン面についてのみ作る
                _stripe.append(_seg)
                _stripe.setcolor(rand.randint(0, 255), rand.randint(
                    0, 255), rand.randint(0, 255))
                self.all_stripe.append(_stripe)

            if is_bottom_line is False:
                dist += line_w
            else:
                dist += interval_w
            is_bottom_line = not is_bottom_line

        # メイン面を元に他の面を作る
        provis_result = []
        for e_stripe in self.all_stripe:
            for e_seg in e_stripe.get():
                _seg1 = e_seg.reflect(
                    Dot(-self.num3 / 2, 0), Dot(-self.num3 / 2, -self.num1))  # 左に鏡映
                provis_result.append(_seg1)
                _seg2 = e_seg.reflect(Dot(0, -(self.num1 * 2 + self.num3) / 2),
                                      Dot(self.num2, -(self.num1 * 2 + self.num3) / 2))  # 右下に鏡映
                provis_result.append(_seg2)
                _seg3 = e_seg.reflect(Dot((self.num2 * 2 + self.num3) / 2, 0),
                                      Dot((self.num2 * 2 + self.num3) / 2, -self.num1))  # 右に鏡映
                provis_result.append(_seg3)
            for e_seg in provis_result:
                e_stripe.append(e_seg)
            provis_result.clear()

        # 側面について追加
        for e_stripe in self.all_stripe:
            for e_seg in e_stripe.get():
                # mainの左
                if e_seg.have_vertical(0, -self.num1):
                    _seg1 = StripeSegment()
                    _dot = Dot(0, e_seg.get_vertical(0, -self.num1)[0])
                    _seg1.append(_dot)
                    _dot = Dot(0, e_seg.get_vertical(0, -self.num1)[1])
                    _seg1.append(_dot)
                    _dot = Dot(0, e_seg.get_vertical(0, -self.num1)[0])
                    _dot.move(-self.num3, 0)
                    _seg1.append(_dot)
                    _dot = Dot(0, e_seg.get_vertical(0, -self.num1)[1])
                    _dot.move(-self.num3, 0)
                    _seg1.append(_dot)
                    provis_result.append(_seg1)

                # メインの左上(上に作ってから鏡映)
                if e_seg.have_horizon(0, -self.num2):
                    _seg2 = StripeSegment()
                    _dot = Dot(e_seg.get_horizon(0, -self.num2)[0], 0)
                    _seg2.append(_dot)
                    _dot = Dot(e_seg.get_horizon(0, -self.num2)[1], 0)
                    _seg2.append(_dot)
                    _dot = Dot(e_seg.get_horizon(0, -self.num2)[0], 0)
                    _dot.move(0, self.num3)
                    _seg2.append(_dot)
                    _dot = Dot(e_seg.get_horizon(0, -self.num2)[1], 0)
                    _dot.move(0, self.num3)
                    _seg2.append(_dot)
                    provis_result.append(_seg2.reflect(
                        Dot(-self.num3 / 2, 0), Dot(-self.num3 / 2, self.num2)))

                # メインの右
                if e_seg.have_vertical(self.num2, -self.num1):
                    _seg3 = StripeSegment()
                    _dot = Dot(self.num2, e_seg.get_vertical(
                        self.num2, -self.num1)[0])
                    _seg3.append(_dot)
                    _dot = Dot(self.num2, e_seg.get_vertical(
                        self.num2, -self.num1)[1])
                    _seg3.append(_dot)
                    _dot = Dot(self.num2, e_seg.get_vertical(
                        self.num2, -self.num1)[0])
                    _dot.move(self.num3, 0)
                    _seg3.append(_dot)
                    _dot = Dot(self.num2, e_seg.get_vertical(
                        self.num2, -self.num1)[1])
                    _dot.move(self.num3, 0)
                    _seg3.append(_dot)
                    provis_result.append(_seg3)

                # メインの下
                if e_seg.have_horizon(-self.num1, -self.num2):
                    _seg4 = StripeSegment()
                    _dot = Dot(e_seg.get_horizon(-self.num1, -
                                                 self.num2)[0], -self.num1)
                    _seg4.append(_dot)
                    _dot = Dot(e_seg.get_horizon(-self.num1, -
                                                 self.num2)[1], -self.num1)
                    _seg4.append(_dot)
                    _dot = Dot(e_seg.get_horizon(-self.num1, -
                                                 self.num2)[0], -self.num1)
                    _dot.move(0, -self.num3)
                    _seg4.append(_dot)
                    _dot = Dot(e_seg.get_horizon(-self.num1, -
                                                 self.num2)[1], -self.num1)
                    _dot.move(0, -self.num3)
                    _seg4.append(_dot)
                    provis_result.append(_seg4)

            for e_dot in provis_result:
                e_stripe.append(e_dot)
            provis_result.clear()

        for e_dot in self.dots_to_render:
            e_dot.rot(0, 0, theta1)
            e_dot.move(w, h)
            # g.plot(e_dot.x, e_dot.y, marker='*')

        for e_stripe in self.all_stripe:
            #Aprint("STRIPE:have color")
            # print(e_stripe.r,e_stripe.g,e_stripe.b)
            for e_dots in e_stripe.get():
                e_dots.sort()
                # print("STRIPESEGMENT:have", e_dots.len(), "dots")
                for e_dot in e_dots.get():
                    e_dot.move(self.num2 + self.num3, 0)
                    e_dot.rot(0, 0, theta1)
                    e_dot.move(w, h)
                    # g.plot(e_dot.x, e_dot.y, marker='o', color=[e_stripe.r / 255, e_stripe.g / 255, e_stripe.b / 255])

    def draw_continuous_picture(self, s, u, offset, b2s_angle, b_angle):
        line_w = s
        interval_w = u
        offset = offset
        theta1 = b2s_angle
        theta2 = b_angle
        # define boundary condition
        p = 2 * self.num1 - 2 * self.num2 * \
            np.tan(theta1) + (1 - np.tan(theta1)) * self.num3 + self.beta
        q = p - self.num3 * np.tan(theta1)
        l2 = q / 2
        w = (l2 + self.num3) * np.sin(theta1)
        h = p * np.cos(theta1)

        # return
        self.all_stripe = []

        # start calculate stripe points
        dist = offset
        is_bottom_line = False
        is_upside = False
        is_left_side = False
        judge = [self.num1 ** 2 + self.num2 **
                 2, self.num1 ** 2 + self.num2 ** 2]
        # while dist < (self.num1 * np.cos(theta2) + self.num2 * np.cos(theta2)):     # 描画範囲内
        while judge[1] <= judge[0]:
            judge[0] = judge[1]
            judge[1] = (self.num2 - dist * np.sin(theta2)) ** 2 + \
                (self.num1 - dist * np.cos(theta2)) ** 2
            if is_bottom_line is False:
                _stripe = Stripe()
                _seg = StripeSegment()

            if dist == 0:
                _dot = Dot(0, 0)
                _seg.append(_dot)
                dist += line_w
                is_bottom_line = True
                continue

            if (np.tan(theta2) * dist * np.sin(theta2) + dist * np.cos(theta2)) / np.tan(theta2) < self.num2:
                # 上辺に接している
                is_upside = True
                _dot = Dot((np.tan(theta2) * dist * np.sin(theta2) +
                            dist * np.cos(theta2)) / np.tan(theta2), 0)
                _seg.append(_dot)
            else:
                # 右辺に接している
                if np.tan(theta2) * self.num2 - np.tan(theta2) * dist * np.sin(theta2) \
                        - dist * np.cos(theta2) < -self.num1:  # 下に溢れたら
                    _dot = Dot(self.num2, -self.num1)
                    _seg.append(_dot)
                    break
                else:
                    _dot = Dot(self.num2,
                               np.tan(theta2) * self.num2 - np.tan(theta2) * dist * np.sin(theta2) - dist * np.cos(
                                   theta2))
                    _seg.append(_dot)
                if is_upside is True & is_bottom_line is True:  # 点が増えるパターン
                    _dot = Dot(self.num2, 0)
                    _seg.append(_dot)
                is_upside = False

            if (-np.tan(theta2) * dist * np.sin(theta2) - dist * np.cos(theta2)) > -self.num1:
                # 左辺に接している
                is_left_side = True
                _dot = Dot(0, -np.tan(theta2) * dist *
                           np.sin(theta2) - dist * np.cos(theta2))
                _seg.append(_dot)
            else:
                # 下辺に接している
                if (-self.num1 + np.tan(theta2) * dist * np.sin(theta2) + dist * np.cos(theta2)) / np.tan(
                        theta2) > self.num2:
                    _dot = Dot(self.num2, -self.num1)
                    _seg.append(_dot)
                    break
                else:
                    _dot = Dot(
                        (-self.num1 + np.tan(theta2) * dist * np.sin(theta2) +
                         dist * np.cos(theta2)) / np.tan(theta2),
                        -self.num1)
                    _seg.append(_dot)
                if is_left_side == True & is_bottom_line == True:  # 点が増えるパターン
                    _dot = Dot(0, -self.num1)
                    _seg.append(_dot)
                is_left_side = False

            if is_bottom_line is True:
                # メイン面についてのみ作る
                _stripe.append(_seg)
                _stripe.setcolor(rand.randint(0, 255), rand.randint(
                    0, 255), rand.randint(0, 255))
                self.all_stripe.append(_stripe)

            if is_bottom_line is False:
                dist += line_w
            else:
                dist += interval_w
            is_bottom_line = not is_bottom_line

        # ----- debug parts -----
        for e_dot in self.dots_to_render:
            pass
            #e_dot.rot(0, 0, theta1)
            #e_dot.move(w, h)
            # g.plot(e_dot.x, e_dot.y, marker='*')
        for e_stripe in self.all_stripe:
            #print("STRIPE:have color")
            # print(e_stripe.r,e_stripe.g,e_stripe.b)
            for e_dots in e_stripe.get():
                e_dots.sort()
                # print("STRIPESEGMENT:have", e_dots.len(), "dots")
                for e_dot in e_dots.get():
                    pass
                    #e_dot.move(self.num2 + self.num3, 0)
                    #e_dot.rot(0, 0, theta1)
                    #e_dot.move(w, h)
                    ##g.plot(e_dot.x, e_dot.y, marker='o', color=[e_stripe.r / 255, e_stripe.g / 255, e_stripe.b / 255])


if __name__ == '__main__':
    # print(np.arctan2(np.pi/2))
    # 引数の3数は大きさです。順番は内部でソートします
    # test = GiftBox(100, 60, 30)
    # test = GiftBox(20,25,30)
    test = GiftBox(100, 120, 150)
    # test.get_valid_paper_size(np.pi/4)

    # print(test.getOptimalTheta())

    # print("許容角度")
    # for i in range(900):
    #     if test.is_valid_theta(i/10 /180*np.pi): print(i/10)
    #     print(np.arctan(i/10 /180*np.pi))

    # 線の幅、線の間、オフセット、箱に対するストライプの角度、箱の角度の順です
    # test.draw_stripe(5,4,5, np.pi / 4, np.pi / 4)
    # test.draw_stripe(5,4,5, np.pi / 2, np.pi / 4)
    test.draw_stripe(10, 10, 0, np.pi / 4, np.pi / 4)

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
