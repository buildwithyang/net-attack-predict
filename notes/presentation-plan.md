# 个人 presentation 最终安排（用户本人，2026-10-21）

来源：`../sources/NNS_report_instruction.docx`（评分表、Individual Presentation、Deliverable 3）、`../../assessment.md`、`../PROJECT.md` 的实验数字。整理日期 2026-10-18。

用户的贡献（用户 2026-10-18 说明）：整个项目代码由用户组织实现；实验对比的重点放在 Training 部分；其他各部分也基本清楚。

## 评分要求（原文）

- Presentation 评分表三项，各 10 分：
  1. **Content & Understanding**：满分要求 "strong grasp of the topic and **personal contribution explained in depth**"。
  2. **Delivery & Engagement**：自信、节奏好、和听众互动。
  3. **Visual Aids & Clarity**：图要清楚，"minimal text overload"。
- 必须覆盖：问题和数据集简介、方法概述、个人贡献、主要结果、收获和教训。
- Tips：10–15 分钟；多用图表；术语讲浅；最后给反思或下一步；不要照着念。
- Deliverable 3：PPT 10–15 分钟，之后 **15 分钟提问 + 现场 demo**，viva 必须参加。
- 老师课上（10.12 summary）：约 10 页，含目标、文献、方法、数据划分、对比表、混淆矩阵、结论；每个人都要懂项目从头到尾。

## 推断

- 三项里最容易拉开差距的是「个人贡献讲得深」。组员共用数据和结果，个人贡献页是唯一区别。
- 用户的贡献分两层：**搭起整个系统**（工程）和 **Training 实验**（研究）。两层都要讲，合计约占一半时间。
- 组员也会讲各自的部分（Data 页、Model 页实验），所以说法要准确：代码是「我组织实现的」，Data / Model 页的实验发现要注明是哪位组员做的，避免讲成全是自己的。
- Q&A + demo 也在 30% 里。代码全是自己写的，这是 demo 环节的优势：老师指哪一格都能讲清楚。

## 最终 PPT 安排（2026-10-18 定稿，约 13 分钟，12 页 + 备用页）

主线：**我把整个流程搭成一个可复现的实验平台，再用它回答一个问题：训练方法怎么决定 MLP 学不学得会。**

- 第 1–4 页：问题和背景，约 3 分钟。
- 第 5–7 页：我搭了什么，约 3.5 分钟。
- 第 8–10 页：我发现了什么，约 4 分钟。
- 第 11–12 页：结果和反思，约 2 分钟。

PPT 用英文。每页标题写成一句结论，下面一张主图，正文最多 3 行。「要讲的点」写进 speaker notes，只写关键词。

| # | 页标题（英文） | 画面 | 要讲的点 | 时间 |
| --- | --- | --- | --- | --- |
| 1 | IoT Network Attack Detection Using Neural Networks | 题目、姓名、学号；一行写角色：*Implemented the full pipeline · Led the training experiments* | 一句话说清这次要讲什么 | 0:20 |
| 2 | Two mistakes matter: missing an attack, and a false alarm | 左图：攻击被放进来（漏报）；右图：正常设备被拦（误报）。底部写 Aim 和 3 个 Objectives | 用烟雾报警器打比方。Aim：用 MLP 区分正常 IoT 流量和攻击。Objectives：① 搭一个可复现的流程；② 比较训练设置的影响；③ 用检出率和误报率评估 | 1:10 |
| 3 | Related work: RT-IoT2022 was built for IoT intrusion detection | 小表格，三行：数据集原论文（无监督自编码器，关注边缘设备资源）、反向传播、Adam；最后一行写「Ours：有监督 MLP，关注训练方法和误报」 | 讲清我们和原论文的区别：它压缩模型，我们研究怎么训练 | 0:50 |
| 4 | 90% of the traffic is attack, so accuracy alone misleads | 类别比例条形图（正常 10% / 攻击 90%），旁边写 123,117 flows · 83 features | 全猜攻击也有 90% 准确率，所以我们看检出率和误报率。正常设备是 ThingSpeak、MQTT、Wipro 灯泡（UCI 页面写明） | 0:50 |
| 5 | I built one pipeline from raw data to test result | 横向流程图：clean → split 70/15/15 → scale（fit on train） → MLP → early stopping（val） → test once。每一步下方小字标对应的课 | validation 用来挑模型，test 只在最后用一次；缩放只在 train 上学，避免泄漏 | 1:15 |
| 6 | The data had hidden problems I fixed before training | 四行前后对比表：`no` 列、5,195 行重复、标签带 `\r`、特征最大约 2e10 | 重点讲去重：要放在划分之前，否则同一行可能同时出现在 train 和 test，成绩会虚高 | 1:00 |
| 7 | A small MLP and a hand-written training loop | 左：网络图（83 → 64 → 1，ReLU，sigmoid）；右：实验面板截图（Data / Model / Training 三页） | 训练循环每一步：forward → loss → backward → step。面板让组员不写代码也能做实验 | 1:15 |
| 8 | Adam learns fastest; plain SGD needs momentum to catch up | 三条 val loss 曲线叠在一张图（SGD / SGD + momentum / Adam），图上标 best val loss：0.017 / 0.017 / 0.0076 | 用滚球比喻讲 momentum；Adam 会给每个权重自动调步长 | 1:30 |
| 9 | The learning rate decides whether the network learns at all | 三条曲线：太小（1e-5）、合适（1e-3）、太大（0.1）；图注：太小时误报 35%，太大时 loss 来回跳 | 用下山步子的比喻；SGD 在 lr 0.001 时误报也是 35% | 1:15 |
| 10 | With little data the network memorises; early stopping saves it | 1% 数据、[256, 128] 网络的 train / val 曲线，标出第 7 轮（val loss 0.106）和之后升到 0.31；旁边小表比较 patience 5、weight decay、dropout、10% 数据 | 用模拟考的比喻讲 early stopping；最有效的是加数据，其次是 weight decay | 1:15 |
| 11 | Final model: 99.84% of attacks caught, 1.28% false alarms | 测试集混淆矩阵（大图）+ 小对比表：baseline、log + standard、[128, 64]，各写一行并注明哪位组员做的 | 数字以 Colab 跑出的为准；组员的发现说明是谁做的 | 1:00 |
| 12 | What I learned, and what comes next | 三栏。Learned：训练设置和网络结构一样重要；先看数据再建模。Limits：只跑了一个 seed；只做了二分类。Next：多分类、多 seed / 交叉验证 | 结尾一句反思，然后说「I can show the notebook live」，直接接 demo | 0:50 |

**备用页**（放在 Thank you 后面，不讲，只在提问时翻出来）：

- B1：实验面板和 Run all 的截图，Colab 出问题时用。
- B2：Step 9 完整实验表。
- B3：训练循环的代码截图。
- B4：参考文献列表。

## 参考文献（上 PPT 前逐条核对）

- Sharmila, B.S. and Nagapadma, R. (2023) 'Quantized autoencoder (QAE) intrusion detection system for anomaly detection in resource-constrained IoT devices using RT-IoT2022 dataset', *Cybersecurity*, 6. doi:10.1186/s42400-023-00178-5。已核对标题、作者、期刊和 DOI，文章编号未核对。
- RT-IoT2022 数据集，UCI Machine Learning Repository，doi:10.24432/C5P338。
- Rumelhart, D.E., Hinton, G.E. and Williams, R.J. (1986) 'Learning representations by back-propagating errors', *Nature*, 323, pp. 533–536。凭记忆写的，未核对。
- Kingma, D.P. and Ba, J. (2015) 'Adam: A method for stochastic optimization', ICLR。凭记忆写的，未核对。
- Prechelt, L. (1998) 'Early stopping — but when?', in *Neural Networks: Tricks of the Trade*. Springer。凭记忆写的，未核对。

## 视觉

- 标题写成结论句，下面放图作为证据。
- 一页一张主图，正文不超过 3 行；细节放 speaker notes。
- 颜色固定：攻击一个色、正常一个色，三个 optimizer 各一个色，全篇不变。
- 图都从 Colab 实跑结果导出，因为老师会重跑核对。

## 术语讲浅（可用的比喻）

- learning rate：下山每一步迈多大，太小走不到，太大跨过谷底。
- momentum：滚下坡的球带着惯性，不会被小坑卡住。
- early stopping：模拟考成绩开始下降就停止刷题，保留最好那次。
- 误报 / 漏报：烟雾报警器没着火也响 / 着火了不响。

## Demo（现场演示，约 3 分钟）

1. 打开 Colab notebook。提前 Run all 跑完，不要现场从头跑。
2. 到实验面板 Training 页，把 optimizer 改成 SGD、lr 设为 0.001，运行，看到误报变高。
3. 切回 Adam、lr 0.001，看到结果恢复。
4. 主动说「老师想看哪一步，我直接打开讲」。

Colab 已测试通过（用户 2026-10-18 确认）。网络或 Colab 出问题时，用备用页 B1 的截图讲。

## Q&A 预案（可能被问）

- 为什么用 MLP，不用 CNN 或随机森林？
- 为什么不只看 accuracy？
- 为什么缩放只在 train 上 fit？为什么分层划分？validation 和 test 各做什么？
- 反向传播怎么更新权重（`w ← w − η·∂E/∂w`）？
- Adam 为什么比 SGD 快？momentum 起什么作用？
- 为什么不用 KDD？正常和攻击是怎么归类的？答：按 UCI 页面，ThingSpeak、MQTT、Wipro 灯泡是正常设备流量。
- 只跑一个 seed，差距可靠吗？答：差距大的结论可信，差几行的标为可能是随机波动。
- 老师指着某格代码问「这行在做什么」：重点准备训练循环（forward → loss → backward → step → zero_grad）、early stopping 怎么保存最好的权重、为什么去重要放在划分之前。

## 准备日程

| 日期 | 做什么 |
| --- | --- |
| 10-18 周日 | 从 Colab 导出图：类别比例、三个 optimizer 曲线、lr 对比、过拟合曲线、混淆矩阵、面板截图 |
| 10-19 周一 | 按上表做 PPT；核对参考文献；写 speaker notes 关键词；和组员对一下各自讲哪些贡献 |
| 10-20 周二 | 计时排练 2–3 遍，控制在 13 分钟以内；练 demo；过一遍 Q&A |
| 10-21 周三 | 讲之前在 Colab 上 Run all 跑好 |

## 待确认

- 参考文献逐条核对（见上）。
- 第 11 页组员的名字和他们各自做的实验。
