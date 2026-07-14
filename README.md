# Deep Reader Toolkit

面向深度阅读者的方法论工具集。

## 包含的 Skill

| Skill | 说明 |
|-------|------|
| [deep-read](./deep-read/SKILL.md) | 用《学会提问》批判性思维框架深度分析书籍或资料，输出结构化分析报告 |
| [cli.py](./deep-read/cli.py) | EPUB/PDF/TXT → Markdown 转换工具（deep-read 预处理依赖） |

## 如何使用

将 skill 目录复制到你的 CodeArts skills 目录下即可使用：

```powershell
Copy-Item -Recurse ./deep-read ~/.codearts/skills/
```

### 安装预处理工具依赖

```powershell
cd deep-read
pip install -r requirements.txt
```

## 核心流程

**沉淀作者经验 → 批判性思维提炼 → 精华内化**

1. **快速扫描**：提取目录结构、核心论题、章节概览
2. **作者论证链**：观察→分类→求证→原因→现实展开→思维工具→结论
3. **分析路线图**：13步批判性思维深度分析
4. **精华提炼**：毋庸置疑的事实 + 可内化的方法论
5. **练习场**：实操练习题
6. **纠错与验证**：反驳/支持路径 + 自我反思
7. **输出报告**：交互式 HTML 报告