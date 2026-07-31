from PIL import Image
import numpy as np
from io import BytesIO


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

    def get_palette(self, n_colors: int=2, min_percentage: float=5.0):
        """
        获取完整调色板，过滤掉占比过低的颜色
        :param n_colors: 最大颜色数量
        :param min_percentage: 最小占比阈值（百分比），低于此值的颜色将被过滤
        :return: list of dict，按占比降序排列
        """
        colors = self.kmeans_colors()

        # 过滤低于阈值的颜色
        filtered = [c for c in colors if c['percentage'] >= min_percentage]

        # 如果过滤后颜色太少，返回原始结果
        if len(filtered) < 2:
            return colors[:n_colors]

        # 截取到需要的数量
        return filtered[:n_colors]


    def kmeans_colors(self, n_colors: int =5, max_iter: int =20, tol: int =1.0):
        """
        使用 K-Means 聚类提取主色调
        :param n_colors: 最大颜色数量
        :param max_iter: 预处理最大尺寸
        :param tol: 最小占比阈值（百分比），低于此值的颜色将被过滤
        :return:
        """
        # 降采样预处理
        processed = self._preprocess()
        pixels = np.array(processed).reshape(-1, 3).astype(np.float32)

        # k-means初始化
        # 中心点选得越好算法迭代越快，结果越稳定
        centroids = np.zeros((n_colors, 3))
        # 第一个中心随机选一个像素
        centroids[0] = pixels[np.random.randint(len(pixels))]
        for i in range(1, n_colors):
            # 对每个像素计算其到最近中心的距离
            dists = np.min(
                np.linalg.norm(
                    pixels[:, np.newaxis] - centroids[:i], axis=2
                ),
                axis=1
            )
            # 距离越远被选中的概率越大（按权重重采样）
            probs = dists / sum(dists)
            centroids[i] = pixels[np.random.choice(len(pixels), p=probs)]

        # 开始迭代聚类
        for _ in range(max_iter):
            # 计算每个像素到所有中心的距离
            dists = np.linalg.norm(
                pixels[:, np.newaxis] - centroids, axis=2
            )
            labels = np.argmin(dists, axis=1)  # 每个像素属于哪个簇

            # 计算新的中心 = 每个簇像素的平均值
            new_centroids = np.array([
                pixels[labels == k].mean(axis=0) if np.any(labels == k)
                else centroids[k]
                for k in range(n_colors)
            ])

            # 检查收敛，中心移动小于tol就停止
            shift = np.linalg.norm(new_centroids - centroids)
            centroids = new_centroids
            if shift <= tol:
                break

        # 迭代结束，统计每个簇的占比
        dists = np.linalg.norm(pixels[:, np.newaxis] - centroids, axis=2)
        labels = np.argmin(dists, axis=1)
        total = len(pixels)
        counts = np.array([np.sum(labels == k) for k in range(n_colors)])

        # 按占比降序排列
        order = np.argsort(-counts)
        colors = centroids[order].astype(np.int32)
        percentages = (counts[order] / total * 100).round(2)

        # 返回兼容现有格式
        result = []
        for i in range(n_colors):
            r, g, b = int(colors[i][0]), int(colors[i][1]), int(colors[i][2])
            r, g, b = min(r, 255), min(g, 255), min(b, 255)
            result.append({
                'hex': f'#{r:02X}{g:02X}{b:02X}',
                'rgb': (r, g, b),
                'percentage': float(percentages[i])
            })
        return result


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

    # 测试 K-Means 聚类
    print("【K-Means 聚类】")
    colors = processor.kmeans_colors(n_colors=1)
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