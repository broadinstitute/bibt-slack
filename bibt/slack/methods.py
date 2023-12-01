import logging

import requests

from .params import DEFAULT_SLACK_ATTACHMENT_COLOR
from .params import SLACK_MAX_TEXT_LENGTH

_LOGGER = logging.getLogger(__name__)


def _check_len(text):
    if len(text) > SLACK_MAX_TEXT_LENGTH:
        text = text[: SLACK_MAX_TEXT_LENGTH - 4] + "\n..."
    elif len(text) < 1:
        _LOGGER.warning("Not adding empty string to message.")
        return None
    return text


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


    :param webhook: a slack webhook in the standard format:
        ``'https://hooks.slack.com/services/{app_id}/{channel_id}/{hash}'``
    :type webhook: str

    :param title: the title of the message. This will appear above the attachment.
        Can be Slack-compatible markdown.
    :type title: str

    :param text: the text to be included in the attachment. Can be
        Slack-compatible markdown, defaults to ``None``. You must
        supply either ``text`` or ``blocks``.
    :type text: str, optional

    :param color: the color to use for the Slack attachment border, defaults to
        ``None``. You must supply either ``text`` or ``blocks``.
    :type color: str, optional

    :param blocks: A list of strings, each to be put in its own attachment
        block, defaults to ``None``. You must supply either ``text`` or ``blocks``.
    :type blocks: str, optional

    :param dividers: When generating multiple blocks, whether or not to
        include dividers between them, defaults to ``False``.
    :type dividers: bool, optional

    :param raise_for_status: whether or not to check for HTTP errors
        and raise an exception, defaults to ``True``.
    :type raise_for_status: bool, optional

    :raises Exception: if ``raise_for_status==True`` and an HTTP error was raised.

    :return: the requests.Response object returned by the API call.
    :rtype: `requests.Response`
    """
    if not color:
        _LOGGER.warning(
            "No attachment color provided, using "
            f"default: [{DEFAULT_SLACK_ATTACHMENT_COLOR}]"
        )
        color = DEFAULT_SLACK_ATTACHMENT_COLOR
    if text and blocks:
        _LOGGER.warning(
            "Both text and blocks provided; prepending the text to the blocks."
        )
        blocks = [text].extend(blocks)
        text = None
    if text:
        text = _check_len(text)
        if not text:
            raise Exception("Cannot pass empty string as text.")
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
        added_block = False
        for block in blocks:
            block = _check_len(block)
            if not block:
                continue
            msg["attachments"][0]["blocks"].append(
                {"type": "section", "text": {"type": "mrkdwn", "text": block}}
            )
            added_block = True
            if dividers:
                msg["attachments"][0]["blocks"].append({"type": "divider"})
        if not added_block:
            raise Exception("No valid text blocks passed (must have len < 0)")

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
