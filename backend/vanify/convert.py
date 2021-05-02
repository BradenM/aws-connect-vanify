"""AWS Connect Vanify Convert."""

import logging
import sys
from collections import deque
from pathlib import Path
from queue import PriorityQueue
from typing import Deque, Dict, Iterator, List, NamedTuple, Optional

import attr
import phonenumbers
import pygtrie

# TODO: For a real application, setup proper log handling.
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger = logging.getLogger(__name__)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class ValidationState(NamedTuple):
    """Tuple for a word validation state."""

    valid: bool = True
    max_cont: int = 0
    max_substring_length: int = 0


class WordNodeComp(NamedTuple):
    eq: bool
    lt: bool
    gt: bool


PHONE_ALPHA_MAP = {
    k: list(v)
    for k, v in {
        "1": "",
        "2": "ABC",
        "3": "DEF",
        "4": "GHI",
        "5": "JKL",
        "6": "MNO",
        "7": "PQRS",
        "8": "TUV",
        "9": "WXYZ",
        "0": "",
    }.items()
}


@attr.s(auto_attribs=True, order=False)
class WordNode:
    current_wordified: str
    current_index: int = 0
    n_chars: int = 0
    # max continuous chars
    max_cont_chars: int = 0
    max_substring_length: int = 0

    def _iter_comparison(self, other: "WordNode") -> Iterator[WordNodeComp]:
        """Iterate word node comparison objects.

        Args:
            other: word node to compare with.

        """
        attrs = (
            "n_chars",
            "max_cont_chars",
            "max_substring_length",
        )
        for a in attrs:
            left = getattr(self, a)
            right = getattr(other, a)
            yield WordNodeComp(eq=left == right, lt=left < right, gt=left > right)

    def __le__(self, other):
        chars, cont_chars, sub_length = list(self._iter_comparison(other))
        return (
            sub_length.lt
            or (sub_length.eq and cont_chars.lt)
            or (sub_length.eq and cont_chars.eq and chars.lt)
        )

    def __eq__(self, other):
        chars, cont_chars, sub_lth = list(self._iter_comparison(other))
        return sub_lth.eq and cont_chars.eq and chars.eq

    def __gt__(self, other):
        chars, cont_chars, sub_lth = list(self._iter_comparison(other))
        return (
            sub_lth.gt
            or (sub_lth.eq and cont_chars.gt)
            or (sub_lth.eq and cont_chars.eq and chars.gt)
        )

    def _has_clean(self, slice: List[str], match: int):
        return len([n for n in slice if n.isalpha()]) == match

    @property
    def has_clean_three(self):
        return self._has_clean(self.current_wordified[-7:-4], 3)

    @property
    def has_clean_four(self):
        return self._has_clean(self.current_wordified[-4:], 4)

    @property
    def has_clean_seven(self):
        return self._has_clean(self.current_wordified[-7:], 7)

    @property
    def score(self):
        """Preference score.

        Opinionated score given to each word node.
        In order of the most potential points to gain,
        the challenges are:
            - Latter seven digits are chars (for phone number)
            - Latter four digits are chars (for phone number)
            - Is a singular word.
            - Inner three digits are chars (for phone number)
            - Total char count is 7 or 4

        """

        def _apply_scoring(current_score: int, scoring: Dict[int, bool], exclusive: bool = False):
            for score, check in scoring.items():
                if check:
                    current_score += score
                    if exclusive:
                        break
            return current_score

        _score = 0
        is_pref_same = (
            self.n_chars == self.max_cont_chars and self.n_chars == self.max_substring_length
        )
        scoring = {2: is_pref_same}
        _score = _apply_scoring(_score, scoring)
        if 11 >= len(self.current_wordified) >= 10:
            scoring = {4: self.has_clean_seven, 3: self.has_clean_four, 1: self.has_clean_three}
            _score = _apply_scoring(_score, scoring, exclusive=False)
        return _score

    @property
    def as_phonenumber(self):
        """Format word node as phone number.

        Examples:
            >>> node.as_phonenumber
            '1-800-123-APPLE'
            >>> node.as_phonenumber
            '1-800-YUP-5311'

        """
        chars = list(self.current_wordified)
        if chars[0] == "1":
            chars.insert(1, "-")
        if not self.has_clean_seven:
            chars.insert(5, "-")
        for idx, c in enumerate(chars):
            try:
                pos_look = chars[idx + 1]
                neg_look = chars[idx - 1]
                if c == "-":
                    yield c
                elif c.isalpha() and (not pos_look.isalpha() and pos_look != "-"):
                    yield c
                    yield "-"
                elif c.isalpha() and (not neg_look.isalpha() and neg_look != "-"):
                    yield "-"
                    yield c
                else:
                    yield c
            except IndexError:
                yield c

    def update_from_state(self, state: ValidationState):
        """Update values from validation state."""
        self.max_substring_length = state.max_substring_length
        self.max_cont_chars = state.max_cont


@attr.s(kw_only=True, auto_attribs=True)
class VanifiedResult:
    node_results: List[WordNode] = attr.ib(factory=list)
    words_queue: PriorityQueue = attr.ib(init=False)
    words_tree: Optional[pygtrie.Trie] = attr.ib(repr=None, default=None)
    _words: List[str] = attr.ib(init=False, factory=list, repr=False)

    max_results: int = 5

    def __attrs_post_init__(self):
        self.words_queue = PriorityQueue(maxsize=0)
        if not self.words_tree:
            root = Path(__file__).parent
            word_list = (root / "words.txt").read_text().splitlines()
            self._words = [w.rstrip().upper() for w in word_list if 9 >= len(w.strip()) > 2]
            self.words_tree = pygtrie.Trie()
            for w in self._words:
                self.words_tree[w] = True

    @property
    def word_results(self) -> List[str]:
        return ["".join(n.as_phonenumber) for n in self.node_results]

    def ensure_put(self, value: WordNode):
        logger.debug("pushing into pqueue: %s", value)
        if self.words_queue.full():
            r = self.words_queue.get_nowait()
            logger.debug("popped item: %s", r)
        self.words_queue.put_nowait(value)

    @staticmethod
    def find_char_prefix(word, index) -> str:
        char_prefix = ""
        while index >= 0 and word[index].isalpha():
            char_prefix = word[index] + char_prefix
            index -= 1
        return char_prefix

    @staticmethod
    def find_word_substrings_with_chars(value: str):
        """Find all word substrings and chars from string.

        Args:
            value: string to extract from.

        Examples:
            >>> VanifiedResult.find_word_substrings_with_chars('1800123APPLE')
            ['A', 'AP', 'APP', 'APPL', 'APPLE']

        Returns:
            List of word substrings and chars.

        """

        all_substrings = []
        substring = ""
        len_word = len(value)
        for index, char in enumerate(value):
            if char.isalpha():
                substring += char
                if index == len_word - 1 or not value[index + 1].isdigit():
                    all_substrings.append(substring)
            else:
                substring = ""
        return all_substrings

    def validate(self, value: str) -> ValidationState:
        """Validate a word node wordified number."""
        substrings = self.find_word_substrings_with_chars(value)

        is_valid = len(substrings) > 0
        max_substring_length = 0
        max_cont_chars = 0

        if is_valid:
            for substring in substrings:
                max_cont_chars = max(len(substring), max_cont_chars)
                sub_substrings = self.find_word_substrings(substring)
                for sub_substring in sub_substrings:
                    max_substring_length = max(len(sub_substring), max_substring_length)
        return ValidationState(
            valid=is_valid, max_cont=max_cont_chars, max_substring_length=max_substring_length
        )

    def is_valid_word_or_prefix(self, value: str) -> bool:
        """Validate if `value` is a valid word or prefix.

        Args:
            value: input value.

        Examples:
            >>> results = VanifiedResult()
            >>> results.is_valid_word_or_prefix('CALLNOW')
            True  # ("CALL" + "NOW" prefix)
            >>> results.is_valid_word_or_prefix('COZL')
            False  # (Not a prefix of anything)
            >>> results.is_valid_word_or_prefix('SUNDAY')
            True  # ("SUNDAY" is a valid word)

        Returns:
            True if valid, False otherwise

        """
        if self.words_tree.has_key(value) or self.words_tree.has_subtrie(value):
            return True
        for idx, _ in enumerate(value):
            if self.words_tree.has_key(value[: idx + 1]) and self.words_tree.has_subtrie(
                value[idx + 1 :]
            ):
                return True
        return False

    def find_word_substrings(self, value: str) -> List[str]:
        """Finds valid sub-words preset in `value`.

        Examples:
            >>> VanifiedResult.find_word_substrings('CALLNOW')
            ['CALL', 'NOW']


        """
        if self.words_tree.has_key(value):
            return [value]
        for idx, _ in enumerate(value):
            right = value[: idx + 1]
            left = value[idx + 1 :]
            if self.words_tree.has_key(left) and self.words_tree.has_key(right):
                return [right, left]
        return []

    def is_valid_word(self, value: str) -> bool:
        return any(self.find_word_substrings(value))

    @classmethod
    def from_phone_number(cls, number: str, *args):
        """Create vanified result from phone number."""
        number_obj = phonenumbers.parse(number, "US")
        parsed_number = phonenumbers.format_number(number_obj, phonenumbers.PhoneNumberFormat.E164)
        return cls.from_numbers(parsed_number.lstrip("+"), *args)

    @classmethod
    def from_numbers(cls, number: str, max_results: int = 5):
        """Convert input numbers to tele-words.

        Args:
            number: input numbers.
            max_results: max results to return.

        Returns:
            VanifiedResult item.

        """
        results = cls(max_results=max_results)

        num_digits = len(number)
        queue: Deque[WordNode] = deque([])

        queue.append(WordNode(number))

        while queue:
            cur_node = queue.popleft()
            cur_wordified = cur_node.current_wordified
            cur_idx = cur_node.current_index

            if cur_idx == num_digits:
                valid_state = results.validate(cur_wordified)

                if not valid_state.valid:
                    continue

                cur_node.update_from_state(valid_state)
                results.ensure_put(cur_node)
                continue

            cur_digit = number[cur_idx]
            cur_n_chars_in_word = cur_node.n_chars

            char_prefix = results.find_char_prefix(cur_wordified, cur_idx - 1)
            len_char_prefix = len(char_prefix)

            for char in PHONE_ALPHA_MAP[cur_digit] + [cur_digit]:
                is_dig_and_prefix_invalid = char.isdigit() and (
                    not len_char_prefix or results.is_valid_word(char_prefix)
                )
                is_alpha_and_valid_word_or_prefix = char.isalpha() and (
                    cur_idx != num_digits - 1
                    and results.is_valid_word_or_prefix(char_prefix + char)
                )
                is_alpha_and_valid_word = char.isalpha() and (
                    cur_idx == num_digits - 1 and results.is_valid_word(char_prefix + char)
                )
                if (
                    is_dig_and_prefix_invalid
                    or is_alpha_and_valid_word_or_prefix
                    or is_alpha_and_valid_word
                ):
                    next_word_num = cur_wordified[:cur_idx] + char + cur_wordified[cur_idx + 1 :]
                    logger.debug("Next word: %s", next_word_num)
                    next_nchars = cur_n_chars_in_word + (1 if char.isalpha() else 0)
                    v_state = results.validate(next_word_num)
                    queue.append(
                        WordNode(
                            next_word_num,
                            current_index=cur_idx + 1,
                            n_chars=next_nchars,
                            max_cont_chars=v_state.max_cont,
                            max_substring_length=v_state.max_substring_length,
                        )
                    )

        # return max word node having most n of cont letters
        if results.words_queue.qsize() > 0:
            node_results = reversed(sorted(results.words_queue.queue, key=lambda n: n.score))
            results.node_results = list(node_results)[: results.max_results]
            return results

        return results
