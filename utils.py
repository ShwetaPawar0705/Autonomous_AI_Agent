import json
import os
import re
from json import JSONDecodeError


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _strip_markdown(text: str) -> str:
    text = text.strip()
    if text.startswith('```'):
        parts = text.split('\n', 1)
        if len(parts) == 2:
            text = parts[1]
    if text.endswith('```'):
        text = text[: text.rfind('```')].strip()
    return text.strip()


def _sanitize_json(text: str) -> str:
    text = text.strip()
    text = text.replace('\r\n', '\n')
    text = text.replace('\t', ' ')
    text = re.sub(r',\s*(?=[}\]])', '', text)
    text = re.sub(r'(?m)^\s*//.*$', '', text)
    text = re.sub(r'(?s)/\*.*?\*/', '', text)
    return text.strip()


def _wrap_body(text: str) -> str:
    wrapped = text.strip()
    if not wrapped.startswith('{'):
        wrapped = '{' + wrapped
    if not wrapped.endswith('}'):
        wrapped = wrapped + '}'
    return wrapped


def safe_parse_json(text: str):
    if text is None:
        raise ValueError('No text to parse.')

    text = _strip_markdown(text)
    if not text:
        raise ValueError('Empty text cannot be parsed as JSON.')

    text = _sanitize_json(text)

    try:
        return json.loads(text)
    except JSONDecodeError:
        pass

    if not text.startswith('{') and (
        text.startswith('"')
        or text.startswith('document_type')
        or ':' in text
    ):
        candidate = _sanitize_json(_wrap_body(text))
        try:
            return json.loads(candidate)
        except JSONDecodeError:
            pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = _sanitize_json(text[start : end + 1])
        try:
            return json.loads(candidate)
        except JSONDecodeError:
            pass

    raise ValueError(
        f'Could not parse JSON from model output. Raw output: {text[:200].replace(chr(10), "\\n")}'
    )


def clamp_text(text: str, limit: int = 2000) -> str:
    text = text or ''
    return text[:limit]
