ssh fahim@35.39.206.19

tmux new -s xps3e2

tmux attach -t mysession

tmux kill-session -t mysession

tail -f tmux-logs/s3e2_mistral_limit50.log

watch -n 1 nvidia-smi

htop

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

---

PYTHONUNBUFFERED=1 python generate.py --model mistralai/Mistral-7B-Instruct-v0.3 --experiment 2 --strategy 1 --limit 50 > tmux-logs/s1e2_mistral_limit50.log 2>&1

PYTHONUNBUFFERED=1 python generate.py --model mistralai/Mistral-7B-Instruct-v0.3 --experiment 2 --strategy 3 --limit 1

PYTHONUNBUFFERED=1 python generate.py \
 --model mistralai/Mistral-7B-Instruct-v0.3 \
 --experiment 2 \
 --strategy 1 \
 --limit 25 \
 --offset 25

PYTHONUNBUFFERED=1 python3 generate.py --model gpt2 --experiment 2 --strategy 3 --limit 1

PYTHONUNBUFFERED=1 python generate.py --model mistralai/Mistral-7B-Instruct-v0.3 --experiment 2 --strategy 1 --limit 50 > tmux-logs/s1e2_mistral_gpu_limit50.log 2>&1

PYTHONUNBUFFERED=1 python generate.py --model mistralai/Mistral-7B-Instruct-v0.3 --experiment 2 --strategy 2 --limit 50 --offset 0 > tmux-logs/s2e2_mistral_limit50.log 2>&1

PYTHONUNBUFFERED=1 python generate.py --model meta-llama/Llama-2-13b-chat-hf --experiment 2 --strategy 1 --limit 50 > tmux-logs/s1e2_llama13b_limit50.log 2>&1

PYTHONUNBUFFERED=1 python generate.py --model Qwen/Qwen2.5-1.5B-Instruct --experiment 2 --strategy 1 --limit 50 > tmux-logs/s1e2_qwen2b_limit50.log 2>&1

PYTHONUNBUFFERED=1 python generate.py --model meta-llama/Llama-2-13b-chat-hf --experiment 2 --strategy 1 --limit 50 --offset 0 > tmux-logs/s1e2i2_llama13b_limit50.log 2>&1

---

python3 scripts/judge_results_with_gemini.py "results/s1e2 mistral (1-50) (gpu)/20260327_175113_s1_e2_limit50_offset0_generated_answers.csv"

python3 scripts/judge_results_with_gemini.py "results/s1e2 qwen (1-50)/20260327_213414_s1_e2_limit50_offset0_generated_answers.csv"

python3 scripts/judge_results_with_gemini.py "results/s1e2 llama (1-50) i3 /20260328_000306_s1_e2_limit50_offset0_generated_answers.csv"

python3 scripts/judge_results_with_gemini.py "results/s2e2 mistral (1-50)/20260327_020011_s2_e2_limit50_offset0_generated_answers.csv"

python3 scripts/judge_results_with_gemini.py "results/s3e2 mistral (1-50)/20260327_010014_s3_e2_limit50_offset0_generated_answers.csv"

python3 scripts/judge_results_with_gemini.py "results/s1e2 mistral (1~45) (cpu)/merged_generated_answers.csv"
