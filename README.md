# Màn sao cưới — Ngọc Thịnh ♡ Châu Khanh

Code dựng khung màn sao cưới kiểu clip TikTok của Blinkk Wedding:
nền trời sao, 2 chòm sao nét đứt vàng (Kim Ngưu + Ma Kết), tên cô dâu
chú rể ở giữa, ngày cưới 28.11.2026.

## Có gì trong repo

- `build_wedding_starscreen.py` — render khung tĩnh 1920×1080
  (file PNG). Chạy: `python3 build_wedding_starscreen.py`
- `build_wedding_video.py` — render video 12 giây, 24fps, 1920×1080
  (sao nhấp nháy, 2 chòm sao vẽ dần trong 5 giây đầu, sao băng ở
  giây 6,5 và 9,5, tên và ngày hiện dần từ giây 5–7). Chạy:
  `python3 build_wedding_video.py`

## Yêu cầu

- Python 3, thư viện Pillow
- ffmpeg (để encode video)
- Font DejaVu (có sẵn trên Linux)

## Lưu ý

- Hình chòm sao đã sửa đúng hình thật: Kim Ngưu gồm cụm Pleiades
  tách riêng + chữ V Hyades (Aldebaran sáng nhất ở đỉnh V) + 2 sừng;
  Ma Kết là hình tam giác (cặp alpha/beta ở đỉnh tây, delta sáng nhất
  ở đỉnh đông, đỉnh nam, mỗi cạnh một sao trung gian).
- Trang web màn sao cưới (bản chạy trên trình duyệt, có nút Toàn màn
  hình) là một artifact riêng, code của nó chưa nằm trong repo này —
  có thể export thành file HTML để thêm vào sau nếu cần.

## Trang web (index.html)

`index.html` là code trang web màn sao cưới (bản chạy trên trình duyệt,
khung 16:9, sao nhấp nháy, 2 chòm sao tự vẽ dần, chữ hiện dần từng chữ
kèm vệt sáng vàng quét ngang, nút Toàn màn hình để chiếu màn LED).
Mở trực tiếp file này trên trình duyệt là chạy, hoặc bật GitHub Pages
cho repo để có link xem online.

Lưu ý: ngày trên trang web đang để 28.11 (chưa có năm), trong khi khung
ảnh và video để 28.11.2026.
