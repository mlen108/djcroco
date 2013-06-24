Changelog for djcroco
=====================

0.2.2
=====

* Fix issue with saving the model's item when file has not changed.
* Return doc name as a string repr of class.
* Add `content_url` property.
* Provide urls to view/download the document. It is a little performance fix
as it means that it does not need to create new session on Crocodoc every time
template gets refreshed/rendered.
* Property `view_file` changed to more appropriate `url`.

0.2.1
=====

* Fix import of South introspection module.

0.2.0
=====

* djcroco is a model field now (and its old API is backward incompatible).

0.1.3
=====

* Fix issue when `url` of thumbnail was not returned properly.
* Allow to use custom width/height of the thumbnail.

0.1.2
=====

* Allow to use env variables for config.
* Bug fixes.

0.1.1
=====

* Fix thumbnails. Wrong thumbnails were displayed when the file changed.

0.1
===

* Initial version.
