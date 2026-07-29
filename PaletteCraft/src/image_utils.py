from PIL import Image
import numpy as np
from io import BytesIO
from collections import Counter


class ImageUtils:
    """图片处理器 - 直方图法提取主色调"""

    def __init__(self, img_data):
        """
        初始化图片处理器
        :param img_data: 图片字节流数据
        """
        try:
            stream = BytesIO(img_data)
            self.img = Image.open(stream)
            # 确保图片为RGB模式
            if self.img.mode != 'RGB':
                self.img = self.img.convert('RGB')
            # 记录原始尺寸
            self.original_size = self.img.size
        except Exception as e:
            raise ValueError(f"图片读取失败: {e}")

    def _preprocess(self, max_size=200):
        """
        图片预处理：缩放到合理尺寸以提高性能
        :param max_size: 最大边长按（像素）
        :return: 预处理后的PIL Image
        """
        width, height = self.img.size
        # 如果图片已经小于max_size，直接返回
        if max(width, height) <= max_size:
            return self.img.copy()

        # 计算缩放比例，保持长宽比
        scale = max_size / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        # 使用LANCZOS高质量缩放
        return self.img.resize((new_width, new_height), Image.LANCZOS)

    def get_dominant_colors(self, n_colors=5, max_size=200, bins=32):
        """
        使用直方图法提取图片主色调
        :param n_colors: 要提取的主色调数量
        :param max_size: 预处理最大尺寸，None则跳过预处理
        :param bins: 每个颜色通道的直方图bins数量（控制颜色精度）
        :return: list of dict: [{'hex': '#RRGGBB', 'rgb': (r,g,b), 'percentage': float}, ...]
        """
        # 1. 预处理：降采样提高性能
        if max_size:
            processed_img = self._preprocess(max_size)
        else:
            processed_img = self.img

        # 2. 转换为numpy数组
        np_image = np.array(processed_img)  # shape: (H, W, 3)

        # 3. 将像素量化到直方图桶中
        #    每个通道256色压缩到bins个桶
        #    计算每个像素对应的桶索引
        bin_size = 256 // bins
        quantized = (np_image // bin_size).astype(np.int32)

        # 4. 将RGB三通道的桶索引组合成唯一键
        #    key = r_bucket * bins^2 + g_bucket * bins + b_bucket
        keys = (quantized[:, :, 0] * bins * bins +
                quantized[:, :, 1] * bins +
                quantized[:, :, 2])

        # 5. 统计每个桶的像素数量
        flat_keys = keys.flatten()
        counter = Counter(flat_keys)

        # 6. 获取频率最高的n_colors个桶
        top_buckets = counter.most_common(n_colors)
        total_pixels = len(flat_keys)

        # 7. 计算每个桶的代表颜色（桶中心值）和占比
        dominant_colors = []
        for bucket_key, count in top_buckets:
            # 从桶索引反推RGB值（取桶中心）
            r_bucket = bucket_key // (bins * bins)
            g_bucket = (bucket_key % (bins * bins)) // bins
            b_bucket = bucket_key % bins

            # 计算桶中心的RGB值，转换为Python原生int
            r = int(r_bucket * bin_size + bin_size // 2)
            g = int(g_bucket * bin_size + bin_size // 2)
            b = int(b_bucket * bin_size + bin_size // 2)

            # 限制在有效范围内
            r = min(r, 255)
            g = min(g, 255)
            b = min(b, 255)

            # 转换为HEX
            hex_color = f"#{r:02X}{g:02X}{b:02X}"

            # 计算占比百分比
            percentage = round((count / total_pixels) * 100, 2)

            dominant_colors.append({
                'hex': hex_color,
                'rgb': (r, g, b),
                'percentage': percentage
            })

        return dominant_colors

    def get_palette(self, n_colors=1, max_size=200, min_percentage=1.0):
        """
        获取完整调色板，过滤掉占比过低的颜色
        :param n_colors: 最大颜色数量
        :param max_size: 预处理最大尺寸
        :param min_percentage: 最小占比阈值（百分比），低于此值的颜色将被过滤
        :return: list of dict，按占比降序排列
        """
        colors = self.get_dominant_colors(n_colors=n_colors * 2, max_size=max_size)

        # 过滤低于阈值的颜色
        filtered = [c for c in colors if c['percentage'] >= min_percentage]

        # 如果过滤后颜色太少，返回原始结果
        if len(filtered) < 2:
            return colors[:n_colors]

        # 截取到需要的数量
        return filtered[:n_colors]


# 测试代码
if __name__ == '__main__':
    # 测试用的图片数据（这里用一个简单的测试）
    # 实际使用时传入图片的二进制数据
    print("=" * 60)
    print("图片处理器 - 直方图法测试")
    print("=" * 60)

    # 创建一个简单的测试图片（红蓝绿渐变）
    test_img = Image.new('RGB', (300, 300))
    pixels = []
    for i in range(300):
        for j in range(300):
            # 创建一个有明显主色的图案
            if i < 100:
                pixels.append((255, 0, 0))      # 红色区域
            elif i < 200:
                pixels.append((0, 255, 0))      # 绿色区域
            else:
                pixels.append((0, 0, 255))      # 蓝色区域
    test_img.putdata(pixels)

    # 转换为字节流
    buffer = BytesIO()
    test_img.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()

    # 使用处理器
    processor = ImageUtils(img_bytes)

    print(f"原始图片尺寸: {processor.original_size}")
    print(f"预处理后尺寸: {processor._preprocess(200).size}")
    print()

    # 提取主色调
    print("【主色调提取 - 直方图法】")
    colors = processor.get_dominant_colors(n_colors=5)

    for i, color in enumerate(colors, 1):
        print(f"  {i}. {color['hex']}  RGB{color['rgb']}  占比: {color['percentage']}%")

    print()

    # 获取调色板
    print("【调色板 - 含过滤】")
    palette = processor.get_palette(n_colors=5, min_percentage=5.0)

    for i, color in enumerate(palette, 1):
        print(f"  {i}. {color['hex']}  RGB{color['rgb']}  占比: {color['percentage']}%")

    print()
    print("✅ 测试完成！")