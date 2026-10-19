# Presentation preparation / PPT 准备说明

来源：`../presentation-plan.md`、`../../notebooks/iot_attack_detection.ipynb`、当前 Colab 运行导出 `assets/colab-results.json`。处理日期：2026-10-18；WPS 完成核对：2026-10-19。

## 已保存的成果

- **最终版** `output/yang-iot-presentation-wps.pptx`：12 页正文 + 4 页备用页，已在 WPS 打开、调整字体、保存并核对全部放映页及备注页。
- `output/yang-iot-presentation.pptx`：保留的初始生成版；排练和提交请使用上面的 WPS 最终版。
- `assets/`：Colab 直接导出的 5 张高清图、Training 面板截图、10 组完整配置/逐轮损失/混淆矩阵，以及原始导出 ZIP。
- `.build/`：构建脚本、逐页预览、结构与字体检查报告。不是提交给老师的代码。

## 原文与实测记录

- Colab baseline：best validation loss 0.007414，best epoch 29；攻击检出率 99.84%，正常误报率 1.16%。测试集矩阵：TN 1782、FP 21、FN 25、TP 15861。
- 83 个原始特征经 one-hot 编码后，MLP 输入是 94 维；网络为 94 / 64 / 1，ReLU；训练使用 BCEWithLogitsLoss，测试再用 sigmoid 和阈值 0.5。
- 10 组实验都来自当前 Colab CPU 会话，seed 42；没有把 Step 9 中的旧本机结果当作 Colab 结果。
- optimizer 图比较的是 SGD lr 0.1、SGD + momentum lr 0.01、Adam lr 0.001 三组配置，不能解释为只改了 optimizer。
- 小数据过拟合实验：826 行训练数据、隐藏层 256/128。第 7 轮验证损失最低 0.10594；第 150 轮为 0.31188。patience 5 时第 12 轮停止，恢复第 7 轮权重。
- 当前 notebook 每组实验都会显示 test 指标；没有把本轮结果写成“完全未查看的最终测试”。
- 日期按用户本轮确认：10-21 presentation；10-27 report。

## 推断与表达边界

- Adam 在这里达到更低的验证损失，不代表它对所有数据/预算都更好。
- 单个 seed 无法支持统计显著性结论。
- early stopping 保护的是验证损失最好的权重，不保证每个测试指标同时变好。
- 未写组员姓名和 Data/Model 实验归属，避免把尚未确认的贡献写给具体的人。

## 建议的排练

正文时间预算合计 11 分 55 秒，留约 1 分钟缓冲；这是预算，尚未实测用户讲述时长。10-20 计时练 2–3 遍。正式演示前先 Run all，现场只切 Training 设置并 Train。演示代码的顺序：forward、loss、zero_grad、backward、step。

三篇论文与 UCI 数据页已核对：
- Sharmila & Nagapadma (2023), Cybersecurity 6, 41: https://doi.org/10.1186/s42400-023-00178-5
- Rumelhart, Hinton & Williams (1986), Nature 323, 533–536: https://doi.org/10.1038/323533a0
- Kingma & Ba (2015), ICLR: https://arxiv.org/abs/1412.6980
- RT-IoT2022: https://doi.org/10.24432/C5P338

## 每页讲解关键词

### 1. IoT Network Attack Detection Using Neural Networks (0:20)

Normal or attack? / My part: full pipeline + training / What changed; what I learned

### 2. We need to catch attacks and avoid false alarms (1:00)

Think of a smoke alarm / 烟雾报警器
Fire, no alarm: missed attack
No fire, alarm: false alarm
Aim: classify IoT traffic
Objectives: build; compare; evaluate

### 3. We study training choices on an IoT dataset (0:50)

Dataset paper: autoencoder; edge resources
Backpropagation: calculate gradients
Adam: adapt updates
Our question: training choices; missed attacks; false alarms

### 4. About 90% of the records are attacks (0:50)

Raw: 123,117 flows; 83 features
After cleaning: 117,922 flows
Always say attack: about 90% accuracy
So: detection rate AND false alarms

### 5. I connected cleaning, training and evaluation (1:10)

My part: organised implementation; one notebook
Clean before split
Train 70%; validation 15%; test 15%
Fit scaler on training rows only
Same split and seed
Honest limit: panel shows test metrics after each run

### 6. Cleaning prevents misleading results (0:55)

no: counter, not a traffic feature
Duplicates: remove before split
Hidden label spaces: strip
Large numbers: scale
Same row in train and test: unfairly easy

### 7. A small MLP learns through a short training loop (1:10)

83 raw features; one-hot encoding gives 94 inputs
64 hidden units; ReLU
One output score
Sigmoid inside BCEWithLogitsLoss during training
Demo: forward; loss; zero gradients; backward; step

### 8. Adam reaches the lowest loss in this comparison (1:20)

Same data; same network; same seed
Three configurations; different learning rates shown
Momentum: a rolling ball / 惯性
Adam: adaptive step per weight
This experiment only; not a universal winner

### 9. The learning rate changes how well Adam learns (1:10)

Step size down a hill / 下山步长
0.00001: slow within 30 epochs
0.001: lower validation loss
0.1: unstable here
Same optimiser; change only learning rate

### 10. Validation shows when more training stops helping (1:20)

826 training rows; larger MLP
Training loss down; validation loss up
Mock exam / 模拟考
Best epoch 7; stop after 5 worse checks
Restore best weights
More data is a separate comparison

### 11. The baseline catches 99.84% of attacks (1:00)

Read rows: actual traffic
False alarms: 1.16% of normal traffic
Misses: 25 attacks
Threshold 0.5
Baseline checkpoint from validation
One seed; this dataset; exploratory test result

### 12. I learned to check the data and the training process (0:50)

My contribution: organised pipeline; training comparisons
Learned: data first; curves explain failures
Limits: one seed; binary labels; random split
Test results visible during experiments
Next: multiple seeds; fresh evaluation; attack-level recall
Thank you. Notebook demo.

### 13. The demo changes one training setting at a time (Backup)

Before talk: Run all
Reset baseline
Training: SGD, lr 0.001; Train
Reset baseline
Training: Adam, lr 0.001; Train
If unavailable: show saved Colab results

### 14. The comparison uses saved Colab runs (Backup)

All rows: Adam, SGD, momentum, learning rates
Small-data runs: 826 rows, larger network
Best val is not last val
Patience 0: last weights
Patience 5: best weights
Different data/model rows are separate comparisons

### 15. Each batch follows five simple steps (Backup)

scores: forward pass
loss: compare scores with labels
zero_grad: clear previous gradients
backward: calculate current gradients
step: update weights
Validation: eval + no_grad
Best weights: deepcopy; load_state_dict

### 16. These sources support the data and methods (Backup)

Dataset and three papers checked 18 October 2026

## 问答备忘（建议表达）

- Why MLP? Tabular data; course focus; a simple baseline. 未比较随机森林，不声称 MLP 优于它。
- Why not accuracy alone? About 90% attacks; an always-attack model gets about 90% accuracy but 100% false alarms.
- Why train-only scaling? Validation and test must not set the preprocessing statistics.
- What does backward do? Calculate gradients. The optimiser step changes the weights.
- Why zero_grad? PyTorch accumulates gradients; clear the previous batch before backward.
- Why save a deepcopy? Keep a separate copy of the best weights, not a reference that continues to change.
- Why is the input 94 rather than 83? One-hot encoding expands categorical columns.
- Is Adam always better? No. Here, these settings and this seed gave lower validation loss.
- What is the main limitation? One seed and one random split; test results were visible during exploration.

## WPS 状态

2026-10-19：WPS 已恢复并完成最终版保存。已核对 16 页实际放映和 16 页关键词备注；修复备注文本框缺少尺寸的问题，清理无用页脚占位符和模板字体。正文使用 Arial，代码使用 Courier New；缺失字体提示已消失。WPS 保存后的正文与备注文字和初始版逐项一致，文件结构、字体、原生表格、16 页页数及重新导入检查通过。

证据：`assets/wps-final.png`、`assets/wps-notes-verified.png`、`.build/wps-check/`；检查报告：`.build/wps-validation.json` 和 `.build/wps-completion.json`。尚未计时排练，也未提交给老师。
