Licensing of ZhConversion data files is complicated.

In theory, MW repo doesn't exclude these from GPL, but the files as a whole are
pieced together from many sources with different licenses:

1. Some character-to-character mapping are from the Unihan database, which is
   in the public domain.
2. Some items are from Chinese Wikipedia, licensed under CC BY-SA 3.0.
3. Some items are directly contributed through Git, so they are under GPL.

Therefore, I don't think the tables can really be licensed under GPL. But in
reality, no one is sure about how to license them. Since a community consensus
which allows fair-uses of this table was reached, I still decided to put these
in the library for convenience and consider this fair-use. If there are any
updates on this, feel free to open an issue or dmca this repo. If something
goes south, you can still provide your own tables.

https://github.com/wikimedia/mediawiki/blob/master/includes/languages/data/ZhConversion.php
