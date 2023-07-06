# fixtable
This package cleaned up the latex files from outreg2 in Stata and any other latex tables generated

- installation
```bash
pip install git+https://github.com/leoliu0/fixtable.git
```

- usage
If you have generated a latex table from outreg2, say table.tex, you could run command

```
fixtable table.tex -v var.txt
```
This will print out the "fixed" table to be used directly in your latex project. var.txt is a file containing variable lables you would like to replace in the table.tex. For example, if you want to replace xrd to R\&D expense and ta to Total Asset, you need to have a var.txt like this
```
xrd R\&D expense
ta Total Asset
```
Then this will automatically replace variable name with the name you specified.

Now, you could replace the table.tex with your fixed version:
```
fixtable table.tex -v var.txt -i
```
-i means inplace, this will replace the table.tex with your fix.


