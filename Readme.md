
# Table of Contents

1.  [Usage](#org7eeb279)
    1.  [‼ Use this at your own risk ‼](#org0d1495f)
    2.  [Dependencies](#orge22c551)
    3.  [Running the obfuscator](#org0430524)



<a id="org7eeb279"></a>

# Usage


<a id="org0d1495f"></a>

## ‼ Use this at your own risk ‼

This is very early work and this will mess up your game if you don&rsquo;t have a git backup.

Currently not production ready, built more as an example of what we could do for GDScript obfuscation


<a id="orge22c551"></a>

## Dependencies

This currently uses `pt` ([platinum-searcher](https://github.com/monochromegane/the_platinum_searcher)) for quickly finding all of the references in the project.
In the future we will probably move this to pure python.


<a id="org0430524"></a>

## Running the obfuscator

1.  Put this script in your game directory
2.  Ensure `DRY_RUN` is `True` at the top of the file (only `prints` changes)
3.  `python3 obfuscator.py`

## Examples

**Before**
<img width="832" alt="Screenshot 2022-03-16 at 15 13 17" src="https://user-images.githubusercontent.com/100964/158587446-158ce369-cb4a-45ce-b8cd-7329df61e0df.png">

**After**
<img width="832" alt="Screenshot 2022-03-16 at 15 14 24" src="https://user-images.githubusercontent.com/100964/158587624-b473b637-b3b2-4dd9-93dd-d725d48d1491.png">
