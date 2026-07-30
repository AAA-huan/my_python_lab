import colorsys


class ColorUtils:
    """调色器"""
    def __init__(self, hex: str):
        self.hex = hex
        self.rgb = self.hex2rgb(self.hex)
        pass

    def hex2rgb(self, hex: str) -> tuple[int, int, int]:
        """
        十六进制字符串转rgb(0~255)
        :param hex:颜色的字符串代码
        :return:rgb数组
        """
        # 去掉可能存在的#号
        hex_str = hex.strip('#')
        # 截取两个字符转为16进制数据
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return r, g, b

    def rgb2hex(self, r: int, g: int, b:int) -> str:
        """
        将RGB整数转为 #RRGGBB 大写十六进制色号
        :param r:红
        :param g:绿
        :param b:蓝
        :return:十六进制色号
        """
        return f"#{r:02X}{g:02X}{b:02X}"

    def rgb2hsv(self, r: int, g: int, b: int) -> tuple[float, float, float]:
        """
        RGB(0~255) → HSV
        :param r:红色
        :param g:绿色
        :param b:蓝色
        :return:H：0~360 色相角度
                S：0~1 饱和度
                V：0~1 明度
        """
        # 先把rgb整数映射到0~1的浮点数
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        h_norm = h * 360
        return h_norm, s, v

    def hsv2rgb(self, h: float, s: float, v: float) -> tuple[int, int, int]:
        """
        HSV转回RGB(0~255整数)
        :param h:色相
        :param s:饱和度
        :param v:明度
        :return:rgb数组
        """
        h_norm = h / 360.0
        r_float, g_float, b_float = colorsys.hsv_to_rgb(h_norm, s, v)
        r = round(r_float * 255)
        g = round(g_float * 255)
        b = round(b_float * 255)
        return r, g, b

    def wrap_hue(self, hue: float) -> float:
        """色相角度归一化，限制 0 ≤ h < 360"""
        return hue % 360.0


    def get_complementary_hues(self, base_hue: float) -> list[float]:
        """互补色色相列表"""
        return [self.wrap_hue(base_hue), self.wrap_hue(base_hue + 180)]

    def get_analogous_hues(self, base_hue: float, span=30.0) -> list[float]:
        """类比色（邻近色）色相列表"""
        return [
            self.wrap_hue(base_hue - span),
            self.wrap_hue(base_hue),
            self.wrap_hue(base_hue + span)
        ]

    def get_triadic_hues(self, base_hue: float) -> list[float]:
        """三角色色相列表"""
        return [
            self.wrap_hue(base_hue),
            self.wrap_hue(base_hue + 120),
            self.wrap_hue(base_hue + 240)
        ]

    def calculate_palette_from_hex(self, mode: str, span=30.0):
        """
        【核心封装函数】输入HEX，输出整套配色的HEX列表
        :param mode: 配色函数（互补/类比/三角）
        :param span: 类比色间隔角度
        :return: 一组新的hex颜色字符串列表
        """
        # HEX → RGB
        r, g, b = self.hex2rgb(self.hex)
        # RGB → HSV，提取色相、保留原始饱和度、明度【关键！】
        base_h, s, v = self.rgb2hsv(r, g, b)

        # 用字典映射在内部做分发
        func_map = {
            'get_complementary_hues': lambda h: self.get_complementary_hues(h),
            'get_analogous_hues': lambda h: self.get_analogous_hues(h, span),
            'get_triadic_hues': lambda h: self.get_triadic_hues(h),
        }

        if mode not in func_map:
            raise ValueError(f"Unknown mode: {mode}")

        hue_list = func_map[mode](base_h)

        # 每个新色相 + 原始S、V → RGB → HEX
        result_hex = []
        for h in hue_list:
            nr, ng, nb = self.hsv2rgb(h, s, v)
            result_hex.append(self.rgb2hex(nr, ng, nb))
        return result_hex