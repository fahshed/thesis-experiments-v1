"""
Shared data loading, config, and styling for all thesis visualizations.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

# ── Data file paths ──────────────────────────────────────────────────────────
DATA_FILES = {
    'S1 Mistral GPU': os.path.join(RESULTS_DIR, 's1e2 mistral (1-50) (gpu)',
                                   '20260327_175113_s1_e2_limit50_offset0_generated_answers.csv'),
    'S1 Mistral CPU': os.path.join(RESULTS_DIR, 's1e2 mistral (1~45) (cpu)',
                                   'merged_generated_answers.csv'),
    'S1 Qwen':        os.path.join(RESULTS_DIR, 's1e2 qwen (1-50)',
                                   '20260327_213414_s1_e2_limit50_offset0_generated_answers.csv'),
    'S1 LLaMA':       os.path.join(RESULTS_DIR, 's1e2 llama (1-50) i3 ',
                                   '20260328_000306_s1_e2_limit50_offset0_generated_answers.csv'),
    'S2 Mistral':     os.path.join(RESULTS_DIR, 's2e2 mistral (1-50)',
                                   '20260327_020011_s2_e2_limit50_offset0_generated_answers.csv'),
    'S3 Mistral':     os.path.join(RESULTS_DIR, 's3e2 mistral (1-50)',
                                   '20260327_010014_s3_e2_limit50_offset0_generated_answers.csv'),
}

# ── Config groupings ─────────────────────────────────────────────────────────
STRATEGY_CONFIGS = ['S1 Mistral GPU', 'S2 Mistral', 'S3 Mistral']
MODEL_CONFIGS    = ['S1 Qwen', 'S1 Mistral GPU', 'S1 LLaMA']
ALL_GPU_CONFIGS  = ['S1 Qwen', 'S1 Mistral GPU', 'S1 LLaMA', 'S2 Mistral', 'S3 Mistral']

# ── Colors ───────────────────────────────────────────────────────────────────
STRATEGY_COLORS = {
    'S1 Mistral GPU': '#2196F3',
    'S2 Mistral':     '#FF9800',
    'S3 Mistral':     '#4CAF50',
}
MODEL_COLORS = {
    'S1 Qwen':        '#9C27B0',
    'S1 Mistral GPU': '#2196F3',
    'S1 LLaMA':       '#F44336',
}
CONFIG_COLORS = {
    'S1 Mistral GPU': '#2196F3', 'S1 Mistral CPU': '#90CAF9',
    'S1 Qwen':        '#9C27B0', 'S1 LLaMA':       '#F44336',
    'S2 Mistral':     '#FF9800', 'S3 Mistral':      '#4CAF50',
}

# ── Category ordering ────────────────────────────────────────────────────────
CATEGORIES = [
    'Personal Information', 'Education', 'Professional Experience',
    'Skills', 'Research and Projects', 'Awards & Extracurricular Activities',
]
CATEGORY_SHORT = {
    'Personal Information': 'Personal Info',
    'Education': 'Education',
    'Professional Experience': 'Prof. Exp.',
    'Skills': 'Skills',
    'Research and Projects': 'Research & Projects',
    'Awards & Extracurricular Activities': 'Awards & Extra.',
}

# ── Answer type mapping ──────────────────────────────────────────────────────
ENTITY_NUMERIC_CATEGORIES = {'Personal Information', 'Education', 'Skills',
                             'Awards & Extracurricular Activities'}
DESCRIPTIVE_CATEGORIES    = {'Professional Experience', 'Research and Projects'}

# ── Display names ────────────────────────────────────────────────────────────
MODEL_SIZES   = {'S1 Qwen': 1.5, 'S1 Mistral GPU': 7, 'S1 LLaMA': 13}
MODEL_DISPLAY = {
    'S1 Qwen':        'Qwen-2.5\n(1.5B)',
    'S1 Mistral GPU': 'Mistral-7B',
    'S1 LLaMA':       'LLaMA-2\n(13B)',
}
MODEL_DISPLAY_INLINE = {
    'S1 Qwen':        'Qwen-2.5 (1.5B)',
    'S1 Mistral GPU': 'Mistral-7B',
    'S1 LLaMA':       'LLaMA-2 (13B)',
}
STRATEGY_DISPLAY = {
    'S1 Mistral GPU': 'S1: Full CV',
    'S2 Mistral':     'S2: Keyword',
    'S3 Mistral':     'S3: Semantic RAG',
}
CONFIG_DISPLAY = {
    'S1 Mistral GPU': 'S1 Mistral (GPU)',
    'S1 Mistral CPU': 'S1 Mistral (CPU)',
    'S1 Qwen':        'S1 Qwen-2.5 (1.5B)',
    'S1 LLaMA':       'S1 LLaMA-2 (13B)',
    'S2 Mistral':     'S2 Mistral-7B',
    'S3 Mistral':     'S3 Mistral-7B',
}

# ── Error types (ordered by expected frequency) ─────────────────────────────
ERROR_TYPES = [
    'none', 'missing_detail', 'contradiction_to_ground_truth', 'wrong_entity',
    'not_answered', 'invented_value_for_missing_ground_truth', 'wrong_numeric_value',
    'extra_unsupported_detail', 'wrong_boolean', 'format_issue', 'other',
]
ERROR_DISPLAY = {
    'none': 'None (Correct)',
    'missing_detail': 'Missing Detail',
    'contradiction_to_ground_truth': 'Contradiction',
    'wrong_entity': 'Wrong Entity',
    'not_answered': 'Not Answered',
    'invented_value_for_missing_ground_truth': 'Invented Value',
    'wrong_numeric_value': 'Wrong Numeric',
    'extra_unsupported_detail': 'Extra Detail',
    'wrong_boolean': 'Wrong Boolean',
    'format_issue': 'Format Issue',
    'other': 'Other',
}

# ── Data loading ─────────────────────────────────────────────────────────────

def load_all_data():
    """Load all CSV files; returns dict of {config_name: DataFrame}."""
    data = {}
    for name, path in DATA_FILES.items():
        df = pd.read_csv(path)
        df['config'] = name
        data[name] = df
    return data


def load_configs(config_list):
    """Load and concatenate specific configs into one DataFrame."""
    all_data = load_all_data()
    frames = [all_data[k] for k in config_list]
    return pd.concat(frames, ignore_index=True)


def load_combined():
    """Load all GPU configs into a single DataFrame."""
    return load_configs(ALL_GPU_CONFIGS)


def add_answer_type(df):
    """Add answer_type column based on question_category."""
    df = df.copy()
    df['answer_type'] = df['question_category'].apply(
        lambda x: 'Entity/Numeric' if x in ENTITY_NUMERIC_CATEGORIES else 'Descriptive'
    )
    return df


def compute_metrics(df):
    """Compute key metrics for a DataFrame group."""
    return {
        'soft_accuracy':  df['judge_answer_credit'].mean(),
        'strict_accuracy': (df['judge_answer_judgment'] == 'correct').mean(),
        'parseability':   df['raw_response_parsable'].mean(),
        'avg_latency':    df['latency'].mean(),
        'median_latency': df['latency'].median(),
        'avg_input_tokens':  df['input_tokens'].mean(),
        'avg_output_tokens': df['output_tokens'].mean(),
        'n': len(df),
    }


def get_gpu_cpu_matched():
    """Get GPU and CPU DataFrames clipped to matching CV/question pairs."""
    all_data = load_all_data()
    gpu = all_data['S1 Mistral GPU']
    cpu = all_data['S1 Mistral CPU']
    common_ids = set(cpu['question_id']).intersection(set(gpu['question_id']))
    gpu_matched = gpu[gpu['question_id'].isin(common_ids)].copy()
    cpu_matched = cpu[cpu['question_id'].isin(common_ids)].copy()
    return gpu_matched, cpu_matched


# ── Plot styling ─────────────────────────────────────────────────────────────

def setup_style():
    """Set up consistent matplotlib style for all charts."""
    plt.rcParams.update({
        'figure.figsize': (10, 6),
        'figure.dpi': 150,
        'savefig.dpi': 150,
        'savefig.bbox': 'tight',
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.spines.top': False,
        'axes.spines.right': False,
    })
    sns.set_palette("muted")


def add_bar_labels(ax, fmt='.1%', fontsize=9):
    """Add value labels on top of bars."""
    for container in ax.containers:
        labels = [f'{v.get_height():{fmt[1:]}}' if fmt.startswith('.') else f'{v.get_height():{fmt}}'
                  for v in container]
        ax.bar_label(container, labels=labels, fontsize=fontsize, padding=2)


def savefig(fig, path):
    """Save figure and close."""
    fig.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved: {os.path.basename(path)}')
