from api import api_blueprint
from flask import session, request, jsonify, redirect, url_for
from squeue.queue import SQueue
from database import db_add
import random
import string


@api_blueprint.route('/add', methods=['POST'])
def add_player():
    if 'players' not in session.keys():
        return jsonify(error='No queue object found'), 404
    players = session.get('players')
    queue = SQueue()
    queue.reconstitute(players)
    if 'new-player' in request.form:
        player = request.form['new-player']
        queue.enqueue(player)
    else:
        return jsonify(error='No/Wrong request arguments found')
    session['players'] = queue.players
    return jsonify(message='Added player'), 201


@api_blueprint.route('/move', methods=['POST'])
def move_player():
    if 'players' not in session.keys():
        return jsonify(error='No queue object found'), 404
    players = session.get('players')
    queue = SQueue()
    queue.reconstitute(players)
    if 'index' in request.form and 'player' in request.form:
        index = int(request.form['index']) - 1
        player = queue.dequeue(index)
        queue.enqueue(player)
    else:
        return jsonify(error='No/Wrong request arguments found')
    session['players'] = queue.players
    return redirect("/", 204)


@api_blueprint.route('/remove', methods=['POST'])
def remove_player():
    if 'players' not in session.keys():
        return jsonify(error='No queue object found'), 404
    players = session.get('players')
    queue = SQueue()
    queue.reconstitute(players)
    if 'index' in request.form and 'player' in request.form:
        index = int(request.form['index']) - 1
        queue.remove(index)
    else:
        return jsonify(error='No/Wrong request arguments found'), 404
    session['players'] = queue.players
    return jsonify(message=request.form['player'] + ' removed'), 205


@api_blueprint.route('/create', methods=['POST'])
def create():
    # TODO: Check for SSO Token
    if 'titleForm' not in request.form and 'datepicker' not in request.form and \
            'gameselect' not in request.form and 'tourneyselect' not in request.form and \
            'competitiors' not in request.form and 'admins' not in request.form and 'rules' not in request.form:
        return jsonify(message="Error, mismatched form"), 400
    create_request_data = {
        'tournament_id': ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(25)),
        'title': request.form['titleForm'],
        'date': request.form['datepicker'],
        'game_title': request.form['gameselect'],
        'tourney_type': request.form['tourneyselect'],
        'competitors': request.form['competitors'],
        'admins': request.form['admins'],
        'rule_set': request.form['rules']
    }
    if db_add.create_tournament(create_request_data):
        return redirect(url_for('tournament_blueprint.get_tourney'), 302)
    return jsonify(message="Error, tournament not created"), 500

