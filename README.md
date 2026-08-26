# AI Customer Service Agent

Dự án học Python và xây dựng AI customer service agent dựa trên tài liệu Shopify chính thức.

Hiện tại dự án đang ở **Giai đoạn 0 — Chuẩn bị môi trường**. Chưa có business logic.

## 1. Công cụ cần cài

- Git
- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop

Trên Windows, mở PowerShell mới sau khi cài đặt rồi kiểm tra:

```powershell
git --version
py -3.13 --version
uv --version
docker --version
docker compose version
```

> Dự án hiện dùng Python 3.13. Docker chưa bắt buộc ở giai đoạn backend ban đầu.

## 2. Cài dependencies

Trong thư mục dự án, chạy:

```powershell
uv sync
```

`uv` sẽ đọc `pyproject.toml`, tạo `.venv` và cài các công cụ phát triển. Bạn không cần tự chạy `pip install` cho từng thư viện.

## 3. Tạo cấu hình local

```powershell
Copy-Item .env.example .env
```

File `.env` chỉ dùng trên máy cá nhân và không được commit lên Git. Ở giai đoạn này có thể giữ nguyên các giá trị mặc định.

## 4. Khởi động PostgreSQL + pgvector

Mở Docker Desktop trước, sau đó chạy:

```powershell
docker compose up -d
docker compose ps
```

Dừng database bằng:

```powershell
docker compose down
```

Lệnh trên không xóa dữ liệu. Chưa dùng tùy chọn `-v` nếu bạn chưa muốn xóa database volume.

## 5. Kiểm tra chất lượng code

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

Ý nghĩa dành cho người mới:

- `ruff check`: tìm lỗi code và vấn đề về style.
- `ruff format --check`: kiểm tra định dạng thống nhất.
- `mypy`: kiểm tra type hints mà không cần chạy chương trình.
- `pytest`: chạy automated tests.

Để Ruff tự định dạng code:

```powershell
uv run ruff format .
```

## 6. Git workflow đơn giản

Không code trực tiếp trên `main`. Mỗi công việc tạo một branch:

```powershell
git switch -c phase-0/project-setup
git add .
git commit -m "chore: set up Python project"
```

Quy ước commit gợi ý:

- `feat:` thêm tính năng.
- `fix:` sửa lỗi.
- `test:` thêm hoặc sửa test.
- `docs:` sửa tài liệu.
- `chore:` cấu hình và công việc bảo trì.

## Cấu trúc hiện tại

```text
src/customer_service_agent/  Package Python
tests/                       Automated tests
compose.yaml                 PostgreSQL + pgvector
pyproject.toml               Dependencies và cấu hình công cụ Python
.env.example                 Mẫu biến môi trường
```

## Definition of Done cho Giai đoạn 0

- [ ] `uv sync` hoàn tất.
- [ ] PostgreSQL + pgvector ở trạng thái healthy.
- [ ] Ruff, mypy và pytest đều pass.
- [x] Tài liệu kiến trúc hiển thị đúng ký tự sơ đồ UTF-8.
