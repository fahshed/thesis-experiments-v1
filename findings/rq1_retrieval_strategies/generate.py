"""
RQ1: How do retrieval strategies affect accuracy?
Comparison: S1 vs S2 vs S3, model fixed to Mistral-7B GPU.
Generates charts 1–4.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import *

OUT = os.path.dirname(os.path.abspath(__file__))


def chart01_overall_accuracy():
    """Grouped bar: soft accuracy, strict accuracy, parseability by strategy."""
    data = load_all_data()
    configs = STRATEGY_CONFIGS
    metrics = {c: compute_metrics(data[c]) for c in configs}

    labels = [STRATEGY_DISPLAY[c] for c in configs]
    soft   = [metrics[c]['soft_accuracy'] for c in configs]
    strict = [metrics[c]['strict_accuracy'] for c in configs]
    parse  = [metrics[c]['parseability'] for c in configs]

    x = np.arange(len(labels))
    w = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - w, soft,   w, label='Soft Accuracy',   color='#2196F3')
    bars2 = ax.bar(x,     strict, w, label='Strict Accuracy', color='#FF9800')
    bars3 = ax.bar(x + w, parse,  w, label='Parseability',    color='#4CAF50')

    ax.set_ylabel('Rate')
    ax.set_title('Overall Accuracy & Parseability by Retrieval Strategy')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.15)
    ax.legend()

    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt='%.2f', fontsize=9, padding=2)

    savefig(fig, os.path.join(OUT, 'chart01_overall_accuracy.png'))


def chart02_per_category_accuracy():
    """Grouped bar: per-category soft accuracy by strategy."""
    data = load_all_data()
    configs = STRATEGY_CONFIGS

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(CATEGORIES))
    w = 0.25

    for i, c in enumerate(configs):
        df = data[c]
        accs = [df[df['question_category'] == cat]['judge_answer_credit'].mean()
                for cat in CATEGORIES]
        bars = ax.bar(x + (i - 1) * w, accs, w,
                      label=STRATEGY_DISPLAY[c], color=list(STRATEGY_COLORS.values())[i])
        ax.bar_label(bars, fmt='%.2f', fontsize=8, padding=2)

    ax.set_ylabel('Soft Accuracy')
    ax.set_title('Per-Category Accuracy by Retrieval Strategy')
    ax.set_xticks(x)
    ax.set_xticklabels([CATEGORY_SHORT[c] for c in CATEGORIES], rotation=15, ha='right')
    ax.set_ylim(0, 1.15)
    ax.legend()
    savefig(fig, os.path.join(OUT, 'chart02_per_category_accuracy.png'))


def chart03_error_distribution():
    """Stacked bar: error type distribution by strategy."""
    data = load_all_data()
    configs = STRATEGY_CONFIGS

    # Build error counts (exclude 'none')
    error_types_no_none = [e for e in ERROR_TYPES if e != 'none']
    counts = {}
    for c in configs:
        df = data[c]
        total = len(df)
        dist = df['judge_error_type'].value_counts()
        counts[c] = [dist.get(e, 0) / total for e in error_types_no_none]

    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(configs))
    bottom = np.zeros(len(configs))

    cmap = plt.cm.Set3(np.linspace(0, 1, len(error_types_no_none)))
    for i, etype in enumerate(error_types_no_none):
        vals = [counts[c][i] for c in configs]
        ax.bar(x, vals, 0.5, bottom=bottom, label=ERROR_DISPLAY[etype], color=cmap[i])
        bottom += vals

    ax.set_ylabel('Proportion of Responses')
    ax.set_title('Error Type Distribution by Retrieval Strategy')
    ax.set_xticks(x)
    ax.set_xticklabels([STRATEGY_DISPLAY[c] for c in configs])
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
    savefig(fig, os.path.join(OUT, 'chart03_error_distribution.png'))


def chart04_efficiency():
    """Grouped bar: average latency and input tokens by strategy."""
    data = load_all_data()
    configs = STRATEGY_CONFIGS
    metrics = {c: compute_metrics(data[c]) for c in configs}
    labels = [STRATEGY_DISPLAY[c] for c in configs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Latency
    lats = [metrics[c]['avg_latency'] for c in configs]
    colors = [STRATEGY_COLORS[c] for c in configs]
    bars1 = ax1.bar(labels, lats, color=colors, width=0.5)
    ax1.set_ylabel('Average Latency (seconds)')
    ax1.set_title('Average Latency by Strategy')
    ax1.bar_label(bars1, fmt='%.2f', fontsize=10, padding=2)

    # Input tokens
    toks = [metrics[c]['avg_input_tokens'] for c in configs]
    bars2 = ax2.bar(labels, toks, color=colors, width=0.5)
    ax2.set_ylabel('Average Input Tokens')
    ax2.set_title('Average Input Tokens by Strategy')
    ax2.bar_label(bars2, fmt='%.0f', fontsize=10, padding=2)

    fig.suptitle('Efficiency Comparison by Retrieval Strategy', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    savefig(fig, os.path.join(OUT, 'chart04_efficiency.png'))


if __name__ == '__main__':
    setup_style()
    print('RQ1: Generating charts...')
    chart01_overall_accuracy()
    chart02_per_category_accuracy()
    chart03_error_distribution()
    chart04_efficiency()
    print('RQ1: Done.')
