from flask import Flask, request as req, url_for
from markupsafe import escape

app = Flask(__name__)

BOOKS = [
    {
        "id": 1,
        "title": "Dế Mèn Phiêu Lưu Ký",
        "author": "Tô Hoài",
        "year": "1941",
        "category": "Văn học",
        "available": "true",
    },
    {
        "id": 2,
        "title": "Lão Hạc",
        "author": "Nam Cao",
        "year": "1943",
        "category": "Văn học",
        "available": "false",
    },
    {
        "id": 3,
        "title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh",
        "author": "Nguyễn Nhật Ánh",
        "year": "2010",
        "category": "Truyện dài",
        "available": "true",
    },
    {
        "id": 4,
        "title": "Số Đỏ",
        "author": "Vũ Trọng Phụng",
        "year": "1936",
        "category": "Tiểu thuyết",
        "available": "true",
    },
    {
        "id": 5,
        "title": "Tắt Đèn",
        "author": "Ngô Tất Tố",
        "year": "1939",
        "category": "Tiểu thuyết",
        "available": "false",
    },
]


def render_nav():
    return f"""
    <nav>
        <a href="{url_for('index')}">Trang chủ</a> | 
        <a href="{url_for('books')}">Danh sách sách</a> | 
        <a href="{url_for('api_books')}">API Danh sách</a>
    </nav>
    <hr>
    """


def book_to_json(b):
    return (
        f'{{"id": {b["id"]}, '
        f'"title": "{b["title"]}", '
        f'"author": "{b["author"]}", '
        f'"year": "{b["year"]}", '
        f'"category": "{b["category"]}", '
        f'"available": "{b["available"]}"}}'
    )


@app.route("/")
def index():
    total_books = len(BOOKS)
    available_books = sum(1 for b in BOOKS if b.get("available") == "true")

    return f"""
    {render_nav()}
    <h2>Thống kê thư viện</h2>
    <p>Tổng số đầu sách: <strong>{total_books}</strong></p>
    <p>Số sách sẵn sàng cho mượn: <strong>{available_books}</strong></p>
    """


@app.route("/books")
def books():
    categories = sorted(list({b["category"] for b in BOOKS}))
    cat_nav = [f'<a href="{url_for("books")}">Tất cả</a>']
    for cat in categories:
        cat_nav.append(
            f'<a href="{url_for("books", category=cat)}">{escape(cat)}</a>'
        )
    category_bar = " | ".join(cat_nav)

    selected_category = req.args.get("category")
    if selected_category:
        filtered_books = [
            b for b in BOOKS if b["category"].lower() == selected_category.lower()
        ]
    else:
        filtered_books = BOOKS

    rows = ""
    for b in filtered_books:
        status = "Có sẵn" if b["available"] == "true" else "Đang mượn"
        detail_url = url_for("book_detail", book_id=b["id"])
        rows += f"""
        <tr>
            <td>{b['id']}</td>
            <td><a href="{detail_url}">{escape(b['title'])}</a></td>
            <td>{escape(b['author'])}</td>
            <td>{escape(b['year'])}</td>
            <td>{escape(b['category'])}</td>
            <td>{escape(status)}</td>
        </tr>
        """

    return f"""
    {render_nav()}
    <h2>Danh sách sách</h2>
    <p><strong>Lọc theo thể loại:</strong> {category_bar}</p>
    <table border="1" cellpadding="8" cellspacing="0">
        <thead>
            <tr>
                <th>ID</th>
                <th>Tiêu đề</th>
                <th>Tác giả</th>
                <th>Năm</th>
                <th>Thể loại</th>
                <th>Trạng thái</th>
            </tr>
        </thead>
        <tbody>
            {rows if rows else '<tr><td colspan="6">Không có sách thuộc thể loại này</td></tr>'}
        </tbody>
    </table>
    """


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return (
            f"""
        {render_nav()}
        <h2>404 - Không tìm thấy</h2>
        <p>Không có sách với ID = {escape(str(book_id))}</p>
        <p><a href="{url_for('books')}">&larr; Quay lại danh sách</a></p>
        """,
            404,
        )

    status = (
        "Sẵn sàng cho mượn" if book["available"] == "true" else "Đã được mượn"
    )

    return f"""
    {render_nav()}
    <h2>Chi tiết sách</h2>
    <ul>
        <li><strong>ID:</strong> {book['id']}</li>
        <li><strong>Tiêu đề:</strong> {escape(book['title'])}</li>
        <li><strong>Tác giả:</strong> {escape(book['author'])}</li>
        <li><strong>Năm xuất bản:</strong> {escape(book['year'])}</li>
        <li><strong>Thể loại:</strong> {escape(book['category'])}</li>
        <li><strong>Trạng thái:</strong> {escape(status)}</li>
    </ul>
    <p><a href="{url_for('books')}">&larr; Quay lại danh sách</a></p>
    """


@app.route("/api/books")
def api_books():
    selected_category = req.args.get("category")
    if selected_category:
        filtered = [
            b for b in BOOKS if b["category"].lower() == selected_category.lower()
        ]
    else:
        filtered = BOOKS

    json_str = "[" + ", ".join(book_to_json(b) for b in filtered) + "]"
    return json_str, {"Content-Type": "application/json; charset=utf-8"}


@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        json_err = f'{{"error": "Không có sách với ID = {book_id}"}}'
        return json_err, 404, {"Content-Type": "application/json; charset=utf-8"}

    return book_to_json(book), {"Content-Type": "application/json; charset=utf-8"}


@app.errorhandler(404)
def page_not_found(e):
    if req.path.startswith("/api/"):
        json_err = '{"error": "Tài nguyên không tồn tại"}'
        return json_err, 404, {"Content-Type": "application/json; charset=utf-8"}

    return (
        f"""
    {render_nav()}
    <h2>404 - Không tìm thấy trang</h2>
    <p>Trang bạn yêu cầu không tồn tại.</p>
    <p><a href="{url_for('index')}">&larr; Về trang chủ</a></p>
    """,
        404,
    )


if __name__ == "__main__":
    app.run(debug=True)