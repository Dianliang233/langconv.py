import re
from enum import Enum

from attrs import define

from langconv.language import Language
from langconv.trie import Node, Trie

SECTION_LENGTH = 30 - 1
# We assume that the longest match will be 30 characters long to save mem


@define
class LCMarkup:
    class Flag(Enum):
        HIDDEN = 'H'
        """Insert a conversion rule without output."""

        COPY = 'A'
        """Insert a conversion rule with a result in the current language."""

        REMOVE = '-'
        """Remove existing conversion rule."""

        TITLE = 'T'
        """Override page title."""

        DESCRIPTION = 'D'
        """Describe a conversion rule."""

        RAW = 'R'
        """Disable language conversion. This can either be created literally with R or implicitly with a invalid rule."""

        SHOW = 'S'
        """A normal conversion that is shown in the output. This does not need to be specified and does not insert a rule."""

        EMPTY = ''
        """(Real) empty flag."""

    @define
    class Rule:
        pass

    @define
    class Unidirectional(Rule):
        original: str
        mapping: dict[str, str]

        def localize(self, language: Language) -> tuple[dict[str, str], str] | None:
            fallbacks = language.fallbacks
            for fallback in fallbacks + [language.code]:
                match = self.mapping.get(fallback, None)
                if match:
                    return {self.original: match}, match
            return None

    @define
    class Omnidirectional(Rule):
        mapping: dict[str, str]

        def localize(self, language: Language) -> tuple[dict[str, str], str] | None:
            fallbacks = language.fallbacks
            copy = self.mapping.copy()
            match: str | None = None
            for fallback in fallbacks + [language.code]:
                match = self.mapping.get(fallback, None)
                if match:
                    copy.pop(fallback, None)
                    break
            if match:
                new_rules = {i: match for _, i in self.mapping.items()}
                return new_rules, match
            return None

    @define
    class Raw(Rule):
        original: str

    @define
    class Empty(Rule):
        pass

    flag: Flag
    rule: Rule

    @classmethod
    def parse_rules(cls, raw: str):
        from_to = [x.strip() for x in raw.split('=>', 1)]
        # 1. Determine direction
        if len(from_to) == 1:
            if from_to[0].find(':') == -1:
                # No rules. Raw or empty
                return cls.Raw(original=from_to[0]) if from_to[0] else cls.Empty()
            # Omnidirectional rule
            raw_rules = [x.strip() for x in from_to[0].split(';')]
            rules: list[tuple[str, str]] = []
            for rule in raw_rules:
                splitted = rule.split(':', 1)
                if len(splitted) != 2:  # noqa: PLR2004
                    continue
                rules.append((splitted[0].strip().lower(), splitted[1].strip()))
            mapping = dict(rules)
            return cls.Omnidirectional(mapping=mapping)
        else:
            # Unidirectional rule
            original = from_to[0].strip()
            raw_rules = [x.strip() for x in from_to[1].split(';')]
            rules: list[tuple[str, str]] = []
            for rule in raw_rules:
                splitted = rule.split(':', 1)
                if len(splitted) != 2:  # noqa: PLR2004
                    continue
                rules.append((splitted[0].strip().lower(), splitted[1].strip()))
            mapping = dict(rules)
            return cls.Unidirectional(original=original, mapping=mapping)

    @classmethod
    def parse(cls, text: str) -> 'LCMarkup':
        # 1. Get rid of -{ and }-
        text = text[2:-2].strip()
        # 2. Split flag and rules. Note that flag can be empty.
        if text.find('|') != -1:
            # If it has flag
            raw_flag, raw_rules = (x.strip() for x in text.split('|', 1))
            flag = cls.Flag(raw_flag)
            rules = cls.parse_rules(raw_rules)
        else:
            raw_rules = text.strip()
            rules = cls.parse_rules(raw_rules)
            # If we find no flag, it can be RAW, SHOW or EMPTY
            if isinstance(rules, cls.Raw):
                flag = cls.Flag.RAW
            elif isinstance(rules, cls.Empty):
                flag = cls.Flag.EMPTY
            else:
                flag = cls.Flag.SHOW

        return cls(flag=flag, rule=rules)


@define
class LanguageConverter:
    language: Language
    rules: list[Trie]

    def longest_prefix(self, text: str, extra_rules: list[Trie] | None = None) -> Node | None:
        rules = self.rules if extra_rules is None else extra_rules + self.rules
        for rule in rules:
            match = rule.longest_prefix(text)
            if match and match.value != '':
                return match
        return None

    def insert_rule(
        self,
        rule: LCMarkup.Unidirectional | LCMarkup.Omnidirectional,
        trie: Trie,
        language: Language,
    ) -> None:
        result = rule.localize(language)
        if result:
            for key, value in result[0].items():
                trie.insert(key, value)

    def delete_rule(
        self,
        rule: LCMarkup.Unidirectional | LCMarkup.Omnidirectional,
        trie: Trie,
        language: Language,
    ) -> None:
        result = rule.localize(language)
        if result:
            for key, _ in result[0].items():
                trie.delete(key)

    def divide(self, text: str):
        segments: list[str | LCMarkup] = []
        pointer = 0
        raw_markups = re.finditer(r'(?P<markup>-{.*?}-)', text)
        for markup in raw_markups:
            before = text[pointer : markup.start()]
            if before:
                segments.append(before)
            segments.append(LCMarkup.parse(markup.group()))
            pointer = markup.end()
        segments.append(text[pointer:])

        return segments

    def convert(
        self,
        text: str,
        *,
        sequential_global: bool = False,
        avoid_html_code: bool = False,
    ) -> str:
        """Converts the given text to this language.

        :param text: The text to convert.
        :param sequential_global: If true, global conversion rules are parsed and added at where it first appears. Otherwise they are added at initialization, which is not compliant to vanilla MW behavior.
        :param ignore_html: Whether to ignore "code" HTML tags (<pre>, <code> and <script>).
        """

        trie = Trie()
        segments = self.divide(text)

        # Filter out global rules (HIDDEN, COPY, REMOVE)
        if not sequential_global:
            for segment in segments.copy():
                if isinstance(segment, str) or not isinstance(
                    segment.rule, LCMarkup.Unidirectional | LCMarkup.Omnidirectional
                ):
                    continue
                if segment.flag in (segment.Flag.HIDDEN, segment.Flag.COPY):
                    self.insert_rule(segment.rule, trie, self.language)
                elif segment.flag == segment.Flag.REMOVE:
                    self.delete_rule(segment.rule, trie, self.language)
                if segment.flag in (segment.flag.REMOVE, segment.Flag.HIDDEN):
                    segments.remove(segment)

        output: list[str] = []
        for segment in segments:
            if isinstance(segment, str):
                i = 0
                while i < len(segment):
                    match = self.longest_prefix(segment[i : i + SECTION_LENGTH], [trie])
                    if match:
                        output += match.value
                        i += len(match.full_key)
                    else:
                        output.append(segment[i])
                        i += 1
                continue

            if isinstance(segment.rule, LCMarkup.Raw):
                output.append(segment.rule.original)
                continue

            if not isinstance(
                segment.rule,
                LCMarkup.Unidirectional | LCMarkup.Omnidirectional,
            ):
                continue

            if segment.flag in (segment.Flag.SHOW, segment.Flag.COPY):
                output.append((segment.rule.localize(self.language) or (None, ''))[1])

            if sequential_global:
                if segment.flag in (segment.Flag.HIDDEN, segment.Flag.COPY):
                    self.insert_rule(segment.rule, trie, self.language)
                elif segment.flag == segment.Flag.REMOVE:
                    self.delete_rule(segment.rule, trie, self.language)

            # TODO: Handle `avoid_html_code`

        return ''.join(output)

    @classmethod
    def from_language(cls, language: Language):
        return cls(language, [language.rules])
