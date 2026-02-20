import json
import shlex
import subprocess

_session_id = None


def ask_openclaw(prompt: str, cmd_template: str) -> str:
    global _session_id

    if "{prompt}" not in cmd_template:
        raise ValueError('OPENCLAW_CMD_TEMPLATE must include "{prompt}"')

    safe_prompt = shlex.quote(prompt)
    cmd = cmd_template.format(prompt=safe_prompt)

    # keep context if we’ve already got a session id
    if _session_id:
        cmd = f"{cmd} --session-id {shlex.quote(_session_id)}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()

    if not stdout and stderr:
        return stderr

    # parse json and extract the clean reply
    try:
        data = json.loads(stdout)

        # session id lives here in your output:
        # data["meta"]["agentMeta"]["sessionId"]
        sid = (
            data.get("meta", {})
                .get("agentMeta", {})
                .get("sessionId")
        )
        if isinstance(sid, str) and sid.strip():
            _session_id = sid.strip()

        # reply lives here:
        # data["payloads"][0]["text"]
        payloads = data.get("payloads", [])
        if isinstance(payloads, list) and payloads:
            first = payloads[0]
            if isinstance(first, dict):
                text = first.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()

        # fallback: if shape changes, at least show something
        return stdout

    except json.JSONDecodeError:
        return stdout or stderr