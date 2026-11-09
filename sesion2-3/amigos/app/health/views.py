from flask import jsonify
from sqlalchemy import text

from . import health
from .. import db


@health.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text('SELECT 1'))

        return jsonify({
            'status': 'ok',
            'database': 'connected'
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'message': str(e)
        }), 503
