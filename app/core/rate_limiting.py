# Add this to your app.py for rate limiting

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiter configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour", "10 per minute"],
    storage_uri="redis://localhost:6379"
)

# Apply to specific routes:
# @app.route('/api/screen')
# @limiter.limit("30 per minute")
# def screen_stocks():
#     return jsonify(results)
