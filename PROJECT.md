# net-attack-predict —— 小组项目：物联网网络攻击检测

领域：study / DMU ｜ 状态：单个 notebook 完成，本机已跑通，Colab 未实测 ｜ 最后更新：2026-10-18

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

## 实现方案

**2026-10-18 改为只用一个 notebook（用户决定）**：项目只剩 5 天左右，有组员没有编程经验，要精简、紧扣课堂内容，让每个人打开 notebook 就能看懂数据处理、训练、验证、调优的全过程。用户要求删掉其他代码和产物，所以下面这些都已删除：
- `src/iotids` 模块库（含 Seam / Adapter 设计）、`scripts/`、`tests/`、`configs/`；
- `notebooks/playground.ipynb`、双击启动器、`pyproject.toml`；
- 生成的 `runs/`、解压出的 CSV。

它们都还在 git 历史里，最后一个包含它们的提交是 `dc6a350`。原先 2026-10-17 定的「数据模块拆 Seam 给组员分头改」「每个实验一份配置文件」作废。

仍然有效的决定（用户 2026-10-17 确认）：
- **只做二分类：判断一条流量记录是不是攻击**。主要目的是掌握训练的整个流程。
- 评估只讲训练曲线、混淆矩阵、攻击检出率和正常误报率。
- **框架用 PyTorch，训练循环自己写**，不用 Lightning、skorch 这类封装。
- 评估必须图形化，老师一看就明白。

### notebook：`notebooks/iot_attack_detection.ipynb`

- **自包含**：所有代码都在 notebook 里，约 200 行。在 Colab 里 *Runtime → Run all* 就能跑，没有本地数据时会自己从 GitHub 下载压缩包。Colab 链接见 [README.md](README.md)。
- 按 Step 0–9 组织，每一步注明对应哪节课（week1 感知机 / 反向传播，week2 泛化、过拟合、early stopping、dropout、归一化）：
  - Step 1–2：读数据、清洗、划分 70/15/15（按 Attack_type 分层，seed 42）；
  - Step 3 数据处理：
    - 训练行：全部 / 50%、10%、5%、1% / 把攻击欠采样到 1:1；
    - 特征：全部 / 去掉常数列 / 去掉 proto 和 service / 手动输入要去掉的列；
    - 缩放：standard、minmax、robust、log + standard、none；
    - 以上都只在 train 上学习。
  - Step 4 模型：隐藏层、激活函数（relu、leaky_relu、tanh、sigmoid）、dropout。
  - Step 5 训练：每个 optimizer 有自己的参数：
    - sgd：momentum、nesterov；
    - adam、adamw：beta1、beta2；
    - rmsprop：alpha、momentum；
    - adagrad：无。
    - 通用参数：lr、weight decay、batch size、max epochs、patience。训练循环是手写的。
  - Step 6：测试集混淆矩阵。
  - Step 7：`run_experiment` 依次执行 Step 3–6，并跑一次 baseline。
  - Step 8 实验面板（ipywidgets，代码默认折叠）：Data、Model、Training 三页，选哪个 optimizer 就出现它自己的参数；下方是结果表和对比图。
  - Step 9：按三页分组的推荐实验，附实测数字。
- 分工（用户 2026-10-18）：Data 页给研究数据处理的同学，Model 页给同学 2，Training 页（optimizer 和调参）由用户本人负责。组员名单仍待补。
- 2026-10-18 起不再用 Colab 表单（`# @param`），原因有两个：表单把下拉选项 `0.0` / `1.0` 显示成 `0` / `1`，和默认值对不上而报错；表单也做不到「选了哪个 optimizer 才显示它的参数」。
- baseline（隐藏层 64、标准化、Adam lr 0.001、batch 256、最多 30 轮、early stopping 5）的实测结果：best val loss 0.0076，攻击检出 99.84%，误报 1.28%。环境是本机 CPU，2026-10-18。
- 本机执行过整份 notebook，Step 9 列的实验也全部跑过，数字都是实测值。**未在 Colab 上实测**。用户在 Colab 上跑旧版代码时，末位数字和本机略有不同，**推断**是 CPU 和 torch 版本不同造成的。

### 实验设计（Step 9）

按面板三页分组，每次只在 baseline 上改一处。数字是本机单个 seed 的实测值，完整表格见 notebook Step 9。
- **Data**：
  - 不缩放时第一轮 loss 约 45,000；robust 也不稳定；log + standard 最好（val loss 0.0058，误报 0.9%）；
  - 去掉 proto 和 service 后误报从 1.3% 升到 2.2%；
  - 攻击欠采样到 1:1 后误报 1.1%，但漏报变多。
- **Model**：
  - 无隐藏层时误报 7.5%；[128, 64] 误报 0.8%；
  - [256, 128] 并不更好；
  - 数据全量时 dropout 只会让学习变慢；
  - 4 层 sigmoid + SGD 时 loss 卡在 0.33，所有流量都判成攻击。
- **Training**：
  - Adam 的 lr 取 0.00001 时误报 35%，取 0.1 时 val loss 来回跳；
  - SGD 在 lr 0.001 时误报 35%；lr 0.01 加 momentum 0.9 后 val loss 0.017；lr 0.1 加 momentum 0.9 后 0.0096；
  - rmsprop 和 Adam 差不多；Adam 的 beta2 改成 0.9 后变差；adagrad 的步长会越来越小。
- **过拟合（三页一起改）**：只用 1% 训练行（826 行）、网络 [256, 128]、150 轮、patience 0：
  - val loss 第 7 轮最低（0.106），之后升到 0.31；
  - patience 5 能保住第 7 轮的权重；weight decay 0.01 效果最好（最后 0.12）；dropout 帮助很小；把训练行增加到 10% 最有效。

结果写进报告时：原文（实验数字）、推断、建议分开写；只跑一个 seed 时，差几行的结果要注明「可能是随机波动」；结论对应 week2/lesson2 的泛化、过拟合、正则化。

### 数据问题（写代码时发现）

- `no` 列在每个攻击类型里从 0 重新计数（CSV 按类型排序），不是唯一编号，已丢弃。
- 去掉 `no` 后有 5,195 行完全重复，划分前去重，剩 117,922 行。另有 7 行特征相同但标签不同，保留。
- 标签末尾带 `\r`；部分特征最大值约 2e10（例如 `flow_iat.tot`），所以提供了 `log + standard` 缩放。

### 运行环境

- Colab：直接打开即可，CPU 就够用。
- 本机：虚拟环境在 `~/.venvs/dmu-project1`（资料库外，避免依赖被同步上云），用 VS Code 或 Jupyter 打开 notebook。2026-10-18 已从该环境卸载旧的 `iotids` 包。
- 不要两台机器同时跑本项目：同步时文件正被改写会产生 `.conflict1/.conflict2` 副本。

## 为什么可以不用 KDD

课程的 Word 作业说明前面允许自选实际问题和数据，后面讲网络入侵的段落写法像是指定 KDD。结合课堂原话，KDD 只是兜底例子，自选数据可以。以下几句已在 `week2/lesson2/class_notes.md`（自动转写，未与音频核对）里查到原文：

- `00:34:43` "Sometimes your topic, you cannot find data, change the topic."
- `00:52:59` "after the real life problem of the data, you can, uh, take, um, Ready-made data." / `00:53:22` "Anything that you want to predict?"
- `01:12:44` "After two, three, four days, you couldn't find any, any topic, choose the topic." / `01:15:07` "In the worst scenario, you can take this example."

Word 作业说明原件已于 2026-10-17 存入 `sources/NNS_report_instruction.docx`（← 用户上传的 `NNS_report_instruction.docx`）。它前面写「A real-life problem using a large dataset, or A network intrusion dataset provided or found online」，KDD 段落以「if you choose this topic」开头，和上面的判断一致。代码语言写的是「Matlab or Python or any other programming language」，代码格式和可用框架的结论见 [assessment.md](../assessment.md) 的 "Code: file format and tools"。

## 数据集

- **RT-IoT2022**，Kaggle：<https://www.kaggle.com/datasets/supplejade/rt-iot2022real-time-internet-of-things>，2026-10-16 下载。
- `data/raw/rt-iot2022.zip`（← 原 `data/rt-iot2022.zip`，2026-10-18 按标准目录移入 `raw/`）：原始压缩包，3.8 MB。解压得到 `data/raw/RT_IOT2022.csv`（55 MB，123,117 行不含表头，85 列；第一列 `no` 是行号，最后一列 `Attack_type` 是标签，其余是流量特征）。notebook 直接读压缩包，不需要解压。

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
- 交给老师的代码形式：assessment.md 推断 Colab `.ipynb` 最贴合老师习惯。**建议**直接提交 `notebooks/iot_attack_detection.ipynb`，待用户确认。

## 文件

- `notebooks/iot_attack_detection.ipynb` —— 整个项目的代码（上面的「notebook」）
- `data/raw/rt-iot2022.zip` —— 数据集原始压缩包（原样保留）。notebook 在 Colab 里从 GitHub 下载的就是这个文件，不要删除或改名
- `README.md` —— 给组员和老师看的英文说明
- `.gitignore` —— 不该提交的文件
- `.vscode/settings.json` —— VS Code 配置：解释器指向 `~/.venvs/dmu-project1`，终端不在同步目录里生成缓存
- `PROJECT.md`、`sources/` —— 资料库约定：项目决定记录，课程原件（`sources/NNS_report_instruction.docx`，2026-10-17 存入）
