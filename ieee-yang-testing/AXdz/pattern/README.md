<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [PATTERN TESTING](#pattern-testing)
- [IMPORTANT FILES](#important-files)
- [TUTORIAL](#tutorial)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

PATTERN TESTING
=====

This repository is for YANG pattern testing

IMPORTANT FILES
=====

   * example-patterns.yang: YANG file with patterns to test
      * tep.in: expect file to run yanglint
      * tep.json: example input
      * tep.xml: generated file from t.json
   * t-sed.sh: error file formatter to make errors easier to read
   * NOTE: example-oddeven.yang  and example-module.yang are obsolete

TUTORIAL
=====

   * See ./example directory
      * em.yang: small example for running example patterns
      * em.in: expect file to run yanglint
      * em.json: example input
      * em-error.json: example error
      * regex-tutorial.docx: Tutorial for regex and the AXdz pattern
