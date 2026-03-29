"""
RQ4: How well do confidence scores and rationales correlate with correctness?
Cross-cutting analysis across all configurations.
Generates charts 17–21.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import *

OUT = os.path.dirname(os.path.abspath(__file__))


def chart17_calibration():
    """Calibration plot: confidence bucket vs actual accuracy."""
    combined = load_combined()

    # Only use rows where confidence is not NaN
    df = combined.dropna(subset=['confidence_score', 'judge_answer_credit'])

    # Bin confidence into buckets
    bins = np.arange(0, 1.1, 0.1)
    df = df.copy()
    df['conf_bucket'] = pd.cut(df['confidence_score'], bins=bins, include_lowest=True)

    cal = df.groupby('conf_bucket', observed=True).agg(
        mean_conf=('confidence_score', 'mean'),
        mean_acc=('judge_answer_credit', 'mean'),
        count=('judge_answer_credit', 'count')
    ).reset_index()

    fig, ax = plt.subplots(figsize=(8, 8))
    # Perfect calibration line
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect Calibration')

    # Calibration curve
    ax.plot(cal['mean_conf'], cal['mean_acc'], 'o-', color='#2196F3',
            markersize=10, linewidth=2, label='Observed')

    # Size annotations
    for _, row in cal.iterrows():
        if row['count'] > 10:
            ax.annotate(f"n={int(row['count'])}", (row['mean_conf'], row['mean_acc']),
                        textcoords="offset points", xytext=(8, -10), fontsize=8, color='gray')

    ax.set_xlabel('Mean Predicted Confidence')
    ax.set_ylabel('Mean Actual Accuracy (Judge Credit)')
    ax.set_title('Confidence Calibration Plot')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.legend()
    savefig(fig, os.path.join(OUT, 'chart17_calibration.png'))


def chart18_confidence_histogram():
    """Histogram: confidence score distribution across all configs."""
    combined = load_combined()
    df = combined.dropna(subset=['confidence_score'])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['confidence_score'], bins=20, range=(0, 1), color='#2196F3',
            edgecolor='white', alpha=0.8)
    ax.axvline(df['confidence_score'].median(), color='red', linestyle='--',
               linewidth=2, label=f"Median = {df['confidence_score'].median():.2f}")
    ax.set_xlabel('Confidence Score')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of LLM Confidence Scores (All GPU Configs)')
    ax.legend()

    # Add percentage annotation for 0.8-1.0 range
    high_conf = (df['confidence_score'] >= 0.8).mean()
    ax.annotate(f'{high_conf:.0%} of scores\nin [0.8, 1.0]',
                xy=(0.9, ax.get_ylim()[1] * 0.7), fontsize=12, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

    savefig(fig, os.path.join(OUT, 'chart18_confidence_histogram.png'))


def chart19_confidence_by_judgment():
    """Violin/overlapping histogram: confidence split by judgment."""
    combined = load_combined()
    df = combined.dropna(subset=['confidence_score', 'judge_answer_judgment'])

    fig, ax = plt.subplots(figsize=(10, 6))
    order = ['correct', 'partial', 'incorrect']
    colors = {'correct': '#4CAF50', 'partial': '#FF9800', 'incorrect': '#F44336'}
    palette = {k: colors[k] for k in order}

    sns.violinplot(data=df, x='judge_answer_judgment', y='confidence_score',
                   order=order, palette=palette, inner='quartile', ax=ax)

    ax.set_xlabel('Judge Answer Judgment')
    ax.set_ylabel('Confidence Score')
    ax.set_title('Confidence Score Distribution by Correctness')

    # Add median annotations
    for i, j in enumerate(order):
        med = df[df['judge_answer_judgment'] == j]['confidence_score'].median()
        ax.annotate(f'med={med:.2f}', (i, med), textcoords="offset points",
                    xytext=(30, 0), fontsize=9, ha='left',
                    arrowprops=dict(arrowstyle='->', color='gray'))

    savefig(fig, os.path.join(OUT, 'chart19_confidence_by_judgment.png'))


def chart20_rationale_quality():
    """Stacked bar: rationale judgment by model and strategy."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS
    judgments = ['correct', 'partial', 'incorrect']
    colors = {'correct': '#4CAF50', 'partial': '#FF9800', 'incorrect': '#F44336'}

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(configs))
    bottom = np.zeros(len(configs))

    for j in judgments:
        vals = []
        for c in configs:
            df = data[c]
            total = len(df)
            count = (df['judge_rationale_judgment'] == j).sum()
            vals.append(count / total)
        ax.bar(x, vals, 0.5, bottom=bottom, label=j.capitalize(), color=colors[j])
        bottom += vals

    ax.set_ylabel('Proportion')
    ax.set_title('Rationale Quality by Configuration')
    ax.set_xticks(x)
    ax.set_xticklabels([CONFIG_DISPLAY[c] for c in configs], rotation=15, ha='right')
    ax.set_ylim(0, 1.1)
    ax.legend()
    savefig(fig, os.path.join(OUT, 'chart20_rationale_quality.png'))


def chart21_answer_vs_rationale():
    """Heatmap (confusion-style): answer judgment x rationale judgment."""
    combined = load_combined()
    df = combined.dropna(subset=['judge_answer_judgment', 'judge_rationale_judgment'])

    judgments = ['correct', 'partial', 'incorrect']
    matrix = pd.crosstab(df['judge_answer_judgment'], df['judge_rationale_judgment'],
                         normalize='all') * 100
    # Reindex to desired order
    matrix = matrix.reindex(index=judgments, columns=judgments, fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(matrix, annot=True, fmt='.1f', cmap='Blues', ax=ax,
                cbar_kws={'label': '% of All Responses'}, linewidths=0.5,
                xticklabels=[j.capitalize() for j in judgments],
                yticklabels=[j.capitalize() for j in judgments])
    ax.set_xlabel('Rationale Judgment')
    ax.set_ylabel('Answer Judgment')
    ax.set_title('Answer Judgment vs Rationale Judgment\n(Right Answer with Wrong Reasoning?)')
    savefig(fig, os.path.join(OUT, 'chart21_answer_vs_rationale.png'))


if __name__ == '__main__':
    setup_style()
    print('RQ4: Generating charts...')
    chart17_calibration()
    chart18_confidence_histogram()
    chart19_confidence_by_judgment()
    chart20_rationale_quality()
    chart21_answer_vs_rationale()
    print('RQ4: Done.')
