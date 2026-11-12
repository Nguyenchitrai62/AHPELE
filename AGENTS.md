# AGENTS.md: quy tắc cho agent làm việc trong repo này

Repo này là **bài nộp (entry)** cho cuộc thi Kaggle
[Google - Agent Harness on Physical-Engineering's Last Exam](https://www.kaggle.com/competitions/physical-engineerings-last-exam)
(PLE). Mọi agent (Claude Code, OpenCode, …) làm việc ở đây phải tuân thủ các quy tắc dưới đây.

**Thứ tự ưu tiên khi các nguồn mâu thuẫn:** trang Kaggle ([docs/kaggle-evaluation.md](docs/kaggle-evaluation.md))
> hướng dẫn chính thức cho coding agent ([docs/official-agents-guide.md](docs/official-agents-guide.md))
> `docs/rules.md` trong kit > file này. Phát hiện mâu thuẫn thì báo người dùng và cập nhật file này.

Kit chính thức: https://github.com/google-research/ple, clone tại `/home/ttlab/src/ple` (**ngoài** repo này;
entry nằm trong kit thì `kit check` không bao giờ báo sẵn sàng).

## 0. QUY TẮC BẮT BUỘC (đọc trước khi làm bất cứ việc gì)

Vai trò: người dùng chỉ đạo, agent là người làm chính. Không chắc thì hỏi, không đoán.

**Model và chi phí**
1. Khi test local chỉ được gọi **2 model** qua OpenCode Go: `deepseek-v4.1-flash` và `muse-spark-1.3-contributor`.
   Áp dụng cho mọi lần gọi: harness, judge, gọi thử một câu. Model khác chỉ được gọi khi người dùng cho phép rõ ràng.
2. Không gọi Claude, Argon hay bất kỳ model đắt tiền nào để thử, kể cả qua OpenCode Zen, Vertex AI hay key khác.
3. Harness **phải tương thích** với model nộp bài (`google-cloud/claude-opus-5-5`, `google-cloud/gemini-4-argon`)
   bằng cách làm theo bài mẫu trong kit (mục 3, mục 6).
4. Hỏi người dùng trước mọi lượt chạy dài hoặc tốn nhiều hạn mức, ví dụ chạy đủ 29 task dev.

**Nộp bài**
5. Không bao giờ tự nộp, rút lại hay sửa Writeup trên Kaggle. Chỉ người dùng làm, hoặc agent làm khi được yêu cầu rõ ràng.
6. Bài nộp phải đủ mọi yêu cầu ở mục 2, qua `kit check` và `kit artifacts`, và `model_api` là một model `google-cloud/<id>`.
7. Mọi lượt chạy dev đều ghi vào `experiments/log.md` (mục 4), vì Writeup cần số liệu này.

**Fair-play** (mục 5)
8. Không hard-code đáp án, không nhận diện task, không đọc grader hay `artifacts/`, không sửa tay `artifacts/`,
   không gọi host ngoài endpoint model, không lưu nội dung task ẩn.

**Bí mật**
9. Không commit, in ra hay gửi ra ngoài bất kỳ key nào trong `.env`. Chỉ in tên biến. Kiểm tra diff trước mỗi commit.

**Git** (mục 8)
10. Luôn commit bằng `Nguyenchitrai62 <121591111+Nguyenchitrai62@users.noreply.github.com>` và push lên
    `origin main` (`https://github.com/Nguyenchitrai62/AHPELE.git`).
11. Tài khoản GitHub này chỉ được cấu hình cho repo này. Không đổi cấu hình git global, không đổi identity.
12. Không force-push, không xoá lịch sử, không đổi public/private của repo khi chưa được người dùng đồng ý.

**Môi trường**
13. Kit nằm ở `/home/ttlab/src/ple`, ngoài repo này. Không copy kit hay dữ liệu task vào repo.
14. File tạm, dữ liệu tải về và log chạy để ngoài repo. Không đưa nội dung task (prompt, file đề) vào git.
15. Máy dùng chung và RAM có hạn: chạy từng task một, dọn Docker image khi ổ đĩa đầy, không tắt container hay
    tiến trình không phải do mình tạo.

**Giao tiếp**
16. Trả lời người dùng bằng tiếng Việt, báo kết quả trung thực: lỗi thì nói lỗi, kèm log; việc bỏ qua thì nói rõ.
17. Khi luật thay đổi hoặc người dùng thêm quy tắc mới thì cập nhật ngay file này, rồi commit và push.

## 1. Cuộc thi tóm tắt

- **Mốc thời gian (23:59 UTC):** 2027-01-05 hạn nộp Writeup + commit · 2027-01-19 xong Stage 1 (chọn Top 100) ·
  2027-01-26 công bố kết quả Stage 2. Giải $250K / $100K / $50K. Đội tối đa 5 người, mỗi đội 1 bài nộp.
- **Cách nộp:** một **Kaggle Writeup** (≤ 2.000 từ) ở tab Writeups, có link repo GitHub trong Project Links và
  SHA commit 40 ký tự (`git rev-parse HEAD`) ở đầu bài. Được rút lại, sửa, nộp lại tới hạn chót.
- **Stage 1 (cổng loại, 100 điểm chấm Writeup):** Insight & phân tích lỗi 25 · Lập luận kỹ thuật (so trajectory
  của agent với quy trình kỹ sư thật trên 1 task dev) 25 · Tổng quát hoá qua ≥ 2 model 15 · Hiệu quả & scaling
  (đồ thị điểm theo chi phí) 20 · Rõ ràng & hình ảnh 15. Bắt buộc có ảnh bìa và 3 hình: sơ đồ kiến trúc,
  đồ thị điểm theo chi phí, phân loại lỗi trên 29 task dev. Top 100 vào Stage 2.
- **Stage 2:** chạy harness trên 56 task ẩn × 3 lần, model do Google trả tiền. Trước đó họ chấm `artifacts/` và
  **chạy lại live một mẫu ngẫu nhiên task dev**; bài không tái lập được hoặc hard-code thì bị loại. Giải trao cho
  3 hệ thống điểm trung bình cao nhất **nằm trên Pareto frontier điểm–chi phí**, điểm tối thiểu 0.138.
  Hoà thì xét điểm Writeup, rồi thời điểm nộp.
- **Chấm mỗi task:** 0–1, bằng script và/hoặc LLM judge (Claude Opus 5.5). Task thiết kế: `s = 0.4·p + 0.6·G·O'`
  (vi phạm bất kỳ ràng buộc an toàn/khả thi nào thì `G = 0`). Lỗi HTTP 400, crash, timeout đều tính điểm 0 cho task đó.

## 2. Repo phải có gì khi nộp

```
submission.yaml   name, model_api (một trong 8 model google-cloud/<id>), install, serve
serve.py          WebSocket server trên 0.0.0.0:$PORT
harness.py        vòng lặp agent
artifacts/        kết quả 29 task dev, chỉ sinh bằng eval/run.py, không sửa tay
LICENSE           Apache-2.0 hoặc MIT
README.md         cài đặt, kiến trúc, cách tái lập
```

Phải qua `uv run python -m kit check` (báo `ready to submit`) và `uv run python -m kit artifacts`.
Nếu repo để private trong lúc thi: cài GitHub App `ple-submission` và chuyển public khi cuộc thi kết thúc.

## 3. Quy trình đã thống nhất với người dùng

1. Người dùng và agent cùng thảo luận, nghiên cứu, thiết kế harness.
2. Chạy dev local bằng key **OpenCode Go** (`OPENCODE_API_KEY`), khai báo kiểu local-only.
   **CHỈ được gọi 2 model:** `deepseek-v4.1-flash` (Chat Completions) và `muse-spark-1.3-contributor`
   (Responses API). Mọi model khác, kể cả judge, test nhanh hay "ping thử", đều bị cấm trừ khi người dùng
   cho phép rõ ràng.
   **Harness vẫn phải tương thích với model mạnh khi nộp** (`google-cloud/claude-opus-5-5`,
   `google-cloud/gemini-4-argon`): theo đúng bài mẫu trong kit (`pi-opus`, `hermes-opus` cho Claude;
   `agy-gemini` cho Gemini), tách phần gọi model thành lớp adapter theo `MODEL_NAME`, không gửi tham số mà model
   đích từ chối (mục 6), có prompt caching cho Claude. Không chạy thử Claude/Argon bằng tiền.
   Thông số OpenCode Go:
   - Base `https://opencode.ai/inference/go`; danh sách model: `/v1/models`.
   - Chat Completions `/openai/v1/chat/completions` (DeepSeek, GLM, Kimi, …); Responses `/openai/v1/responses`
     (Muse Spark, GPT, Grok); Anthropic Messages `/anthropic/v1/messages`; Google `/google/v1beta/models/<id>`.
   - Bắt buộc header `x-opencode-session: <id cố định cho mỗi hội thoại>` (thiếu là HTTP 400 `MissingSessionID`)
     và `User-Agent` riêng (không dùng tên SDK chung chung). Harness nộp bài không được phụ thuộc header này:
     thêm header bằng proxy cục bộ hoặc chỉ bật khi chạy local.
   - Hạn mức tính bằng USD theo từng model: mỗi 5 giờ 20%, mỗi tuần 50%, mỗi tháng 100% hạn mức tháng.
3. Khi đạt kết quả: đổi `model_api` sang model mạnh (`google-cloud/claude-opus-5-5` hoặc
   `google-cloud/gemini-4-argon`), commit cùng `artifacts/` rồi nộp Writeup. Kaggle cho phép rõ: được sinh
   `artifacts/` bằng model cá nhân rồi đổi `model_api` trước khi commit, không bị loại, miễn là Writeup ghi rõ
   model và judge đã dùng. Ban tổ chức chấm lại `artifacts/` bằng judge chính thức.
4. Lưu ý rủi ro, phải nhắc người dùng trước khi nộp:
   - Harness chưa từng chạy trên model đích có thể dính HTTP 400 vì tham số riêng của model (mục 6).
     Nên chạy ít nhất bước `model` của `kit check`, tốn vài cent, trên model đích.
   - Stage 2 chạy lại live một số task dev bằng model đích, kết quả sẽ khác `artifacts/` sinh bằng model rẻ.
5. **Hỏi người dùng trước** mọi lượt chạy tốn tiền, mọi lần dùng model ngoài danh sách đã duyệt, và trước khi nộp lên Kaggle.

## 4. Ghi chép thí nghiệm (phục vụ Writeup)

Writeup cần ablation ("thêm X thì điểm dev từ A lên B"), bảng so sánh ≥ 2 model, đồ thị điểm theo chi phí, và
phân loại lỗi. Vì vậy **mọi lượt chạy dev** phải ghi một dòng vào `experiments/log.md` (sẽ tạo khi bắt đầu chạy):
ngày, commit harness, model, judge, danh sách task, điểm từng task và trung bình, token/chi phí/thời gian, thay đổi
so với lần trước, nhận xét lỗi. Giữ lại `runs/` cục bộ để phân tích, nhưng không commit nội dung task.

## 5. Luật fair-play (vi phạm có thể bị loại)

- KHÔNG hard-code đáp án, KHÔNG nhận diện task cụ thể để rẽ nhánh (kể cả task dev).
- KHÔNG để harness đọc grader, file tham chiếu, `tests/`, hay `artifacts/` của chính nó (từ đĩa, git history, mạng).
- KHÔNG sửa tay hay tạo file trong `artifacts/`; chỉ export bằng `eval/run.py` từ đúng harness đang commit.
  Được chạy lại từng task (`--tasks <id>`). Sửa harness thì phải chạy lại dev set và commit chung.
- KHÔNG gọi host nào ngoài endpoint model (không web search, không tool do nhà cung cấp host, không API ngoài).
- KHÔNG lưu, log, publish nội dung prompt hay file của task test ẩn.

## 6. Kỹ thuật cần nhớ

- Harness đọc URL/key model từ biến môi trường (`MODEL_NAME`, `MODEL_BASE_URL`, `MODEL_API_KEY`, `OPENAI_*`,
  `ANTHROPIC_*`, `GEMINI_*`), không hard-code. Mọi kết nối ra ngoài phải đi qua `HTTPS_PROXY`.
- **Claude Opus 5.5:** trả 400 nếu có `temperature`, `top_p`, `top_k`, `budget_tokens`, hoặc `tool_choice` bắt buộc.
  Đặt `max_tokens` khoảng 32000. Gắn `cache_control: ephemeral` vào system prompt và message mới nhất, nếu không
  chi phí tăng nhiều lần.
- **Gemini 4 Argon:** `reasoning_effort` là low/medium/high; trả 400 nếu có `thinkingBudget`; `max_tokens` ≤ 65536.
- Model mặc định nghĩ ở mức cao nhất; muốn mức khác thì truyền `reasoning_effort` rõ ràng.
- Stream hoặc đặt timeout dài; retry 429/5xx/timeout với backoff; không retry 400.
- Theo dõi `limits.agent_timeout_sec`; khi nhận `cancel` phải gửi `done` ngay với tóm tắt tốt nhất.
- Luôn kết thúc bằng `done.final_message` tóm tắt đã làm gì và file nằm ở đâu (judge có đọc phần này).
  Ghi deliverable sớm rồi tinh chỉnh dần. Đúng tên và đường dẫn file theo đề là quan trọng nhất.

| Hạng mục | Giới hạn |
|---|---|
| Server khởi động | Nhận WebSocket trên `0.0.0.0:$PORT` trong 120 s |
| Serve container | 2 CPU, 4 GB RAM, 512 process, `/tmp` và `$HOME` mỗi cái 1 GB, `/opt/harness` read-only |
| Build (`install`) | `debian:bookworm`, 30 phút, `/opt/harness` ≤ 2 GiB nén / 8 GiB giải nén, repo kể cả `.git` ≤ 1 GiB |
| Mỗi task | 6 giờ; mỗi lệnh `exec` ≤ 600 s; output ≤ 100 KB; tối đa 8 request song song |
| `artifacts/` | ≤ 512 MiB, ≤ 10.000 file, không LFS, không symlink, mỗi file ≤ 95 MiB |

## 7. Bảo mật và bí mật

- Key nằm trong `.env` (đã `.gitignore`): `KAGGLE_API_TOKEN`, `HF_TOKEN`, `OPENCODE_API_KEY`, …
- KHÔNG BAO GIỜ commit, in ra log, hay gửi key lên dịch vụ ngoài. Khi cần xem `.env` chỉ in tên biến:
  `sed -E 's/=.*/=<hidden>/' .env`. Không đặt key trong `submission.yaml` (`env:` chỉ dành cho giá trị không bí mật).
- Trước mỗi commit: `git status`, rồi kiểm tra diff không chứa key thật.

## 8. Git

- Remote: `origin = https://github.com/Nguyenchitrai62/AHPELE.git`, nhánh `main`. Push qua đăng nhập `gh` của
  tài khoản Nguyenchitrai62, chỉ cấu hình trong `.git/config` của repo này.
- **Luôn commit bằng tài khoản Nguyenchitrai62:** `user.name = Nguyenchitrai62`,
  `user.email = 121591111+Nguyenchitrai62@users.noreply.github.com`. Không dùng identity global của máy (`thao_ttp`).
- Commit nhỏ, message rõ ràng. Commit chứa `artifacts/` phải chứa đúng harness đã sinh ra chúng.
- Mỗi phiên bản `artifacts/` đều nằm lại trong lịch sử git: squash khi repo phình to (giới hạn 1 GiB).
- Không force-push, không xoá lịch sử khi chưa được người dùng đồng ý.

## 9. Lệnh thường dùng

**Gate OpenCode (bắt buộc cho mọi lần gọi model khi chạy local):** `tools/start_gate.sh` khởi động
`tools/opencode_gate.py` trên `0.0.0.0:8090`. Gate chỉ cho qua 2 model đã duyệt, tự thêm header
`x-opencode-session`, và ghi token/chi phí từng lần gọi vào `~/.cache/ahpele/gate-usage.jsonl`.
Lần chạy đầu, script tạo `/home/ttlab/src/ple/local.env` (nằm ngoài repo, chứa `MODEL_API_KEY` của gate và cấu hình
`JUDGE_*`, judge = `deepseek-v4.1-flash`). Không bao giờ gọi thẳng OpenCode mà bỏ qua gate.

Khi test local, entry khai báo `model_api: openai-compatible/deepseek-v4.1-flash` (hoặc `muse-spark-1.3-contributor`)
với `model_base_url: https://llm.example.org/v1` làm placeholder. Đổi về `google-cloud/<id>` trước khi nộp.

Chạy từ `/home/ttlab/src/ple`; mọi lệnh kit/eval đều thêm
`--env-file local.env --model-base-url http://localhost:8090/v1`:

```bash
uv run python -m kit check /home/ttlab/src/AHPELE                 # build, smoke test, kiểm tra sẵn sàng nộp
uv run python eval/run.py --tasks <id> /home/ttlab/src/AHPELE     # chạy 1 task dev
uv run python eval/run.py /home/ttlab/src/AHPELE                  # chạy đủ dev set, export artifacts/
uv run python -m kit artifacts /home/ttlab/src/AHPELE             # kiểm tra artifacts theo luật
uv run python eval/run.py --artifacts /home/ttlab/src/AHPELE      # chấm lại artifacts offline (chỉ gọi judge)
uv run python eval/run.py --regrade runs/<name>-<time>            # chấm lại sau khi sửa judge
```

Log của kit: `~/.cache/plebench/<name>/` (`build.log`, `serve.log`, `egress.log`, `relay.log`, `check.json`).

## 10. Tài nguyên máy (10.0.0.105)

- 24 CPU, khoảng 58 GB RAM (thường chỉ khoảng 20 GB trống), ổ đĩa khoảng 99 GB trống.
- Mỗi task dev cần tới 6 CPU / 16.25 GB nên chạy tuần tự. Image task rubric khoảng 17 GB: dọn image khi đĩa đầy.
- File tạm ghi vào thư mục scratch, không vào repo.
