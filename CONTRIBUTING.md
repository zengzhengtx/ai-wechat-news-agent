# 贡献指南

感谢您对AI资讯微信公众号智能体项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请：

1. 检查[Issues](https://github.com/zengzheng/wechatAgent/issues)中是否已有相关问题
2. 如果没有，请创建新的Issue，包含：
   - 问题的详细描述
   - 复现步骤
   - 期望的行为
   - 实际的行为
   - 环境信息（Python版本、操作系统等）

### 提交代码

1. Fork这个仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

### 代码规范

- 遵循PEP 8 Python代码规范
- 使用4个空格缩进
- 添加适当的注释和文档字符串
- 确保代码通过现有测试
- 为新功能添加测试

### 开发环境设置

```bash
# 克隆您的fork
git clone https://github.com/您的用户名/wechatAgent.git
cd wechatAgent

# 创建虚拟环境
conda create -n wechat-agent python=3.11 -y
conda activate wechat-agent

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_basic.py
python stable_demo.py
```

### 测试

在提交PR之前，请确保：

- 所有现有测试通过
- 新功能有相应的测试
- 运行演示脚本无错误

### 文档

- 更新README.md（如果需要）
- 为新功能添加使用示例
- 更新配置文件说明

## 项目结构

```
wechatAgent/
├── src/                    # 源代码
│   ├── agent/             # 智能体核心
│   ├── tools/             # 工具集合
│   ├── database/          # 数据库相关
│   ├── utils/             # 工具函数
│   └── web/               # Web界面
├── tests/                 # 测试文件
├── docs/                  # 文档
├── config.yaml           # 配置文件
└── requirements.txt       # 依赖列表
```

## 联系方式

如有问题，请通过以下方式联系：

- 创建Issue
- 发送邮件到项目维护者

感谢您的贡献！
