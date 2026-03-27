ssh fahim@35.39.206.19

tmux new -s xps3e2

tmux attach -t mysession

tmux kill-session -t mysession

tail -f tmux-logs/s3e2_mistral_limit50.log

watch -n 1 nvidia-smi

htop

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

---

PYTHONUNBUFFERED=1 python generate.py --model mistralai/Mistral-7B-Instruct-v0.3 --experiment 2 --strategy 1

PYTHONUNBUFFERED=1 python generate.py --model mistralai/Mistral-7B-Instruct-v0.3 --experiment 2 --strategy 3 --limit 1

PYTHONUNBUFFERED=1 python generate.py \
 --model mistralai/Mistral-7B-Instruct-v0.3 \
 --experiment 2 \
 --strategy 1 \
 --limit 25 \
 --offset 25

PYTHONUNBUFFERED=1 python3 generate.py --model gpt2 --experiment 2 --strategy 3 --limit 1

PYTHONUNBUFFERED=1 python generate.py --model mistralai/Mistral-7B-Instruct-v0.3 --experiment 2 --strategy 3 --limit 50 > tmux-logs/s3e2_mistral_limit50.log 2>&1
