# Expected behaviour of tests

_Using `INCLUDE_UNMAPPED_FIELDS`_

* Record `0` (id `000000001`) :
  * 1 item with `items.biblionumber` `000000001`
* Record `1` :
  * Error `No 001`
* Record `2` (id `000000010`) :
  * 3 items with `items.biblionumber` `000000010`
* Record `3` (id `000000100`) :
  * 1 item with `items.biblionumber` `000000100`
  * The items has a `995$$1`
  * The items has a `995$$s`
  * The items has no `995$$Y`
* Record `3` (id `000001000`) :
  * 1 item with call number `First|Second`
