# AGENTS.md: quy tắc cho agent làm việc trong repo này

Repo này là **bài nộp (entry)** cho cuộc thi Kaggle
[Google - Agent Harness on Physical-Engineering's Last Exam](https://www.kaggle.com/competitions/physical-engineerings-last-exam)
(PLE). Mọi agent (Claude Code, OpenCode, …) làm việc ở đây phải tuân thủ toàn bộ các quy tắc dưới đây.
Khi quy tắc ở đây mâu thuẫn với luật chính thức thì luật chính thức thắng; cập nhật lại file này.

- Hạn chót: **2027-01-05 23:59:59 UTC** (Kaggle). Giải: $250K / $100K / $50K.
- Luật chính thức: `docs/rules.md` trong kit, trang https://ple-bench.com/competition, tab Rules trên Kaggle.
- Kit chính thức: https://github.com/google-research/ple, clone tại `/home/ttlab/src/ple` (**ngoài** repo này).

## 1. Bài nộp là gì

Một commit GitHub chứa:

1. `submission.yaml` (khai báo `model_api`, `install`, `serve`).
2. Harness: WebSocket server (`serve.py` + file phụ) chạy trong container 2 CPU / 4 GB, nhận đề qua
   WebSocket, gửi lệnh shell / đọc-ghi file / gọi MCP sang task container (không có mạng).
3. `artifacts/`: kết quả chạy 29 task dev, **chỉ** được sinh bằng `uv run python eval/run.py <entry>` từ kit.

Ban tổ chức chạy harness trên 56 task ẩn (6 giờ/task). Điểm mỗi task 0–1; task thiết kế:
`s = 0.4·p + 0.6·G·O'` (vi phạm bất kỳ ràng buộc an toàn/khả thi nào thì `G = 0`).

## 2. Luật fair-play (vi phạm có thể bị loại)

- KHÔNG hard-code đáp án, KHÔNG nhận diện task cụ thể để rẽ nhánh (kể cả task dev).
- KHÔNG để harness đọc grader, file tham chiếu, `tests/`, hay `artifacts/` của chính nó (từ đĩa, git history, mạng).
- KHÔNG sửa tay, tạo, hay ghép file trong `artifacts/`. Chỉ export bằng `eval/run.py` từ đúng harness và
  đúng `model_api` đang commit. Được phép chạy lại từng task (`--tasks <id>`).
- KHÔNG gọi host nào ngoài endpoint model (không web search, không tool do nhà cung cấp host, không API ngoài).
- KHÔNG lưu, log, publish nội dung prompt/file của task test.
- `model_api` trong `submission.yaml` phải khớp model harness thực sự gọi, và bài nộp phải dùng
  `google-cloud/<id>`. Model khác (OpenCode, key riêng) chỉ dùng để thử local, không bao giờ để trong commit nộp.

## 3. Bảo mật và bí mật

- Key nằm trong `.env` (đã `.gitignore`): `KAGGLE_API_TOKEN`, `HF_TOKEN`, và sau này `OPENCODE_API_KEY`, `GITHUB_TOKEN`, …
- KHÔNG BAO GIỜ commit, in ra log, hay gửi key lên dịch vụ ngoài. Khi cần kiểm tra `.env` chỉ in tên biến:
  `sed -E 's/=.*/=<hidden>/' .env`.
- Trước mỗi commit: `git status` và kiểm tra không có key trong diff (`git diff --cached | grep -iE 'key|token|secret'`).
- Harness đọc URL/key model từ biến môi trường (`MODEL_BASE_URL`, `MODEL_API_KEY`, `OPENAI_*`, `ANTHROPIC_*`, `GEMINI_*`), không bao giờ hard-code.

## 4. Git

- Remote: `origin = https://github.com/Nguyenchitrai62/AHPELE.git`, nhánh `main`.
- **Luôn commit bằng tài khoản Nguyenchitrai62** (đã đặt trong `git config` local của repo):
  `user.name = Nguyenchitrai62`, `user.email = 121591111+Nguyenchitrai62@users.noreply.github.com`.
  Không đổi, không dùng identity global của máy (`thao_ttp`).
- Commit nhỏ, message rõ ràng. Commit chứa `artifacts/` phải chứa luôn đúng harness đã sinh ra chúng
  (`manifest.json` lưu hash harness).
- Repo giới hạn 1 GiB tính cả `.git`; `artifacts/` ≤ 512 MiB. Squash lịch sử nếu nhiều lần chạy dev làm repo phình to.
- Không force-push, không xoá lịch sử khi chưa được người dùng đồng ý.

## 5. Quy trình làm việc

1. Phát triển và debug harness bằng model rẻ (OpenCode, ví dụ DeepSeek) trên 1–3 task dev.
2. Kiểm tra trên model nộp bài (`google-cloud/claude-opus-5-5` hoặc `google-cloud/gemini-4-argon`) với vài task
   trước khi chạy đủ 29 task. Mỗi model có tham số API riêng: Opus 5.5 trả 400 nếu có `temperature`/`top_p`/
   `tool_choice: required`/`budget_tokens`; Argon trả 400 nếu có `thinkingBudget`.
3. Chạy đủ dev set bằng model nộp, rồi `kit check` phải báo `ready to submit`, commit, push.
4. **Hỏi người dùng trước** mọi lượt chạy tốn tiền lớn (chạy đủ 29 task, model mạnh) và trước khi nộp bài lên Kaggle.

Lệnh thường dùng (chạy từ `/home/ttlab/src/ple`, nạp env từ `/home/ttlab/src/AHPELE/.env`):

```bash
uv run python -m kit check /home/ttlab/src/AHPELE           # build + smoke test + kiểm tra sẵn sàng nộp
uv run python eval/run.py --tasks <id> /home/ttlab/src/AHPELE  # chạy 1 task dev
uv run python eval/run.py /home/ttlab/src/AHPELE            # chạy đủ dev set, export artifacts/
uv run python eval/run.py --artifacts /home/ttlab/src/AHPELE  # chấm lại artifacts offline
```

## 6. Tài nguyên máy (10.0.0.105)

- 24 CPU, khoảng 58 GB RAM (thường chỉ khoảng 20 GB trống), ổ đĩa khoảng 99 GB trống.
- Mỗi task dev cần tới 6 CPU / 16.25 GB, nên chạy tuần tự. Image task rubric khoảng 17 GB: dọn `docker image prune` khi đĩa đầy.
- Ghi file tạm vào thư mục scratch, không vào repo.

## 7. Giới hạn kỹ thuật cần nhớ

| Hạng mục | Giới hạn |
|---|---|
| Server khởi động | Nhận WebSocket trên `0.0.0.0:$PORT` trong 120 s |
| Serve container | 2 CPU, 4 GB RAM, 512 process, `/tmp` và `$HOME` mỗi cái 1 GB, root FS read-only |
| Build (`install`) | 30 phút, `/opt/harness` ≤ 2 GiB nén / 8 GiB giải nén |
| Thời gian mỗi task | 6 giờ (đọc `limits.agent_timeout_sec`, kết thúc gọi model trước khi hết giờ) |
| Kết nối model | Proxy đóng kết nối im lặng quá 30 phút; hãy stream và retry 429/5xx với backoff, không retry 400 |
