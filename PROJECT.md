# net-attack-predict —— 小组项目：物联网网络攻击检测

领域：study / DMU ｜ 状态：代码完成；实验结果已清空，待重新跑 ｜ 最后更新：2026-10-18

本课程（CSIP5103 / CSIP5103D）的小组项目。考核比重、硬要求和日期以上级目录的 [assessment.md](../assessment.md) 为准，本文件只记本项目自己的决定。

## 项目性质（用户 2026-10-17 确认）

这是一个**学习项目**，学的是**神经网络 MLP**（多层感知机）。模型用 MLP，目的是借这个项目把 MLP 学懂。

## 选题（用户已确认）

- 中文：**基于神经网络的物联网网络攻击检测**
- 英文：**IoT Network Attack Detection Using Neural Networks**
- 任务：根据网络流量特征，判断是正常通信还是攻击。
- 标题不带数据集名，RT-IoT2022 放在报告的「数据来源」部分介绍（用户意见）。
- 范围：正常 / 攻击**二分类**；用 MLP 比较不同参数设置；分析**攻击检出率**和**正常流量误报率**。

来源：用户 2026-10-16 提供的早先讨论，只存本摘要，原文不入库。

## 实现方案（用户 2026-10-17 确认）

- **只做二分类：判断一条流量记录是不是攻击**。主要目的是掌握训练的整个流程。
- 评估只讲训练曲线、混淆矩阵、攻击检出率和正常误报率。按攻击类型拆分和类别不平衡实验是补充材料，不作为主线。
- 对比实验围绕训练流程：标准化、学习率、网络大小、过拟合与 early stopping / dropout。配置在 `configs/training/`。
- **框架用 PyTorch，训练循环自己写**，不用 Lightning、skorch 这类封装。学习目标是框架和实战，不做 numpy 手写版。
- 模型只接触数字矩阵 `X, y`，不知道 CSV。
- 数据模块必须拆好 Seam，并配好文档和注释：后期会由其他组员实现和调试不同的清洗（去掉干扰特征）、标准化等方案来对比效果。
- 评估必须图形化，老师一看就明白。
- 每个实验是一份配置文件，只改其中一节；`seed` 和 `data.split` 不变，保证测试集相同（看 `metrics.json` 里的 `test_fingerprint`）。

代码结构、各模块的 Interface、怎么加新的 Adapter，见 [README.md](README.md)。

### 实验设计

主线（`configs/training/`），每组只比 baseline 改一处：

| 组 | 配置 | 改了什么 |
| --- | --- | --- |
| 基线 | `baseline` | 隐藏层 [64]，标准化，lr 0.001，early stopping 5，阈值 0.5 |
| 标准化 | `scale_none` | 不做标准化 |
| 学习率 | `lr_high`、`lr_low` | lr 0.1 / 0.00001 |
| 网络大小 | `hidden_8`、`hidden_128_64` | 隐藏层 [8] / [128, 64] |
| 过拟合 | `long_no_early_stop`、`long_no_early_stop_dropout` | 100 轮、关掉 early stopping，后者再加 dropout 0.3 |

关掉 early stopping 时，模型保留**最后一轮**的权重，这样能看到过拟合对测试结果的影响。

补充（`configs/imbalance/`）：训练集欠采样、损失函数类别权重、按验证集误报率选阈值。

结果写进本文件时：原文（实验数字）、推断、建议分开写；只跑一个 seed 时，差几行的结果要注明「可能是随机波动」；结论对应 week2/lesson2 的泛化、过拟合、正则化。

### 写代码时发现的数据问题

- `no` 列在每个攻击类型里从 0 重新计数（CSV 按类型排序），不是唯一编号，已丢弃，改用 CSV 行号作 id。
- 去掉 `no` 后有 5,195 行完全重复，划分前去重，剩 117,922 行。另有 7 行特征相同但标签不同，保留。
- 标签末尾带 `\r`；`bwd_URG_flag_count` 是常数列；部分特征最大值约 2e10，所以准备了 `log_standard` 标准化方案。

### 运行环境

- 虚拟环境在 `~/.venvs/dmu-project1`（资料库外，避免依赖被同步上云）。只用 CPU。
- 本项目已用 `pip install -e ".[dev]"` 以可编辑方式装进该环境（2026-10-18）。在项目根目录运行：`~/.venvs/dmu-project1/bin/python -B scripts/train.py configs/baseline.yaml`；测试直接 `pytest`。VS Code 终端已设好 `PYTHONDONTWRITEBYTECODE` 和 `MPLCONFIGDIR`，避免在同步目录里生成缓存。
- 依赖写在 `pyproject.toml`，版本下限按 Colab 能满足的写。
- 不要两台机器同时跑本项目：同步时文件正被改写会产生 `.conflict1/.conflict2` 副本。
- 2026-10-18 加了给没编程经验的组员用的启动器：双击 `start.command`（macOS）或 `start.bat`（Windows），代码在 `scripts/start.py`。它在项目根目录建 `.venv/`、装依赖、解压数据，再用菜单选实验、对比、自检。`.venv/` 已写进 `.gitignore`。**Drive 里这份副本不要用启动器**，否则 `.venv`（含 torch，几百 MB）会被同步上云；本机继续用 `~/.venvs/dmu-project1`。组员从 GitHub clone 后再用。

### 交互式 notebook（2026-10-18）

- `notebooks/playground.ipynb`：用滑块调数据处理、网络、optimizer 和训练参数，点 Train 后实时看 train / val loss 曲线，并给出测试集结果（四张图和 `summary.png` 相同）。另外可以对比多次运行、对单个参数做 sweep，还附带一份「引导实验」清单。用户要求：Colab 能跑，能交互式调超参数和 optimizer，看到效果。
- notebook 不另写模型或训练循环，直接调用 `src/iotids`。同配置、同 seed 和命令行结果一致：本机核对过 baseline，测试集 fp=20、fn=33，与 `runs/baseline/metrics.json` 相同。
- 为此给库加了以下功能，旧配置照常能用：
  - `train.optimizer` 新增 `adamw`、`rmsprop`、`adagrad`；
  - 新增可选的 `train.momentum`（sgd、rmsprop）和 `train.weight_decay`；
  - `fit(..., on_epoch=...)` 回调，用来画实时曲线；
  - `data.sampler` 新增 `{name: subsample, fraction: 0.01}`，只用一部分训练行，用来故意做出过拟合。
  - 对应测试共 19 个，全部通过。
- Colab 里的 setup 单元会从 GitHub clone 仓库，所以 Colab 徽章和 clone 都要等这些改动 push 之后才生效。
- 引导实验里的数字来自 2026-10-18 本机 CPU、seed 42 的单次运行。**推断**：换机器或换 torch 版本，末位可能不同。几个值得写进报告的观察（原文数字见 notebook 第 6 节）：
  - 不做标准化时，第一轮 train loss 约 44,000；
  - SGD 在 lr 0.001 下 30 轮后误报 35%，而 Adam 只有 1.1%；
  - 全量数据下这个 MLP 几乎不过拟合；只用 1%（828 行）训练、网络取 [256, 128] 时，val loss 在第 20 轮最低（0.066），之后升到 0.25；
  - 在这个设置下，weight decay 0.01 能把最后的 val loss 压到 0.077，dropout 0.3 / 0.5 几乎没用；
  - 4 层 sigmoid + SGD 时 loss 卡在 0.33，模型把所有流量都判成攻击。

## 为什么可以不用 KDD

课程的 Word 作业说明前面允许自选实际问题和数据，后面讲网络入侵的段落写法像是指定 KDD。结合课堂原话，KDD 只是兜底例子，自选数据可以。以下几句已在 `week2/lesson2/class_notes.md`（自动转写，未与音频核对）里查到原文：

- `00:34:43` "Sometimes your topic, you cannot find data, change the topic."
- `00:52:59` "after the real life problem of the data, you can, uh, take, um, Ready-made data." / `00:53:22` "Anything that you want to predict?"
- `01:12:44` "After two, three, four days, you couldn't find any, any topic, choose the topic." / `01:15:07` "In the worst scenario, you can take this example."

Word 作业说明原件已于 2026-10-17 存入 `sources/NNS_report_instruction.docx`（← 用户上传的 `NNS_report_instruction.docx`）。它前面写「A real-life problem using a large dataset, or A network intrusion dataset provided or found online」，KDD 段落以「if you choose this topic」开头，和上面的判断一致。代码语言写的是「Matlab or Python or any other programming language」，代码格式和可用框架的结论见 [assessment.md](../assessment.md) 的 "Code: file format and tools"。

## 数据集

- **RT-IoT2022**，Kaggle：<https://www.kaggle.com/datasets/supplejade/rt-iot2022real-time-internet-of-things>，2026-10-16 下载。
- `data/raw/rt-iot2022.zip`（← 原 `data/rt-iot2022.zip`，2026-10-18 按标准目录移入 `raw/`）：原始压缩包，3.8 MB。解压得到 `data/raw/RT_IOT2022.csv`（55 MB，123,117 行不含表头，85 列；第一列 `no` 是行号，最后一列 `Attack_type` 是标签，其余是流量特征）。2026-10-18 按用户要求删除了解压出的 CSV，用前先 `unzip data/raw/rt-iot2022.zip -d data/raw/`。

各标签行数（2026-10-16 统计）：

| Attack_type | 行数 | 推断归类 |
| --- | ---: | --- |
| DOS_SYN_Hping | 94,659 | 攻击 |
| Thing_Speak | 8,108 | 正常 |
| ARP_poisioning | 7,750 | 攻击 |
| MQTT_Publish | 4,146 | 正常 |
| NMAP_UDP_SCAN | 2,590 | 攻击 |
| NMAP_XMAS_TREE_SCAN | 2,010 | 攻击 |
| NMAP_OS_DETECTION | 2,000 | 攻击 |
| NMAP_TCP_scan | 1,002 | 攻击 |
| DDOS_Slowloris | 534 | 攻击 |
| Wipro_bulb | 253 | 正常 |
| Metasploit_Brute_Force_SSH | 37 | 攻击 |
| NMAP_FIN_SCAN | 28 | 攻击 |

**推断**：Thing_Speak、MQTT_Publish、Wipro_bulb 看名字是正常设备流量，其余是攻击。这个归类还没对照 Kaggle 页面或原论文核实。照这个归类，正常 12,507 行（10.2%），攻击 110,610 行（89.8%），单是 DOS_SYN_Hping 就占 76.9%。

**建议**：攻击占了绝大多数，全猜「攻击」准确率也有约 90%。所以报告不要只报 accuracy，要报正常流量误报率、各类检出率和混淆矩阵，并考虑类别权重或重采样。

## 个人 presentation 要求

来源：用户 2026-10-16 粘贴的课程页面 "Individual Presentation"（原文不入库）。

- **每个组员都要单独准备、单独讲自己的 presentation**："Each group member must prepare and deliver their own presentation"。项目数据和实验结果可以共用。
- 必须覆盖：问题和数据集简介；方法概述；用自己的方式说明本人对项目的贡献；主要结果；收获和教训。
- 10–15 分钟，多用图表，术语讲浅，最后给一段简短反思或下一步，不要照着念。
- 页面写的是 "Due on 11 November 2025 11:59 AM"，比现在早一年，推断是旧学期的设置没改。本次以用户确认的 2026-10-27 为准，见 [assessment.md](../assessment.md)。

**建议**的 PPT 结构（约 9 页、12 分钟）：题目与目标 → 实际问题（误报和漏报）→ 数据集 → 数据处理与训练 / 验证 / 测试划分 → 网络结构与训练方法 → 对比实验 → 结果（训练曲线、指标表、混淆矩阵）→ 个人贡献与收获 → 结论、局限与下一步。

## 分工记录

从现在开始记录每个人实际做了什么（数据清洗、模型训练、结果分析等），讲 PPT 时用代码、实验记录和图表证明自己的贡献。每个人都要理解完整流程。

| 组员 | 做了什么 | 证据（文件 / 提交） |
| --- | --- | --- |
| （待填） | | |

## 待确认

- 组员名单。
- 正常 / 攻击标签的归类（见上方推断）。
- 交给老师的代码形式：assessment.md 推断 Colab `.ipynb` 最贴合老师习惯。现在已有调用模块的 `notebooks/playground.ipynb`（交互式），是否直接作为提交形式待定。

## 文件

2026-10-18 按 Python 机器学习项目常用的 src 布局整理（用户要求），代码从 `code/` 提到项目根目录。每个目录的作用见 [README.md](README.md) 的 "Project layout"。

- `README.md`、`pyproject.toml`、`configs/`、`src/iotids/`、`scripts/`、`tests/` —— 代码部分（标准布局）
- `notebooks/playground.ipynb` —— 交互式调参 notebook（Colab / Jupyter），见上方「交互式 notebook」
- `data/raw/rt-iot2022.zip` —— 数据集原始压缩包（原样保留）；解压出的 CSV 可以随时重建
- `runs/<name>/` —— 每个实验的结果和图表，由 `scripts/train.py` 生成（目前已清空）
- `.gitignore` —— 列出可重新生成、不该提交的文件
- `.vscode/settings.json` —— VS Code 配置：解释器指向 `~/.venvs/dmu-project1`，让 `iotids`、`torch` 等可以点击跳转
- `PROJECT.md`、`sources/` —— 资料库约定：项目决定记录，课程原件（`sources/NNS_report_instruction.docx`，2026-10-17 存入）
