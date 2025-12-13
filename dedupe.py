import time
from config import MAX_REPEAT, COOLDOWN_SECONDS


class DedupeSpeaker:
    """
    Controls how often detected labels are allowed to be spoken,
    preventing excessive repetition through count limits and cooldowns.
    """

    def __init__(self):
        # Track how many times each label was spoken and the last time it occurred
        self.state = {}  # label -> {"count": int, "last": float}

    def should_speak(self, label: str, current_labels: set) -> bool:
        """
        Determine whether a label should be spoken based on repetition rules.
        """
        now = time.time()
        s = self.state.get(label, {"count": 0, "last": 0})

        # Block speech if the label exceeded repeat limit and is still in cooldown
        if s["count"] >= MAX_REPEAT and (now - s["last"]) < COOLDOWN_SECONDS:
            # If only one object is present, do not repeat until cooldown expires
            if len(current_labels) == 1:
                return False
            return False

        return True

    def mark_spoken(self, label: str):
        """
        Update internal state after a label has been spoken.
        """
        now = time.time()
        s = self.state.get(label, {"count": 0, "last": 0})
        s["count"] += 1
        s["last"] = now
        self.state[label] = s
