import re
from enum import Enum

from attr import field
from attrs import define

from langconv.language import Language
from langconv.trie import DoubleArrayTrie, Node

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

    flags: tuple[Flag, ...]
    rule: Rule

    @classmethod
    def parse(cls, text: str) -> 'LCMarkup':
        def parse_rules(raw: str):
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

        # 1. Get rid of -{ and }-
        text = text[2:-2].strip()
        # 2. Split flags and rules. Note that flag can be empty.
        if text.find('|') != -1:
            # If it has flag
            raw_flags, raw_rules = (x.strip() for x in text.split('|', 1))
            flags = tuple(cls.Flag(raw_flag) for raw_flag in raw_flags)
            rules = parse_rules(raw_rules)
        else:
            raw_rules = text.strip()
            rules = parse_rules(raw_rules)
            # If we find no flags, it can be RAW, SHOW or EMPTY
            if isinstance(rules, cls.Raw):
                flags = cls.Flag.RAW,
            elif isinstance(rules, cls.Empty):
                flags = cls.Flag.EMPTY,
            else:
                flags = cls.Flag.SHOW,

        return cls(flags=flags, rule=rules)


@define
class LanguageConverter:
    language: Language
    rules: list[DoubleArrayTrie]
    is_initialized: bool = field(default=False)

    def longest_prefix(self, text: str, extra_rules: list[DoubleArrayTrie] | None = None) -> Node | None:
        rules = self.rules if extra_rules is None else extra_rules + self.rules
        for rule in rules:
            match = rule.longest_prefix(text)
            if match:
                return match
        return None

    def convert(self, text: str, *, sequential_global: bool = False, avoid_html_code: bool = False) -> str:
        '''Converts the given text to this language.

        :param text: The text to convert.
        :param sequential_global: Control whether global conversion rules are parsed and added at initialization or at where it first appears.
        :param ignore_html: Whether to ignore "code" HTML tags (<pre>, <code> and <script>).
        '''

        def insert_global_rule(
                rule: LCMarkup.Unidirectional | LCMarkup.Omnidirectional,
                trie: DoubleArrayTrie,
                language: Language) -> None:
            result = rule.localize(language)
            if result:
                for key, value in result[0].items():
                    trie.insert(key, value)

        def delete_global_rule(
                rule: LCMarkup.Unidirectional | LCMarkup.Omnidirectional,
                trie: DoubleArrayTrie,
                language: Language) -> None:
            result = rule.localize(language)
            if result:
                for key, _ in result[0].items():
                    trie.delete(key)

        # Retrieve all markups
        raw_markups = re.finditer(r'(?P<markup>-{.*?}-)', text)
        markups = {markup.span(): LCMarkup.parse(markup.group()) for markup in raw_markups}
        starts = tuple(markup[0] for markup, _ in markups.items())
        locations = tuple(markup for markup, _ in markups.items())

        trie = DoubleArrayTrie()

        # Filter out global rules (HIDDEN, COPY, REMOVE)
        if not sequential_global:
            for _, markup in markups.items():
                if not isinstance(markup.rule, LCMarkup.Unidirectional | LCMarkup.Omnidirectional):
                    continue
                if (markup.Flag.HIDDEN in markup.flags or markup.Flag.COPY in markup.flags):
                    insert_global_rule(markup.rule, trie, self.language)
                if markup.Flag.REMOVE in markup.flags:
                    delete_global_rule(markup.rule, trie, self.language)

        output: list[str] = []
        i = 0
        while i < len(text):
            if i in starts:
                loc = locations[starts.index(i)]
                markup = markups[loc]
                i += loc[1] - loc[0]
                if not isinstance(markup.rule, LCMarkup.Unidirectional | LCMarkup.Omnidirectional | LCMarkup.Raw):
                    continue

                if isinstance(markup.rule, LCMarkup.Raw):
                    output.append(markup.rule.original)
                    continue
                elif markup.Flag.SHOW in markup.flags or markup.Flag.COPY in markup.flags:
                    output.append((markup.rule.localize(self.language) or (None, ''))[1])

                if not sequential_global:
                    continue
                if markup.Flag.HIDDEN in markup.flags or markup.Flag.COPY in markup.flags:
                    insert_global_rule(markup.rule, trie, self.language)
                elif markup.Flag.REMOVE in markup.flags:
                    delete_global_rule(markup.rule, trie, self.language)

                continue

            # TODO: Handle `avoid_html_code`

            match = self.longest_prefix(text[i:i + SECTION_LENGTH], [trie])
            if match:
                output += match.value
                i += len(match.full_key)
            else:
                output.append(text[i])
                i += 1
        return ''.join(output)

    @classmethod
    def from_language(cls, language: Language):
        return cls(language, [language.rules])
