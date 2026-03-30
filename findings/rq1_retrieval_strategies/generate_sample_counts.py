"""
Generate a chart showing sample counts behind each accuracy bar.
For each strategy: count of soft-correct, strict-correct, and parseable rows.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import *

OUT = os.path.dirname(os.path.abspath(__file__))


def chart_sample_counts():
    """Grouped bar: number of rows contributing to each metric by strategy."""
    data = load_all_data()
    configs = STRATEGY_CONFIGS
    metrics = {}
    for c in configs:
        df = data[c]
        n = len(df)
        metrics[c] = {
            'soft_n': int(round(df['judge_answer_credit'].sum())),
            'strict_n': int((df['judge_answer_judgment'] == 'correct').sum()),
            'parseable_n': int(df['raw_response_parsable'].sum()),
            'total': n,
        }

    labels = [STRATEGY_DISPLAY[c] for c in configs]
    soft_n   = [metrics[c]['soft_n'] for c in configs]
    strict_n = [metrics[c]['strict_n'] for c in configs]
    parse_n  = [metrics[c]['parseable_n'] for c in configs]

    x = np.arange(len(labels))
    w = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - w, soft_n,   w, label='Soft Correct',     color='#2196F3')
    bars2 = ax.bar(x,     strict_n, w, label='Strict Correct',   color='#FF9800')
    bars3 = ax.bar(x + w, parse_n,  w, label='Parseable',        color='#4CAF50')

    ax.set_ylabel('Number of Rows')
    ax.set_title('Sample Counts by Retrieval Strategy (N = 1500 per config)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    for bars in [bars1, bars2, bars3]:
        ax.bar_label(bars, fmt='%d', fontsize=9, padding=2)

    # Add a bit of headroom for labels
    ax.set_ylim(0, max(max(soft_n), max(strict_n), max(parse_n)) * 1.15)

    savefig(fig, os.path.join(OUT, 'chart01b_sample_counts.png'))


if __name__ == '__main__':
    setup_style()
    print('Generating sample counts chart...')
    chart_sample_counts()
    print('Done.')
