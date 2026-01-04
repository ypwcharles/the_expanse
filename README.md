# The Expanse (苍穹浩瀚) 翻译项目

## 简介

《无垠的太空/苍穹浩瀚》原著小说中文翻译项目。

- **原著**：The Expanse
- **作者**：James S.A. Corey (詹姆斯·S.A.·科里)
- **翻译**：印象 & AI辅助
- **首发**：[博客园 - 印象](https://www.cnblogs.com/rockyching2009/category/2106963.html)

## 系列目录

1.  **利维坦觉醒 (Leviathan Wakes)**
2.  **卡利班之战 (Caliban’s War)**
3.  **亚巴顿之门 (Abaddon’s Gate)**
4.  **锡沃拉之旅 (Cibola Burn)**
5.  **涅墨西斯之局 (Nemesis Games)**
6.  **巴比伦废墟 (Babylon’s Ashes)**
7.  **波斯波利斯崛起 (Persepolis Rising)**
8.  **提亚玛特之怒 (Tiamat’s Wrath)**
9.  **利维坦陨落 (Leviathan Falls)**

*番外合集：Memory’s Legion (2022)*

## 翻译进度

### 已完结
- (1) 利维坦觉醒
- (9) 利维坦陨落

### 翻译中
- (7) 波斯波利斯崛起 (当前重点)
- (8) 提亚玛特之怒

*(其他卷目尚未启动)*

## 技术实现与构建

本项目使用 Python 脚本结合 Pandoc 自动化生成高质量 EPUB 电子书。

### 核心功能
*   **自动化构建**：使用 `generate_th7_epub.py` 一键生成 EPUB。
*   **智能脚注处理**：
    *   源码保持纯净的 Markdown 格式（使用标准 `[^1]` 语法）。
    *   构建过程中自动将 Markdown 脚注转换为特定格式的 HTML 代码（`<span><a...><sup>①</sup></a></span>`），以兼容老旧或特定的 EPUB 阅读器，确保“译注”标题与内容正确同页显示。
*   **目录生成**：自动提取章节标题生成 TOC。

### 使用方法

1.  **环境要求**：
    *   Python 3.x
    *   Pandoc

2.  **生成电子书**：
    ```bash
    python3 generate_th7_epub.py
    ```
    生成的 EPUB 文件将位于 `the_expanse/中文电子书/` 目录下。

## 最近更新

- **[2026-01] 脚注显示修复**：
    - 解决了部分阅读器中“译注”标题与内容分离的问题。
    - 实现了构建时自动转换脚注格式，不再需要手动维护 HTML 代码，源码回归标准 Markdown。
    - 修复了跨章节脚注 ID 冲突的问题。

## 参考资料

- [The Expanse Wiki](https://expanse.fandom.com/wiki/The_Expanse_Wiki)
