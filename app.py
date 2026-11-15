import hashlib
import json
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "blockchain-demo"

# ====== GANTI 5 NAMA DI SINI SESUKA KAMU ======
NAMA_LIST = ["Alice", "Bob", "Charlie", "David", "Eva"]
# ==============================================

DIFFICULTY = 3  # hash harus diawali "000"


def hitung_hash(b):
    isi = {k: b[k] for k in ("index", "waktu", "nama1", "nama2", "uang", "prev_hash", "nonce")}
    return hashlib.sha256(json.dumps(isi, sort_keys=True).encode()).hexdigest()


def buat_block(index, nama1, nama2, uang, prev_hash):
    b = {
        "index": index,
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nama1": nama1,
        "nama2": nama2,
        "uang": uang,
        "prev_hash": prev_hash,
        "nonce": 0,
    }
    # proses mining: cari nonce sampai hash diawali "000"
    while True:
        h = hitung_hash(b)
        if h.startswith("0" * DIFFICULTY):
            b["hash"] = h
            return b
        b["nonce"] += 1


def chain_valid():
    for i, b in enumerate(chain):
        if b["hash"] != hitung_hash(b) or not b["hash"].startswith("0" * DIFFICULTY):
            return False
        if i > 0 and b["prev_hash"] != chain[i - 1]["hash"]:
            return False
    return True


# Block 0 (genesis)
chain = [buat_block(0, "-", "-", 0.0, "0")]

HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blockchain (Blok)</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: Arial, sans-serif; background:#f4f4f4; margin:0; padding:30px; color:#222; }
  .wrap { display:flex; gap:35px; flex-wrap:wrap; align-items:flex-start; }
  .panel { background:#fff; border:1px solid #bbb; border-radius:8px; padding:25px; }
  .left { flex:1; min-width:340px; }
  .right { flex:1; min-width:340px; }
  h1 { font-size:24px; text-align:center; margin:0 0 15px; padding-bottom:15px; border-bottom:1px solid #ccc; }
  .row { display:flex; align-items:center; margin-top:22px; }
  .row label { width:110px; font-size:18px; }
  .row select, .row input { flex:1; padding:14px; font-size:18px; border:1px solid #bbb; border-radius:4px; background:#fff; }
  .btn-wrap { text-align:center; margin-top:30px; }
  button { padding:12px 40px; font-size:18px; border:1px solid #888; border-radius:4px; background:#eee; cursor:pointer; }
  button:hover { background:#ddd; }
  .info-title { border:1px solid #bbb; border-radius:4px; text-align:center; padding:14px; font-size:18px; margin-bottom:20px; }
  .block { border:1px solid #bbb; border-radius:4px; padding:20px; margin-bottom:15px; }
  .block h2 { font-size:28px; font-weight:normal; margin:0 0 20px; }
  .lbl { font-weight:bold; margin-top:12px; }
  .val { font-size:15px; word-break:break-all; line-height:1.6; }
  hr { border:0; border-top:1px solid #ddd; margin:18px 0; }
  .valid { color:#222; }
  .invalid { color:red; }
  .msg { margin-top:25px; padding:12px; background:#e8e8e8; font-size:17px; }
  .msg.error { background:#fde2e2; color:#b00; }
  .small { opacity:.75; }
  .small h2 { font-size:20px; }
</style>
</head>
<body>
<div class="wrap">

  <div class="panel left">
    <h1>BLOCKCHAIN (BLOK)</h1>
    <form method="POST" action="/">
      <div class="row">
        <label>Nama 1</label>
        <select name="nama1" required>
          <option value="" disabled selected>Pilih nama</option>
          {% for n in nama_list %}<option value="{{ n }}">{{ n }}</option>{% endfor %}
        </select>
      </div>
      <div class="row">
        <label>Nama 2</label>
        <select name="nama2" required>
          <option value="" disabled selected>Pilih nama</option>
          {% for n in nama_list %}<option value="{{ n }}">{{ n }}</option>{% endfor %}
        </select>
      </div>
      <div class="row">
        <label>Uang</label>
        <input type="number" name="uang" placeholder="100" min="1" step="any" required>
      </div>
      <div class="btn-wrap"><button type="submit">Submit</button></div>
    </form>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for cat, m in messages %}<div class="msg {{ cat }}">{{ m }}</div>{% endfor %}
    {% endwith %}
  </div>

  <div class="panel right">
    <div class="info-title">Informasi Block</div>

    {% set b = chain[-1] %}
    <div class="block">
      <h2>Block {{ b.index }}</h2>
      <div class="lbl">Hash:</div>
      <div class="val">{{ b.hash }}</div>
      <div class="lbl">Previous Hash:</div>
      <div class="val">{{ b.prev_hash }}</div>
      <hr>
      <div class="lbl">Transaksi:</div>
      <div class="val">
        {% if b.index == 0 %}Block Genesis (belum ada transaksi)
        {% else %}{{ b.nama1 }} → {{ b.nama2 }} : {{ b.uang }}{% endif %}
      </div>
      <div class="val small">Waktu: {{ b.waktu }} | Nonce: {{ b.nonce }}</div>
      <div class="val" style="margin-top:18px;">
        Status Blockchain:
        {% if valid %}<b class="valid">Valid ✓</b>{% else %}<b class="invalid">Tidak Valid ✗</b>{% endif %}
      </div>
    </div>

    {% if chain|length > 1 %}
    <div class="lbl" style="margin:20px 0 10px;">Block sebelumnya:</div>
    {% for p in chain[:-1]|reverse %}
    <div class="block small">
      <h2>Block {{ p.index }}</h2>
      <div class="val">Hash: {{ p.hash }}</div>
      <div class="val">
        {% if p.index == 0 %}Block Genesis{% else %}{{ p.nama1 }} → {{ p.nama2 }} : {{ p.uang }}{% endif %}
      </div>
    </div>
    {% endfor %}
    {% endif %}
  </div>

</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nama1 = request.form.get("nama1")
        nama2 = request.form.get("nama2")
        try:
            uang = float(request.form.get("uang", "0"))
        except ValueError:
            uang = 0.0

        if not nama1 or not nama2:
            flash("Pilih Nama 1 dan Nama 2 dulu.", "error")
        elif nama1 == nama2:
            flash("Nama 1 dan Nama 2 tidak boleh sama!", "error")
        elif uang <= 0:
            flash("Jumlah uang harus lebih dari 0.", "error")
        else:
            chain.append(buat_block(len(chain), nama1, nama2, uang, chain[-1]["hash"]))
            flash("Transaksi berhasil dikirim dan blok berhasil dibuat.", "ok")
        return redirect(url_for("index"))

    return render_template_string(HTML, chain=chain, nama_list=NAMA_LIST, valid=chain_valid())


if __name__ == "__main__":
    app.run(host="localhost", port=8800, debug=True)
