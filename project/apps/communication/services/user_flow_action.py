from apps.communication.models import UserFlowAction
from . import communications as history_service
from ..tasks import send_user_flow_action


def create(user_flow, flow_action, eta):
    return UserFlowAction.objects.create(
        flow=user_flow,
        action=flow_action,
        eta=eta,
    )


def send(user_flow_action: UserFlowAction):
    communication = create_communication(user_flow_action)
    history_service.send(communication)


def send_async(user_flow_action: UserFlowAction):
    send_user_flow_action.apply_async(args=(user_flow_action.id,), eta=user_flow_action.eta)


def create_communication(user_flow_action: UserFlowAction):
    from .user_flow import complete as complete_user_flow

    communication = history_service.generate(
        user_id=user_flow_action.flow.user_id,
        target=user_flow_action.action.template.format_subject(user_flow_action.flow.context),
        trigger_type=user_flow_action.flow.trigger_type,
        user_flow_action=user_flow_action,
        type=user_flow_action.action.template.type,
    )
    communication.save()
    if user_flow_action.is_last:
        complete_user_flow(user_flow_action.flow)

    return communication

    # action_types[action.type](flow_action=action).execute(*args, **kwargs)
