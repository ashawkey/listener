import time
from flask import Blueprint, request, jsonify
from mysql import *

bp = Blueprint('route', __name__, url_prefix='/api/nonsense/')

#@bp.route('/')
#def hello():
#    return "Hello!"

# =========== Nonsense ===========
# currently, we leave exception handling with frontend. 

@bp.route('/meta')
def get_nonsense_meta():
    token = request.args.get('token')
    page = int(request.args.get('page'))
    db = mysql.get_db()
    cur = db.cursor()
    cur.execute(stmt_meta, (token,))
    meta = cur.fetchall() # [[nid, ctime, mtime, body], ...]
    
    hasMore = True
    start = (page - 1) * 10
    end = page * 10
    if end > len(meta):
        end = len(meta)
        hasMore = False
    
    meta = meta[start:end]
    
    cur.close()
    db.close()
    return jsonify({
        'meta': meta,
        'hasMore': hasMore,
        })

@bp.route('/post', methods=('POST', ))
def post_nonsense():
    ctime = time.time()
    mtime = ctime
    body = request.form['body']
    token = request.form['token']
    state = request.form['state']

    db = mysql.get_db()
    cur = db.cursor()
    cur.execute(stmt_post, (ctime, mtime, body, token, state))
    db.commit()

    # get nid
    cur.execute(stmt_size)
    nid = cur.fetchone()[0]
    cur.close()
    db.close()

    return jsonify({
        'success': True,
        'nid': nid,
        })

@bp.route('/get')
def get_nonsense_content():
    nid = request.args.get('nid')
    token = request.args.get('token')

    db = mysql.get_db()
    cur = db.cursor()
    cur.execute(stmt_get, (nid,))
    content = cur.fetchone()
    cur.close()
    db.close()

    if content is None:
        return jsonify({
            'success': False,
            'error': 'Content Error',
        })
    elif content[3] != token:
        return jsonify({
            'success': False,
            'error': 'Token Error',
        })
    else:
        return jsonify({
            'success': True,
            'content': content,
        })

@bp.route('/update', methods=('POST', ))
def update_nonsense_content():
    mtime = time.time()
    body = request.form['body']
    state = request.form['state']
    nid = request.form['nid']

    db = mysql.get_db()
    cur = db.cursor()
    cur.execute(stmt_update, (mtime, body, state, nid))
    db.commit()
    cur.close()
    db.close()

    return jsonify({
        'success': True,
        })

@bp.route('/search')
def search_nonsense_content():
    token = request.args.get('token')
    keyword = request.args.get('keyword')

    db = mysql.get_db()
    cur = db.cursor()
    cur.execute(stmt_search, (keyword, token))
    res = cur.fetchall()
    cur.close()
    db.close()

    return jsonify(res)

@bp.route('/delete', methods=('POST', ))
def delete_nonsense_content():
    nid = request.form['nid']
    token = request.form['token']

    db = mysql.get_db()
    cur = db.cursor()
    cur.execute(stmt_get, (nid,))
    content = cur.fetchone()
    
    if content[3] != token:
        cur.close()
        db.close()
        return jsonify({
            'success': False,
            'error': 'Token Error',
            })
    else:
        cur.execute(stmt_delete, (nid,))
        db.commit()
        cur.close()
        db.close()
        return jsonify({
            'success': True,
            })