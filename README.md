# IoT Network Attack Detection Using Neural Networks

A multilayer perceptron (MLP) in PyTorch that reads IoT network flow features (RT-IoT2022) and says
**normal** or **attack**. Coursework for Neural Systems & NLP (CSIP5103), De Montfort University Dubai.

The whole project is one notebook:

<a href="https://colab.research.google.com/github/buildwithyang/net-attack-predict/blob/main/notebooks/iot_attack_detection.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

[`notebooks/iot_attack_detection.ipynb`](notebooks/iot_attack_detection.ipynb)

## How to run

**Colab (recommended):** click the badge above, then *Runtime → Run all*. A CPU is enough.
The notebook downloads the dataset by itself.

**Local:** Python 3.10+ with `torch numpy pandas scikit-learn matplotlib`, then open the notebook
in Jupyter or VS Code and run all cells. It reads `data/raw/rt-iot2022.zip` directly (no need to unzip).

## What is inside

| Step | Content |
| --- | --- |
| 1 | load and clean the data (drop the row counter, remove duplicates, label normal / attack) |
| 2 | stratified train / validation / test split, 70 / 15 / 15, seed 42 |
| 3 | one-hot encode `proto` / `service`, scale the numeric features (fitted on train only) |
| 4 | build the MLP |
| 5 | hand-written training loop with early stopping |
| 6 | test: detection rate, false alarm rate, confusion matrix |
| 7 | **experiment**: change settings (scaling, network size, activation, dropout, optimizer, learning rate, batch size, epochs, early stopping, weight decay, training rows) |
| 8 | compare all runs in a table and a chart |
| 9 | suggested experiments with the results we got |

## Files

```
notebooks/iot_attack_detection.ipynb   the code
data/raw/rt-iot2022.zip                the dataset (keep it: Colab downloads it from here)
sources/                               the coursework specification
```

## Data notes

- Source: <https://www.kaggle.com/datasets/supplejade/rt-iot2022real-time-internet-of-things>
  (`RT_IOT2022.csv`, 123,117 rows, 85 columns).
- Column `no` restarts at 0 for every attack type, so it is dropped. 5,195 duplicate rows are removed
  before splitting; 117,922 rows remain.
- **Assumption**: `Thing_Speak`, `MQTT_Publish`, `Wipro_bulb` are normal traffic; all other types are
  attacks. Not yet checked against the dataset paper.
- About 90% of rows are attacks, so accuracy alone is misleading; we report the detection rate and the
  false alarm rate.
