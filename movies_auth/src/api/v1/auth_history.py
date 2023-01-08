from flask import session, request
from app.flask_app import urls
from models.auth_history import AuthHistory
from models.user_agent import UserAgent
from utils.api_utils import create_error_response
from utils.authenticate import authenticate
from utils.rate_limit import rate_limit


@urls.route("/auth_history", methods=["GET"])
@authenticate
def auth_history():
    """
        Get auth history
        ---
        tags:
          - history
        parameters:
          - name: page
            in: query
            type: integer
            description: Номер страницы
            default: 1
          - name: page_size
            in: query
            type: integer
            description: Количество записей на странице
            default: 5
        responses:
          200:
            description: list of AuthHistory items
            schema:
              id: AuthHistoryModel
              properties:
                uuid:
                  type: string
                  description: id, format uuid4
                auth_date:
                  type: string
                  description:  user auth date
                user_agent_id:
                  type: string
                  description: user agent id. Format uuid4
        """
    page = int(request.args.get("page"))
    page_size = int(request.args.get("page_size"))
    user_agents_ids = UserAgent.query.with_entities(UserAgent.uuid).filter_by(user_id=session.get("user_id"))
    auth_histories_count = AuthHistory.query.with_entities(AuthHistory).\
        filter(AuthHistory.user_agent_id.in_(user_agents_ids)).order_by("auth_date").count()
    auth_histories = AuthHistory.query.with_entities(AuthHistory).\
        filter(AuthHistory.user_agent_id.in_(user_agents_ids)).order_by("auth_date").paginate(page, page_size, False).\
        items
    if isinstance(auth_histories, list):
        return {
            "results": [i.serialize() for i in auth_histories],
            "total": auth_histories_count,
            "page": page,
            "page_size": page_size,
        }
    return create_error_response(auth_histories)
