# Final Project Brief: Anomaly Detection

## Overview and deadline

Build and honestly evaluate an anomaly detector on a real problem, then hand in a short report and your code by **30 December 2026, 23:59**. This deadline is fixed.

The project is designed to fit around a full-time job and a PhD. Each project is done individually, and you are welcome to use data from your own research or work if you are allowed to share the results.

## What to submit

Submit two files: a report of 6 to 10 pages and your source code as a zip. How to send them will be announced later.

| Deliverable | Format | What it contains |
| --- | --- | --- |
| Report | PDF, in English, 6 to 10 pages including figures and excluding references, any template | The problem and its anomaly type, the data, the methods, the results, and what you would do next, including the limits of your approach |
| Source code | One .zip named after you, under 50 MB | Notebooks or scripts, a short README with the steps to run them, a requirements.txt, and the data or a link to it |

If your data cannot leave your lab or company, include a small sample or a synthetic stand-in so that the code still runs, and say so in the report.

## Proposed topics

Pick one of these six topics or bring a different one. The datasets are starting points, and you should confirm the anomaly type for your problem.

| Topic | Likely anomaly type | Suggested dataset | Question to explore |
| --- | --- | --- | --- |
| Your own research or work data | Depends on the data | Your own | Which detector finds the events that matter in your field, and what does a false alarm cost? |
| Industrial sensor monitoring | Collective | [SKAB](https://github.com/waico/SKAB) | Do window features beat scoring each reading on its own? |
| Server and cloud metrics | Contextual | [NAB](https://github.com/numenta/NAB), AWS server metrics | Does modelling daily and weekly patterns reduce false alarms? |
| Network intrusion | Point and collective | [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) | Which attack categories does each detector miss, and why? |
| ECG arrhythmia | Collective | [MIT-BIH Arrhythmia Database](https://physionet.org/content/mitdb/) | Can a detector trained on normal beats flag arrhythmias across patients? |
| Scientific data | Point or collective | [MAGIC Gamma Telescope](https://archive.ics.uci.edu/dataset/159/magic+gamma+telescope) or the [LHC Olympics 2020](https://lhco2020.github.io/homepage/) R&D data | Can a detector find rare signal events without being trained on the signal? |

For MAGIC, downsample the gamma class so that the signal is rare, because the file is not balanced like real data. In the LHC Olympics, use the R&D data with its labelled benchmark signal, because the challenge data has no labels.

A topic outside this list needs no approval. If you are unsure whether it fits, message Eduard Stan at eduard.stan@dell.com, or talk directly to your professor. Please do not reuse the course datasets (Credit Card Fraud, KDD Cup 1999, Sparkov, NYC taxi) as your main dataset.

## Minimum requirements

Every project must meet these five points, so that all projects can be read and compared the same way; everything beyond them is your choice.

1. **Data with ground truth.** Use real data with labels. A defensible proxy or injected anomalies are fine if you explain them.
2. **Named anomaly type.** State whether you target point, contextual or collective anomalies, and why.
3. **Three detectors.** Compare at least three, one of them a simple baseline such as a z-score. Any library or method is allowed.
4. **Clean split.** Choose the threshold on a validation split and report results on a held-out test set. For time-ordered data, split by time.
5. **Reproducible code.** Fix the random seeds, and make sure the code runs from start to finish by following your README.

## What we look for

We value clear reasoning over complex models, so a well-argued comparison of classical detectors is a complete project.

- **No deep learning needed.** The project can run on a laptop, and a small dataset is fine if it suits the question.
- **Negative results count.** If no detector works well, explaining why is a valid outcome.
- **Reuse is welcome.** You can start from the course notebooks and from your existing work. Cite what you reuse, including AI assistance.
