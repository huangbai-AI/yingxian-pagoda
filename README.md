# 应县木塔 · 一木千年

六幕连续滚动的 3D 科普网站，包含斜向拆层、柱网展示、斗栱近景、飞檐归位和自由观塔。

![首屏预览](yingxian-pagoda/public/alignment/after-01.png)

## 本地运行

需要 Node.js 22.12 或更新版本。

```sh
cd yingxian-pagoda
npm ci
npm run dev
```

构建：`npm run build`。将生成的 `yingxian-pagoda/dist` 部署在站点根目录。`alignment.html` 为最新六幕光影与排版对照页，`quality.html` 保留第九版试验。

## 完整下载

[版本附件](https://github.com/huangbai-AI/yingxian-pagoda/releases/tag/v9) 提供网站成品、可编辑 Blender 模型、通用模型和渲染样片的完整压缩包。解压后可运行启动脚本。

仓库保留网站源码、网页用模型、纹理、字体、设计参考及建模脚本。体积较大的 Blender 文件、通用模型和网站成品保存在版本附件中。

## 当前版本

第十版重新调整六幕侧光与补光、瓦面亮度、背景明暗、标题位置、字号及行距。首屏保留 64° 广角仰视和两侧前景松枝。六幕随滚动连续变化，可进入自由观塔。版本附件 v9 保留第九版完整交付。

网页仍为实时渲染；对照页中的两张预渲染样片属于上一轮试验，尚未生成完整滚动影片。模型是科普展示性重建，并非文物测绘模型，与设计参考仍有细节差异。

详细使用方式及素材来源见 [使用说明](使用说明.md)。木纹素材来自 Poly Haven，采用 CC0 许可。
