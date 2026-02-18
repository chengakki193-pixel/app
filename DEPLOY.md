## 部署到 Render (免费/推荐)

**Render** 的 "Web Service" 提供免费层，非常适合托管API。

### 1. 准备代码 (Push到GitHub)
确保你的代码已上传到GitHub仓库（必须包含 `Dockerfile` 和 `requirements.txt`）。

### 2. 在 Render 创建服务
1. 注册/登录 [dashboard.render.com](https://dashboard.render.com/)
2. 点击 **New +** -> **Web Service**
3. 连接你的 GitHub 仓库
4. 配置如下：
   - **Name**: `stock-api` (任意名)
   - **Runtime**: `Docker` (很重要，选Docker！)
   - **Instance Type**: `Free` (免费)
5. 点击 **Create Web Service**

### 3. 获取 API 地址
部署成功后，Render 会给你一个在线地址，例如：
`https://stock-api-xq3z.onrender.com`

### 4. 给 AI 使用
把这个地址给 AI 即可：
- 价格查询: `https://stock-api-xq3z.onrender.com/api/stock/price?code=600000`
- 文档地址: `https://stock-api-xq3z.onrender.com/docs`

---

## 部署到 Zeabur (国内速度快/需信用卡验证)

1. 登录 [zeabur.com](https://zeabur.com)
2. 创建项目 -> 部署新服务 -> Git
3. 选择你的仓库
4. Zeabur 会自动识别 `Dockerfile` 并部署
5. 在 "域名" 选项卡中绑定一个免费域名（如 `stock-api.zeabur.app`）

---

## ⚠️ 注意事项

**免费版的限制 (Render)：**
- **休眠机制**：如果 15 分钟没人访问，服务会进入休眠。
- **唤醒延迟**：下一次请求时，需要等待 30-60 秒启动（AI 第一次调用可能会超时，重试即可）。
- **解决方法**：使用 `UptimeRobot` 每 10 分钟访问一次你的 API，保持唤醒。
