"""
Summary tables for the thesis.
Generates T1 (master results), T2 (per-category accuracy), T3 (error taxonomy).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import *

OUT = os.path.dirname(os.path.abspath(__file__))


def table_t1_master_results():
    """T1: One row per config with key metrics."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS

    rows = []
    for c in configs:
        m = compute_metrics(data[c])
        rows.append({
            'Configuration': CONFIG_DISPLAY[c],
            'Strategy': data[c]['strategy'].iloc[0],
            'Model': data[c]['model_name'].iloc[0],
            'N': m['n'],
            'Soft Accuracy': round(m['soft_accuracy'], 4),
            'Strict Accuracy': round(m['strict_accuracy'], 4),
            'Parseability': round(m['parseability'], 4),
            'Avg Latency (s)': round(m['avg_latency'], 2),
            'Median Latency (s)': round(m['median_latency'], 2),
            'Avg Input Tokens': round(m['avg_input_tokens'], 0),
            'Avg Output Tokens': round(m['avg_output_tokens'], 0),
        })

    df = pd.DataFrame(rows)
    path = os.path.join(OUT, 'T1_master_results.csv')
    df.to_csv(path, index=False)
    print(f'  Saved: T1_master_results.csv')
    print(df.to_string(index=False))
    return df


def table_t2_per_category():
    """T2: Rows = 6 question categories, columns = each config's soft accuracy."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS

    rows = []
    for cat in CATEGORIES:
        row = {'Question Category': cat}
        for c in configs:
            df = data[c]
            acc = df[df['question_category'] == cat]['judge_answer_credit'].mean()
            row[CONFIG_DISPLAY[c]] = round(acc, 4)
        rows.append(row)

    df = pd.DataFrame(rows)
    path = os.path.join(OUT, 'T2_per_category_accuracy.csv')
    df.to_csv(path, index=False)
    print(f'  Saved: T2_per_category_accuracy.csv')
    print(df.to_string(index=False))
    return df


def table_t3_error_taxonomy():
    """T3: Error type definitions and counts per config."""
    data = load_all_data()
    configs = ALL_GPU_CONFIGS

    ERROR_DEFINITIONS = {
        'none': 'Answer is correct; no error present.',
        'missing_detail': 'Answer omits details present in the ground truth.',
        'contradiction_to_ground_truth': 'Answer directly contradicts the ground truth.',
        'wrong_entity': 'Answer references the wrong person, organization, or entity.',
        'not_answered': 'Model failed to answer or explicitly declined.',
        'invented_value_for_missing_ground_truth': 'Model fabricated a value when ground truth had none.',
        'wrong_numeric_value': 'Numerical value (date, count, GPA) is incorrect.',
        'extra_unsupported_detail': 'Answer includes information not in the source CV.',
        'wrong_boolean': 'Yes/no or true/false answer is inverted.',
        'format_issue': 'Answer is correct but formatted unusably.',
        'other': 'Error does not fit any defined category.',
    }

    rows = []
    for etype in ERROR_TYPES:
        row = {
            'Error Type': ERROR_DISPLAY[etype],
            'Definition': ERROR_DEFINITIONS[etype],
        }
        total = 0
        for c in configs:
            count = (data[c]['judge_error_type'] == etype).sum()
            row[CONFIG_DISPLAY[c]] = count
            total += count
        row['Total'] = total
        rows.append(row)

    df = pd.DataFrame(rows)
    path = os.path.join(OUT, 'T3_error_taxonomy.csv')
    df.to_csv(path, index=False)
    print(f'  Saved: T3_error_taxonomy.csv')
    print(df.to_string(index=False))
    return df


if __name__ == '__main__':
    print('Tables: Generating...')
    table_t1_master_results()
    print()
    table_t2_per_category()
    print()
    table_t3_error_taxonomy()
    print('\nTables: Done.')
