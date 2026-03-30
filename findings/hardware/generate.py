"""
Separate Finding: Hardware Impact (GPU vs CPU).
Comparison: Mistral S1 on GPU vs CPU (clipped to matching records).
Generates charts 22–23.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import *

OUT = os.path.dirname(os.path.abspath(__file__))


def chart22_latency_comparison():
    """Bar: GPU vs CPU latency for Mistral S1."""
    gpu, cpu = get_gpu_cpu_matched()

    labels = ['GPU', 'CPU']
    avg_lat = [gpu['latency'].mean(), cpu['latency'].mean()]
    med_lat = [gpu['latency'].median(), cpu['latency'].median()]
    colors = ['#2196F3', '#90CAF9']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Average latency
    bars1 = ax1.bar(labels, avg_lat, color=colors, width=0.4, edgecolor='black', linewidth=0.5)
    ax1.set_ylabel('Average Latency (seconds)')
    ax1.set_title('Average Latency: GPU vs CPU')
    ax1.bar_label(bars1, fmt='%.2f', fontsize=12, padding=4)

    # Median latency
    bars2 = ax2.bar(labels, med_lat, color=colors, width=0.4, edgecolor='black', linewidth=0.5)
    ax2.set_ylabel('Median Latency (seconds)')
    ax2.set_title('Median Latency: GPU vs CPU')
    ax2.bar_label(bars2, fmt='%.2f', fontsize=12, padding=4)

    # Speedup annotation
    speedup = avg_lat[1] / avg_lat[0]
    fig.suptitle(
        f'Mistral-7B S1: GPU is {speedup:.0f}× faster than CPU',
        fontsize=14,
        fontweight='bold',
        y=1.05,
    )
    fig.tight_layout()
    savefig(fig, os.path.join(OUT, 'chart22_latency_comparison.png'))


def chart23_accuracy_comparison():
    """Grouped bar: GPU vs CPU accuracy comparison."""
    gpu, cpu = get_gpu_cpu_matched()

    gpu_m = compute_metrics(gpu)
    cpu_m = compute_metrics(cpu)

    labels = ['Soft Accuracy', 'Strict Accuracy', 'Parseability']
    gpu_vals = [gpu_m['soft_accuracy'], gpu_m['strict_accuracy'], gpu_m['parseability']]
    cpu_vals = [cpu_m['soft_accuracy'], cpu_m['strict_accuracy'], cpu_m['parseability']]

    x = np.arange(len(labels))
    w = 0.3

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - w/2, gpu_vals, w, label='GPU', color='#2196F3')
    bars2 = ax.bar(x + w/2, cpu_vals, w, label='CPU', color='#90CAF9')

    ax.set_ylabel('Rate')
    ax.set_title('Accuracy Comparison: GPU vs CPU (Mistral-7B S1)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.15)
    ax.legend()

    for bars in [bars1, bars2]:
        ax.bar_label(bars, fmt='%.3f', fontsize=10, padding=2)

    savefig(fig, os.path.join(OUT, 'chart23_accuracy_comparison.png'))


if __name__ == '__main__':
    setup_style()
    print('Hardware: Generating charts...')
    chart22_latency_comparison()
    chart23_accuracy_comparison()
    print('Hardware: Done.')
