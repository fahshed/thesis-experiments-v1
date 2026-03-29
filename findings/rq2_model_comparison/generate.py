"""
RQ2: How do models of varying sizes compare?
Comparison: Qwen 1.5B vs Mistral 7B vs LLaMA 13B, strategy fixed to S1 Full CV.
Generates charts 5–10.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import *

OUT = os.path.dirname(os.path.abspath(__file__))


def chart05_overall_accuracy():
    """Grouped bar: soft accuracy, strict accuracy, parseability by model."""
    data = load_all_data()
    configs = MODEL_CONFIGS
    metrics = {c: compute_metrics(data[c]) for c in configs}

    labels = [MODEL_DISPLAY[c] for c in configs]
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
    ax.set_title('Overall Accuracy & Parseability by Model')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.15)
    ax.legend()

    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt='%.2f', fontsize=9, padding=2)

    savefig(fig, os.path.join(OUT, 'chart05_overall_accuracy.png'))


def chart06_accuracy_vs_size():
    """Scatter/line: accuracy vs model size (1.5B, 7B, 13B)."""
    data = load_all_data()
    configs = MODEL_CONFIGS

    sizes  = [MODEL_SIZES[c] for c in configs]
    soft   = [data[c]['judge_answer_credit'].mean() for c in configs]
    strict = [(data[c]['judge_answer_judgment'] == 'correct').mean() for c in configs]
    colors = [MODEL_COLORS[c] for c in configs]

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(sizes, soft, 'o--', color='#2196F3', markersize=12, linewidth=2, label='Soft Accuracy')
    ax.plot(sizes, strict, 's--', color='#FF9800', markersize=12, linewidth=2, label='Strict Accuracy')

    for i, c in enumerate(configs):
        ax.annotate(MODEL_DISPLAY_INLINE[c], (sizes[i], soft[i]),
                    textcoords="offset points", xytext=(10, 10), fontsize=10)

    ax.set_xlabel('Model Size (Billion Parameters)')
    ax.set_ylabel('Accuracy')
    ax.set_title('Accuracy vs Model Size — "Bigger ≠ Better"')
    ax.set_xscale('log')
    ax.set_xticks(sizes)
    ax.set_xticklabels([f'{s}B' for s in sizes])
    ax.set_ylim(0, 1.0)
    ax.legend()
    savefig(fig, os.path.join(OUT, 'chart06_accuracy_vs_size.png'))


def chart07_per_category_accuracy():
    """Grouped bar: per-category soft accuracy by model."""
    data = load_all_data()
    configs = MODEL_CONFIGS

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(CATEGORIES))
    w = 0.25

    for i, c in enumerate(configs):
        df = data[c]
        accs = [df[df['question_category'] == cat]['judge_answer_credit'].mean()
                for cat in CATEGORIES]
        bars = ax.bar(x + (i - 1) * w, accs, w,
                      label=MODEL_DISPLAY_INLINE[c], color=list(MODEL_COLORS.values())[i])
        ax.bar_label(bars, fmt='%.2f', fontsize=8, padding=2)

    ax.set_ylabel('Soft Accuracy')
    ax.set_title('Per-Category Accuracy by Model')
    ax.set_xticks(x)
    ax.set_xticklabels([CATEGORY_SHORT[c] for c in CATEGORIES], rotation=15, ha='right')
    ax.set_ylim(0, 1.15)
    ax.legend()
    savefig(fig, os.path.join(OUT, 'chart07_per_category_accuracy.png'))


def chart08_error_distribution():
    """Stacked bar: error type distribution by model."""
    data = load_all_data()
    configs = MODEL_CONFIGS

    error_types_no_none = [e for e in ERROR_TYPES if e != 'none']
    counts = {}
    for c in configs:
        df = data[c]
        total = len(df)
        dist = df['judge_error_type'].value_counts()
        counts[c] = [dist.get(e, 0) / total for e in error_types_no_none]

    fig, ax = plt.subplots(figsize=(10, 7))
    x = np.arange(len(configs))
    bottom = np.zeros(len(configs))

    cmap = plt.cm.Set3(np.linspace(0, 1, len(error_types_no_none)))
    for i, etype in enumerate(error_types_no_none):
        vals = [counts[c][i] for c in configs]
        ax.bar(x, vals, 0.5, bottom=bottom, label=ERROR_DISPLAY[etype], color=cmap[i])
        bottom += vals

    ax.set_ylabel('Proportion of Responses')
    ax.set_title('Error Type Distribution by Model')
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_DISPLAY_INLINE[c] for c in configs])
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
    savefig(fig, os.path.join(OUT, 'chart08_error_distribution.png'))


def chart09_latency_distribution():
    """Violin plot: latency distribution by model."""
    data = load_all_data()
    configs = MODEL_CONFIGS

    plot_data = []
    for c in configs:
        df = data[c][['latency']].copy()
        df['Model'] = MODEL_DISPLAY_INLINE[c]
        plot_data.append(df)
    plot_df = pd.concat(plot_data, ignore_index=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    order = [MODEL_DISPLAY_INLINE[c] for c in configs]
    colors = [MODEL_COLORS[c] for c in configs]
    palette = dict(zip(order, colors))

    sns.violinplot(data=plot_df, x='Model', y='latency', order=order,
                   palette=palette, inner='quartile', ax=ax)
    ax.set_ylabel('Latency (seconds)')
    ax.set_title('Latency Distribution by Model')

    # Add median annotations
    for i, c in enumerate(configs):
        med = data[c]['latency'].median()
        ax.annotate(f'med={med:.1f}s', (i, med), textcoords="offset points",
                    xytext=(30, 0), fontsize=9, ha='left',
                    arrowprops=dict(arrowstyle='->', color='gray'))

    savefig(fig, os.path.join(OUT, 'chart09_latency_distribution.png'))


def chart10_accuracy_vs_latency():
    """Scatter: accuracy vs latency tradeoff (all 5 GPU configs)."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS

    fig, ax = plt.subplots(figsize=(10, 7))

    for c in configs:
        df = data[c]
        acc = df['judge_answer_credit'].mean()
        lat = df['latency'].mean()
        ax.scatter(lat, acc, s=150, c=CONFIG_COLORS[c], edgecolors='black',
                   linewidth=1, zorder=5)
        ax.annotate(CONFIG_DISPLAY[c], (lat, acc), textcoords="offset points",
                    xytext=(10, 8), fontsize=9)

    ax.set_xlabel('Average Latency (seconds)')
    ax.set_ylabel('Soft Accuracy')
    ax.set_title('Accuracy vs Latency Tradeoff (All GPU Configurations)')
    savefig(fig, os.path.join(OUT, 'chart10_accuracy_vs_latency.png'))


if __name__ == '__main__':
    setup_style()
    print('RQ2: Generating charts...')
    chart05_overall_accuracy()
    chart06_accuracy_vs_size()
    chart07_per_category_accuracy()
    chart08_error_distribution()
    chart09_latency_distribution()
    chart10_accuracy_vs_latency()
    print('RQ2: Done.')
