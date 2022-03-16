
# Table of Contents

1.  [Usage](#org643df87)
    1.  [‼ Use this at your own risk ‼](#orgbe5b6ba)
    2.  [Dependencies](#orge2a7935)
    3.  [Running the obfuscator](#org8a51fc6)
    4.  [# no-mangle](#org9a38cdb)
    5.  [Examples](#org723a10b)
        1.  [Before](#orge4801dd)
        2.  [After](#org8379ffe)
2.  [Support](#org734f3f2)



<a id="org643df87"></a>

# Usage


<a id="orgbe5b6ba"></a>

## ‼ Use this at your own risk ‼

This is very early work and this will mess up your game if you don&rsquo;t have a git backup.

Currently not production ready, built more as an example of what we could do for GDScript obfuscation


<a id="orge2a7935"></a>

## Dependencies

This currently uses `pt` ([platinum-searcher](https://github.com/monochromegane/the_platinum_searcher)) for quickly finding all of the references in the project.
In the future we will probably move this to pure python.


<a id="org8a51fc6"></a>

## Running the obfuscator

1.  Put this script in your game directory
2.  Ensure `DRY_RUN` is `True` at the top of the file (only `prints` changes)
3.  `python3 obfuscator.py`


<a id="org9a38cdb"></a>

## # no-mangle

Currently `# no-mangle` keyword is supported only for function names

    func my_function(): # no-mangle
    	pass

Which will keep the name of the function intact


<a id="org723a10b"></a>

## Examples


<a id="orge4801dd"></a>

### Before

![img](https://user-images.githubusercontent.com/100964/158587446-158ce369-cb4a-45ce-b8cd-7329df61e0df.png)


<a id="org8379ffe"></a>

### After

![img](https://user-images.githubusercontent.com/100964/158587624-b473b637-b3b2-4dd9-93dd-d725d48d1491.png)


<a id="org734f3f2"></a>

# Support

Currently this is something that I will work on when I have some free time. If you like this project and want me to work on it more, consider buying me a coffee ☕️

<a href="https://www.buymeacoffee.com/tavurth" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

