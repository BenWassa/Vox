# logic.py
import datetime

# Leitner system: intervals for boxes 1 through 5
# After getting a card right, it moves to the next box.
# If it's in the last box and correct, it's 'mastered' (moved to box 6).
SRS_INTERVALS_DAYS = {
    1: 1,
    2: 3,
    3: 7,
    4: 14,
    5: 30,
}

def get_next_review_date(current_box: int) -> datetime.datetime:
    """Calculates the next review date based on the current box."""
    now = datetime.datetime.utcnow()
    if current_box in SRS_INTERVALS_DAYS:
        delta = datetime.timedelta(days=SRS_INTERVALS_DAYS[current_box])
        return now + delta
    # If card is mastered (box 6) or new (box 0/1), set review far in the future
    # or handle as a special case. For mastered, we can set a very long delay.
    return now + datetime.timedelta(days=365 * 5)
