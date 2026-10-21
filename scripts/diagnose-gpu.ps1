Write-Host "=== Windows NVIDIA driver ==="
nvidia-smi
Write-Host "=== Docker GPU visibility ==="
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
Write-Host "=== FFmpeg NVENC encoder ==="
docker compose exec api ffmpeg -hide_banner -encoders | Select-String "h264_nvenc"
Write-Host "=== Actual NVENC test ==="
docker compose exec api ffmpeg -hide_banner -loglevel error -f lavfi -i color=c=black:s=64x64:d=0.1 -frames:v 1 -c:v h264_nvenc -f null -
