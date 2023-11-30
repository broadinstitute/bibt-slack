import logging

import requests

from .params import SLACK_MAX_TEXT_LENGTH

_LOGGER = logging.getLogger(__name__)


def post_message(
    webhook,
    title,
    text=None,
    color=None,
    blocks=None,
    dividers=False,
    raise_for_status=True,
):
    """Posts a message to Slack.

    .. code:: python

        from bibt.slack import send_message
        ...


    :param str webhook: a slack webhook in the standard format:
        ``'https://hooks.slack.com/services/{app_id}/{channel_id}/{hash}'``
    :param str title: the title of the message. This will appear above the attachment.
        Can be Slack-compatible markdown.
    :param str text: the text to be included in the attachment.
        Can be Slack-compatible markdown.
    :param str color: the color to use for the Slack attachment border.
    :param list blocks: A list of strings, each to be put in its own attachment block.
    :param bool dividers: When generating multiple blocks, whether or not to
        include dividers between them.
    :param bool raise_for_status: whether or not to check for HTTP errors
        and raise an exception, defaults to ``True``.
    :raises Exception: if ``raise_for_status==True`` and an HTTP error was raised.
    :return requests.Response: the requests.Response object returned by the API call.
    """

    if not color:
        color = "#000000"
    if text:
        if len(text) > SLACK_MAX_TEXT_LENGTH:
            text = text[:SLACK_MAX_TEXT_LENGTH] + "\n..."
        msg = {
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": title}}],
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {"type": "section", "text": {"type": "mrkdwn", "text": text}}
                    ],
                }
            ],
        }
    elif blocks:
        msg = {
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": title}}],
            "attachments": [
                {
                    "color": color,
                    "blocks": [],
                }
            ],
        }
        for block in blocks:
            if len(block) > SLACK_MAX_TEXT_LENGTH - 35:
                block = block[: SLACK_MAX_TEXT_LENGTH - 35] + "\n..."
            msg["attachments"][0]["blocks"].append(
                {"type": "section", "text": {"type": "mrkdwn", "text": block}}
            )
            if dividers:
                msg["attachments"][0]["blocks"].append({"type": "divider"})

    else:
        raise Exception("Either text or blocks must be passed.")
    r = requests.post(webhook, json=msg)
    if raise_for_status:
        try:
            r.raise_for_status()
        except Exception:
            _LOGGER.error(f"[HTTP Status: {r.status_code}] {r.text}")
            raise
    return r
