# ChangeLog

## v. 0.2.0
 * Add `languages` config parameter
 * Accept overall language definition (a) in config (b) as a plugin argument
 * Cache Presidio AnalyzerEngine to reuse it if another task object is created
 * Ensure that a custom config can delete a PII defined in the standard config
   (by setting its `lang` to `null`)

## v. 0.1.1
 * improved debug output

## v. 0.1.0
 * initial version
