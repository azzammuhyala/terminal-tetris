# Terminal Tetris🕹️
Permainan Tetris di terminal. Tidak ada egine khusus.

Dasar kodenya saya ambil dari [repositori GitHub](https://github.com/techwithtim/Tetris-Game) yang kemudian saya modifikasi dan buat se-efisien juga sebagus mungkin. Pemilik repositori menyertakan video tutorial di [YouTube](https://www.youtube.com/watch?v=uoR4ilCWwKA&t=3s) yang bisa kamu pelajari.

# Cara menjalankannya?⏸️
- Gunakan versi python terbaru. (Setidaknya versi 3.8 ke atas)
- Install modul yang diperlukan dengan perintah `pip install -r requirements.txt`.
- Lalu jalankan file `terminal-tetris.py`. Usahakan terminal yang kamu pakai mendukung karakter ansi escape `\x1b`. (Kalau kamu tidak tahu ansi escape intinya ini dipakai agar tampilan lebih berwarna. Jika terminalmu tidak mendukungnya ada kemungkinan tampilannya bisa rusak)

# Cara bermain?🎮
Saat anda menjalankan filenya permainan akan langsung dimulai. Tata balok yang jatuh perlahan dan ketika salah satu baris penuh maka baris itu akan di hapus dan akan menerima skor. Skor di permainan ini bisa didapat juga tiap kamu menaruh balok yang berjatuhan dengan jumlah kepingan balok yang jatuh.

Terdapat kontrol untuk melakukan tindakan pada balok berupa:
- Tombol `kiri` untuk mengeser balok jatuh ke kiri.
- Tombol `kanan` untuk mengeser balok jatuh ke kanan.
- Tombol `atas` untuk merotasi balok jatuh.
- Tombol `bawah` untuk mempercepat jatuhnya balok.
- Tombol `spasi` untuk mesegarkan tampilan terminal jika tampilannya aneh.
- Tombol `p` untuk pause.
- Tombol `q` untuk keluar.

# Fitur➕
- Bayangan balok
- Balok selanjutnya
- Skor khusus
- Tampilan berwarna