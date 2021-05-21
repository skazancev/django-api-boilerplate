from django.conf import settings
from django.db.models import Exists, OuterRef
from django.utils import timezone

from apps.communication.models import UserFlow, FlowAction
from utils.timezone import rounded_now
from . import user_flow_action as user_flow_action_service


def create(flow, user, context=None, start_date=None, trigger_type=None, **metadata):
    return UserFlow.objects.create(
        user=user,
        flow=flow,
        start_date=start_date or timezone.now(),
        context=context or {},
        metadata=metadata,
        trigger_type=trigger_type or UserFlow.Type.automatic,
    )


def find_actions_for_sending(user_flow) -> FlowAction.objects:
    # find actual actions that have not yet been sent
    return user_flow.flow.actions.annotate(
        is_completed=Exists(queryset=user_flow.actions.filter(action_id=OuterRef('id'))),
    ).filter(is_completed=False)


def trigger(user_flow):
    now = rounded_now()
    period = now + settings.FLOW_REPEAT_DELAY
    actions = find_actions_for_sending(user_flow)
    for action in actions:
        # calculate send_date for every action
        send_date = action.get_send_date(user_flow.start_date)

        # check if action can be sent
        if not period >= send_date >= now:
            continue

        flow_action = user_flow_action_service.create(user_flow, action, eta=send_date)
        user_flow_action_service.send_async(flow_action)


def complete(user_flow: UserFlow):
    user_flow.is_completed = True
    user_flow.save()
