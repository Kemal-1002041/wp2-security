from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response
from flask_bcrypt import Bcrypt
from lib.testgpt.testgpt import TestGPT
from notes_model import NotesModel
from category_model import CategoryModel
from question_model import QuestionModel
from login_model import LoginModel
from Adminmodel import Adminpanel, AddTeacher
import math
from urllib.parse import urlparse
import config

app = Flask(__name__)
app.config["SECRET_KEY"] = 'HOI'
bcrypt = Bcrypt(app)


def is_valid_url(value):
    try:
        result = urlparse(value)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


app.jinja_env.filters['is_valid_url'] = is_valid_url


@app.before_request
def sessions():
    free_routes = ["login"]
    user = session.get("user")
    if not user and request.endpoint not in free_routes and request.endpoint != 'static':
        return redirect(url_for("login"))


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            error = 'Username and password are required!'
        else:
            login_model = LoginModel()
            user = login_model.get_user_by_username(username)

            if user and bcrypt.check_password_hash(user['teacher_password'], password):
                session["user"] = (user['teacher_id'], user['is_admin'])
                return redirect(url_for('notes_list'))
            else:
                error = 'Incorrect username or password!'
    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route('/notes_list', methods=['GET', 'POST'])
def notes_list():
    notes = NotesModel()
    category_model = CategoryModel()
    categories = category_model.get_categories()
    teacher_id, admin = session["user"][0], session["user"][-1]

    page_number = request.args.get('page', 1, type=int)
    notes_per_page = 20

    if request.method == 'POST':
        page_number = 1
        return handle_post_request(notes, admin, teacher_id, page_number, notes_per_page, categories)
    else:
        return handle_get_request(notes, admin, teacher_id, page_number, notes_per_page, categories)


def handle_post_request(notes, admin, teacher_id, page_number, notes_per_page, categories):
    if 'reset_filters' in request.form:
        if 'search_query' in session:
            session.pop('search_query')
        if 'all_teachers' in session:
            session.pop('all_teachers')
        if 'category' in session:
            session.pop('category')
        return view_all_notes(notes, admin, teacher_id, page_number, notes_per_page, categories)
    if 'query' in request.form:
        search_query = request.form['query']
        session['search_query'] = search_query
        return search_notes(notes, admin, teacher_id, page_number, notes_per_page, categories, search_query)
    elif 'all_teachers' in request.form:
        all_teachers = request.form['all_teachers']
        session['all_teachers'] = all_teachers
        return view_all_teachers_notes(notes, admin, teacher_id, page_number, notes_per_page, categories, all_teachers)
    elif 'categories' in request.form:
        category = request.form['categories']
        session['category'] = category
        return filter_notes_by_category(notes, admin, teacher_id, page_number, notes_per_page, categories, category)
    else:
        return view_all_notes(notes, admin, teacher_id, page_number, notes_per_page, categories)


def handle_get_request(notes, admin, teacher_id, page_number, notes_per_page, categories):
    search_query = request.args.get('query') or session.get('search_query')
    all_teachers = request.args.get('all_teachers') or session.get('all_teachers')
    category = request.args.get('category') or session.get('category')

    if search_query is None:
        session.pop('search_query', None)
    if all_teachers is None:
        session.pop('all_teachers', None)
    if category is None:
        session.pop('category', None)

    if search_query:
        return search_notes(notes, admin, teacher_id, page_number, notes_per_page, categories, search_query)
    elif all_teachers:
        return view_all_teachers_notes(notes, admin, teacher_id, page_number, notes_per_page, categories, all_teachers)
    elif category:
        return filter_notes_by_category(notes, admin, teacher_id, page_number, notes_per_page, categories, category)
    else:
        return view_all_notes(notes, admin, teacher_id, page_number, notes_per_page, categories)


def search_notes(notes, admin, teacher_id, page_number, notes_per_page, categories, search_query):
    session.pop('all_teachers', None)
    session.pop('category', None)

    if admin == 0:
        all_searched_notes = notes.get_searched_notes(search_query, search_query, teacher_id, page_number,
                                                      notes_per_page)
        total_notes = notes.count_searched_notes(search_query, search_query, teacher_id)
    else:
        all_searched_notes = notes.get_searched_notes(search_query, search_query, page_number=page_number,
                                                      notes_per_page=notes_per_page)
        total_notes = notes.count_searched_notes(search_query, search_query)

    total_pages = math.ceil(total_notes / notes_per_page)
    return render_template('notes_list.html.jinja', notes=all_searched_notes, total_notes=total_notes,
                           total_pages=total_pages, current_page=page_number, categories=categories,
                           search_query=search_query, admin=admin)


def view_all_teachers_notes(notes, admin, teacher_id, page_number, notes_per_page, categories, all_teachers):
    session.pop('search_query', None)
    session.pop('category', None)

    if admin == 0:
        all_public_notes = notes.get_all_public_notes(teacher_id, page_number, notes_per_page)
        total_notes = notes.count_all_public_notes(teacher_id)
    else:
        all_public_notes = notes.get_all_notes(page_number=page_number, notes_per_page=notes_per_page)
        total_notes = notes.count_all_notes()

    total_pages = math.ceil(total_notes / notes_per_page)
    return render_template('notes_list.html.jinja', notes=all_public_notes, total_notes=total_notes,
                           total_pages=total_pages, current_page=page_number, categories=categories,
                           all_teachers=all_teachers, admin=admin)


def filter_notes_by_category(notes, admin, teacher_id, page_number, notes_per_page, categories, category):
    session.pop('search_query', None)
    session.pop('all_teachers', None)

    if admin == 0:
        all_filtered_notes = notes.get_filtered_notes(category, teacher_id, page_number, notes_per_page)
        total_notes = notes.count_filtered_notes(category, teacher_id)
    else:
        all_filtered_notes = notes.get_filtered_notes(category, page_number=page_number, notes_per_page=notes_per_page)
        total_notes = notes.count_filtered_notes(category)

    total_pages = math.ceil(total_notes / notes_per_page)
    return render_template('notes_list.html.jinja', notes=all_filtered_notes, total_notes=total_notes,
                           total_pages=total_pages, current_page=page_number, categories=categories, category=category,
                           admin=admin)


def view_all_notes(notes, admin, teacher_id, page_number, notes_per_page, categories):
    session.pop('search_query', None)
    session.pop('all_teachers', None)
    session.pop('category', None)

    # Show only the logged-in teacher's notes by default for regular teachers
    if admin == 0:
        all_notes = notes.get_all_notes(teacher_id, page_number, notes_per_page)
        total_notes = notes.count_all_notes(teacher_id)
    else:  # For admin, show all notes
        all_notes = notes.get_all_notes(page_number=page_number, notes_per_page=notes_per_page)
        total_notes = notes.count_all_notes()

    total_pages = math.ceil(total_notes / notes_per_page)
    return render_template('notes_list.html.jinja', notes=all_notes, total_notes=total_notes,
                           total_pages=total_pages, current_page=page_number, categories=categories, admin=admin,
                           teacher_id=teacher_id)


@app.route('/export_notes_csv')
def export_notes_csv():
    notes_model = NotesModel()
    notes_data = notes_model.get_all_notes_for_csv()  # notes without pagination

    def generate_csv():
        # Headers
        yield ','.join(
            ['Notitie ID', 'Titel', 'Openbaar', 'Notitie', 'Datum aangemaakt', 'Categorie', 'Docent']).encode() + b'\n'

        # Actual data
        for row in notes_data:
            row = list(row)
            row[2] = 'Ja' if row[2] == 1 else 'Nee'
            yield ','.join(str(cell) for cell in row).encode() + b'\n'

    response = Response(generate_csv(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=notes.csv'
    return response


@app.route('/view_note/<note_id>')
def view_note(note_id):
    notes_model = NotesModel()
    question_model = QuestionModel()

    get_note = notes_model.get_note(note_id)
    questions = question_model.get_question_from_noteID(note_id)
    return render_template('view_note.html.jinja', note=get_note, questions=questions)


@app.route('/delete_note/<note_id>')
def delete_note(note_id):
    notes = NotesModel()
    notes.delete_note(note_id)
    return redirect(url_for('notes_list'))


def open_question_gen(note):
    test_gpt = TestGPT(config.api_key)
    open_question = test_gpt.generate_open_question(note)
    return open_question


def mc_question_gen(note):
    test_gpt = TestGPT(config.api_key)
    mc_question = test_gpt.generate_multiple_choice_question(note)
    return mc_question


@app.route('/generate_open_question/<note_id>')
def generate_open_question(note_id):
    notes_model = NotesModel()
    question_model = QuestionModel()

    get_note = notes_model.get_note(note_id)
    note = notes_model.get_actual_note(note_id)
    note = note[-2]
    open_question = open_question_gen(note)
    question_model.save_question(note_id, open_question)
    questions = question_model.get_question_from_noteID(note_id)

    return render_template('view_note.html.jinja', note=get_note, questions=questions)


@app.route('/generate_mc_question/<note_id>')
def generate_mc_question(note_id):
    notes_model = NotesModel()
    question_model = QuestionModel()

    get_note = notes_model.get_note(note_id)
    note = notes_model.get_actual_note(note_id)
    note = note[-2]
    mc_question = mc_question_gen(note)
    question_model.save_question(note_id, mc_question)
    questions = question_model.get_question_from_noteID(note_id)

    return render_template('view_note.html.jinja', note=get_note, questions=questions)


@app.route('/change_question/<questions_id>', methods=['POST', 'GET'])
def change_question(questions_id):
    question_model = QuestionModel()

    if request.method == 'POST':
        question = request.form["changed_question"]
        question_model.change(questions_id, question)
        return redirect(url_for('notes_list'))
    else:
        question_db = question_model.get_question(questions_id)
        question = question_db[1]
        note_id = question_db[0]
        return render_template('change_question.html.jinja', default_value=question, note_id=note_id,
                               questions_id=questions_id)


@app.route('/change_open_question_gen/<questions_id>')
def change_open_question_gen(questions_id):
    notes_model = NotesModel()
    question_model = QuestionModel()

    note_id = question_model.get_question(questions_id)
    note_id = note_id[0]

    note = notes_model.get_actual_note(note_id)
    note = note[-2]
    new_question = open_question_gen(note)
    question_model.change(questions_id, new_question)

    return redirect(url_for('notes_list'))


@app.route('/change_mc_question_gen/<questions_id>')
def change_mc_question_gen(questions_id):
    notes_model = NotesModel()
    question_model = QuestionModel()

    note_id = question_model.get_question(questions_id)
    note_id = note_id[0]

    note = notes_model.get_actual_note(note_id)
    note = note[-2]
    new_question = mc_question_gen(note)
    question_model.change(questions_id, new_question)

    return redirect(url_for('notes_list'))


@app.route('/delete_question/<questions_id>')
def delete_question(questions_id):
    question_model = QuestionModel()
    question_model.delete(questions_id)
    return redirect(url_for('notes_list'))


def get_note_dict():
    teacher_id = session["user"][0]
    note_dict = {
        'key_title': request.form['title'],
        'key_note_source': request.form['source'],
        'key_is_public': request.form['public'],
        'key_teacher_id': teacher_id,
        'key_category_id': request.form['category'],
        'key_note': request.form["note"],
    }
    if note_dict['key_title'] == "":
        note = note_dict['key_note']
        note_dict['key_title'] = note[:20]

    return note_dict


@app.route('/notes_form', methods=['POST', 'GET'])
def notes_form():
    notes = NotesModel()
    category_model = CategoryModel()
    categories = category_model.get_categories()

    if request.method == 'POST':
        note_dict = get_note_dict()
        notes.save_dict(note_dict)
        return redirect(url_for("notes_list"))
    else:
        return render_template('notes_form.html', categories=categories, title="NotesForm")


@app.route('/change_note/<note_id>', methods=['POST', 'GET'])
def change_note(note_id):
    note_model = NotesModel()
    category_model = CategoryModel()
    categories = category_model.get_categories()

    old_note_data = note_model.get_note(note_id)

    if request.method == 'POST':
        changed_note_dict = get_note_dict()
        note_model.change_note(note_id, changed_note_dict)
        return redirect(url_for("notes_list"))
    else:
        return render_template('change_note.html', categories=categories, old_note=old_note_data)


@app.route('/create_category', methods=['POST', 'GET'])
def create_category():
    category_model = CategoryModel()

    if request.method == 'POST':
        new_category = request.form['new_category']
        category_model.create_category(new_category)
        return redirect(url_for('notes_list'))
    else:
        return render_template('create_category.html.jinja', default_value="")


@app.route('/change_category/<category_id>', methods=['POST', 'GET'])
def change_category(category_id):
    category_model = CategoryModel()

    if request.method == 'POST':
        changed_category = request.form['changed_category']
        category_model.change_category(category_id, changed_category)
        return redirect(url_for('notes_list'))
    else:
        category = category_model.get_one_category(category_id)
        return render_template('create_category.html.jinja', default_value=category[0])


@app.route('/adminpanel', methods=['GET', 'POST'])
def adminpage():
    admin_model = Adminpanel()
    categories_data = admin_model.get_categories()
    return render_template('adminpanel.html', categories=categories_data)


@app.route('/createteacher', methods=['POST', 'GET'])
def create_teacher():
    admin_model = AddTeacher()
    if request.method == 'POST':
        display_name = request.form['display_name']
        username = request.form['username']
        is_admin = request.form.get('is_admin')
        teacher_password = request.form['teacher_password']
        hashed_password = bcrypt.generate_password_hash(teacher_password).decode('utf-8')
        admin_model.create_teacher(hashed_password, display_name, username, is_admin)

    return render_template('createteacher.html')


if __name__ == '__main__':
    app.run()
