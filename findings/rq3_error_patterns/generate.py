"""
RQ3: What question types and error patterns emerge?
Cross-cutting analysis across all configurations.
Generates charts 11–16.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import *
from matplotlib.patches import FancyBboxPatch

OUT = os.path.dirname(os.path.abspath(__file__))


def chart11_error_heatmap():
    """Heatmap: error type x config matrix."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS
    error_types_no_none = [e for e in ERROR_TYPES if e != 'none']

    matrix = []
    for c in configs:
        df = data[c]
        total = len(df)
        dist = df['judge_error_type'].value_counts()
        row = [dist.get(e, 0) / total * 100 for e in error_types_no_none]
        matrix.append(row)

    matrix_df = pd.DataFrame(
        matrix,
        index=[CONFIG_DISPLAY[c] for c in configs],
        columns=[ERROR_DISPLAY[e] for e in error_types_no_none]
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(matrix_df, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
                cbar_kws={'label': '% of Responses'}, linewidths=0.5)
    ax.set_title('Error Type Distribution Across Configurations (%)')
    ax.set_ylabel('')
    plt.xticks(rotation=30, ha='right')
    savefig(fig, os.path.join(OUT, 'chart11_error_heatmap.png'))


def chart12_answer_type_by_strategy():
    """Grouped bar: accuracy by answer type x strategy."""
    data = load_all_data()
    configs = STRATEGY_CONFIGS

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(configs))
    w = 0.3

    for j, atype in enumerate(['Entity/Numeric', 'Descriptive']):
        accs = []
        for c in configs:
            df = add_answer_type(data[c])
            accs.append(df[df['answer_type'] == atype]['judge_answer_credit'].mean())
        color = '#2196F3' if atype == 'Entity/Numeric' else '#FF9800'
        bars = ax.bar(x + (j - 0.5) * w, accs, w, label=atype, color=color)
        ax.bar_label(bars, fmt='%.2f', fontsize=9, padding=2)

    ax.set_ylabel('Soft Accuracy')
    ax.set_title('Accuracy by Answer Type × Retrieval Strategy')
    ax.set_xticks(x)
    ax.set_xticklabels([STRATEGY_DISPLAY[c] for c in configs])
    ax.set_ylim(0, 1.15)
    ax.legend()
    savefig(fig, os.path.join(OUT, 'chart12_answer_type_by_strategy.png'))


def chart13_answer_type_by_model():
    """Grouped bar: accuracy by answer type x model."""
    data = load_all_data()
    configs = MODEL_CONFIGS

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(configs))
    w = 0.3

    for j, atype in enumerate(['Entity/Numeric', 'Descriptive']):
        accs = []
        for c in configs:
            df = add_answer_type(data[c])
            accs.append(df[df['answer_type'] == atype]['judge_answer_credit'].mean())
        color = '#2196F3' if atype == 'Entity/Numeric' else '#FF9800'
        bars = ax.bar(x + (j - 0.5) * w, accs, w, label=atype, color=color)
        ax.bar_label(bars, fmt='%.2f', fontsize=9, padding=2)

    ax.set_ylabel('Soft Accuracy')
    ax.set_title('Accuracy by Answer Type × Model')
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_DISPLAY_INLINE[c] for c in configs])
    ax.set_ylim(0, 1.15)
    ax.legend()
    savefig(fig, os.path.join(OUT, 'chart13_answer_type_by_model.png'))


def chart14_radar_category():
    """Radar/spider chart: per-category accuracy profile per config."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS
    n_cats = len(CATEGORIES)

    angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

    for c in configs:
        df = data[c]
        vals = [df[df['question_category'] == cat]['judge_answer_credit'].mean()
                for cat in CATEGORIES]
        vals += vals[:1]
        ax.plot(angles, vals, 'o-', linewidth=2, label=CONFIG_DISPLAY[c],
                color=CONFIG_COLORS[c], markersize=5)
        ax.fill(angles, vals, alpha=0.05, color=CONFIG_COLORS[c])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([CATEGORY_SHORT[c] for c in CATEGORIES], fontsize=10)
    ax.set_ylim(0, 1.0)
    ax.set_title('Per-Category Accuracy Profile by Configuration', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=9)
    savefig(fig, os.path.join(OUT, 'chart14_radar_category.png'))


def chart15_top_errors():
    """Horizontal bar: top error types overall (sorted descending)."""
    combined = load_combined()
    error_types_no_none = [e for e in ERROR_TYPES if e != 'none']

    counts = combined[combined['judge_error_type'] != 'none']['judge_error_type'].value_counts()
    # Reindex to our defined order, then sort by count
    counts = counts.reindex(error_types_no_none).dropna().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [ERROR_DISPLAY.get(e, e) for e in counts.index]
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(counts)))

    bars = ax.barh(labels, counts.values, color=colors)
    ax.bar_label(bars, fmt='%.0f', fontsize=9, padding=4)
    ax.set_xlabel('Count (across all GPU configurations)')
    ax.set_title('Most Common Error Types (Excluding "None")')
    savefig(fig, os.path.join(OUT, 'chart15_top_errors.png'))


def chart16_per_cv_accuracy():
    """Boxplot: per-CV accuracy spread across configs."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS

    plot_data = []
    for c in configs:
        df = data[c]
        cv_acc = df.groupby('cv_id')['judge_answer_credit'].mean().reset_index()
        cv_acc['config'] = CONFIG_DISPLAY[c]
        plot_data.append(cv_acc)
    plot_df = pd.concat(plot_data, ignore_index=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    order = [CONFIG_DISPLAY[c] for c in configs]
    colors = [CONFIG_COLORS[c] for c in configs]
    palette = dict(zip(order, colors))

    sns.boxplot(data=plot_df, x='config', y='judge_answer_credit',
                order=order, palette=palette, ax=ax, width=0.5)
    ax.set_xlabel('')
    ax.set_ylabel('Mean Soft Accuracy per CV')
    ax.set_title('Per-CV Accuracy Distribution — Consistency Across Configurations')
    plt.xticks(rotation=15, ha='right')
    savefig(fig, os.path.join(OUT, 'chart16_per_cv_accuracy.png'))


if __name__ == '__main__':
    setup_style()
    print('RQ3: Generating charts...')
    chart11_error_heatmap()
    chart12_answer_type_by_strategy()
    chart13_answer_type_by_model()
    chart14_radar_category()
    chart15_top_errors()
    chart16_per_cv_accuracy()
    print('RQ3: Done.')
