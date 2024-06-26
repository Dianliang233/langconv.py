"""
This type stub file was generated by pyright.
"""

class Lang(tuple):
    """Lang handles the ISO 639 series of international standards
    for language codes

    Instantiable with any ISO 639 language code or name as argument
    (case sensitive)

    ...

    Attributes
    ----------
    name : str
        ISO 639-3 reference language name or ISO 639-5 English name
    pt1 : str
        two-letter ISO 639-1 code, if there is one
    pt2b : str
        three-letter ISO 639-2 code for bibliographic applications,
        if there is one
    pt2t : str
        three-letter ISO 639-2 code for terminology applications,
        if there is one
    pt3 : str
        three-letter ISO 639-3 code, if there is one
    pt5 : str
        three-letter ISO 639-5 code, if there is one

    Examples
    --------
    >>> lg = Lang('eng')
    >>> lg
    Lang(name='English', pt1='en', pt2b='eng', pt2t='eng', pt3='eng', pt5='')
    >>> lg.name
    'English'
    """

    _tags = ...
    _abrs = ...
    _data = ...
    _scope = ...
    _type = ...
    _deprecated = ...
    _macro = ...
    __slots__ = ...
    def __new__(cls, *args: str | Lang, **kwargs: str):  # -> Self@Lang:
        ...
    def __repr__(self):  # -> str:
        ...
    def __hash__(self) -> int: ...
    def __eq__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __getnewargs__(self):  # -> tuple[str]:
        ...
    @property
    def name(self) -> str:
        """Gets the ISO 639 name of this language"""
        ...

    @property
    def pt1(self) -> str:
        """Gets the ISO 639-1 code of this language"""
        ...

    @property
    def pt2b(self) -> str:
        """Gets the ISO 639-2B code of this language"""
        ...

    @property
    def pt2t(self) -> str:
        """Gets the ISO 639-2T code of this language"""
        ...

    @property
    def pt3(self) -> str:
        """Gets the ISO 639-3 code of this language"""
        ...

    @property
    def pt5(self) -> str:
        """Gets the ISO 639-5 code of this language"""
        ...

    def asdict(self) -> dict[str, str]:
        """Get ISO 639 language name and codes as a Python
        dictionary.

        Returns
        -------
        Dict[str, str]
            A dictionary containing the values of the 'name',
            'pt1', 'pt2b', 'pt2t', 'pt3' and 'pt5' attibutes.
        """
        ...

    def scope(self) -> str:
        """Gets the ISO 639-3 scope of this language

        Returns
        -------
        str
            the ISO 639-3 scope of this language among 'Individual',
            'Macrolanguage' and 'Special'.
            None is returned by not ISO 639-3 languages.
        """
        ...

    def type(self) -> str:
        """Gets the ISO 639-3 type of this language

        Returns
        -------
        str
            the ISO 639-3 type of this language among 'Ancient',
            'Constructed', 'Extinct', 'Historical', 'Living' and
            'Special'.
            None is returned by not ISO 639-3 languages.
        """
        ...

    def macro(self) -> Lang:
        """Get the macrolanguage of this individual language

        Returns
        -------
        iso639.Lang
            the macrolanguage of this individual language, if there is one
        """
        ...

    def individuals(self) -> list[Lang]:
        """Get all individual languages of this macrolanguage

        Returns
        -------
        list of Lang
            the Lang instances of the individual languages of this
            macrolanguage, if it is one
        """
        ...
